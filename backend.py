import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time
import os
import json
import base64
import paho.mqtt.client as mqtt  # MQTT for communication with Raspberry Pi

# Firebase Initialization
firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
if firebase_credentials:
    json_creds = json.loads(base64.b64decode(firebase_credentials).decode("utf-8"))
    cred = credentials.Certificate(json_creds)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
else:
    raise FileNotFoundError("Firebase credentials not found in Streamlit secrets.")

db = firestore.client()

# MQTT Configuration
MQTT_BROKER = "raspberry_pi_ip_address"  # Replace with actual Raspberry Pi IP
START_TRIGGER_TOPIC = "robot/start"
ARRIVED_TOPIC = "robot/arrived"
STOP_TRIGGER_TOPIC = "robot/stop"
GO_BACK_TOPIC = "robot/go_back"
USER_ID_TOPIC = "robot/user_id"

client = mqtt.Client()

def connect_mqtt():
    """Connects to the MQTT broker."""
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_start()

def get_most_urgent_user():
    """Retrieves the most urgent user from Firestore who has a valid duration (>0)."""
    sorted_users_ref = db.collection("sorted_users").stream()
    
    for user in sorted_users_ref:
        user_data = user.to_dict()
        exit_time = parse_time(user_data.get("exit_time", ""))
        duration = float(user_data.get("duration", 0))
        
        if duration > 0 and exit_time > datetime.datetime.now().time():
            return user_data
    return None

def parse_time(time_str):
    """Convert HH:MM time string to a datetime.time object."""
    try:
        return datetime.datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        return None  # Invalid format

def listen_for_start():
    """Listens for the start trigger from the Raspberry Pi."""
    def on_message(client, userdata, message):
        if message.topic == START_TRIGGER_TOPIC and message.payload.decode() == "true":
            process_charging()
    
    client.subscribe(START_TRIGGER_TOPIC)
    client.on_message = on_message

def process_charging():
    """Main process for handling the charging sequence."""
    while True:
        urgent_user = get_most_urgent_user()
        
        if urgent_user is None:
            print("No valid users in the queue. Sending go_back signal.")
            client.publish(GO_BACK_TOPIC, "true")
            break  # No more users, end process
        
        aruco_id = urgent_user["aruco_id"]
        duration = float(urgent_user["duration"])
        exit_time = parse_time(urgent_user["exit_time"])

        print(f"Processing user: {aruco_id} with duration {duration} mins, exit time {exit_time}")

        # Validate user’s exit time and duration
        if exit_time <= datetime.datetime.now().time() or duration <= 0:
            db.collection("users").document(urgent_user["uid"]).update({"duration": -1})
            print(f"User {aruco_id} skipped (invalid exit time or duration).")
            continue

        # Send the user’s aruco_id to the Raspberry Pi
        client.publish(USER_ID_TOPIC, str(aruco_id))
        print(f"Sent aruco_id {aruco_id} to robot.")

        # Wait for "arrived" flag from the robot
        arrived_flag = wait_for_arrived()
        if not arrived_flag:
            print(f"Robot did not arrive for user {aruco_id}. Skipping.")
            continue

        # Start charging timer
        start_time = time.time()
        while True:
            elapsed_time = (time.time() - start_time) / 60  # Convert seconds to minutes
            current_time = datetime.datetime.now().time()

            # Check if charging should stop
            if (exit_time.hour * 60 + exit_time.minute) - 5 <= (current_time.hour * 60 + current_time.minute) or elapsed_time >= duration:
                print(f"Stopping charge for user {aruco_id}.")
                client.publish(STOP_TRIGGER_TOPIC, "true")
                db.collection("users").document(urgent_user["uid"]).update({"duration": -1})
                break
            
            time.sleep(2)  # Check conditions every 2 seconds

        print(f"Charge completed for user {aruco_id}. Checking next user...")

def wait_for_arrived():
    """Waits for the 'arrived' flag from the Raspberry Pi."""
    arrived_flag = False

    def on_message(client, userdata, message):
        nonlocal arrived_flag
        if message.topic == ARRIVED_TOPIC and message.payload.decode() == "true":
            arrived_flag = True

    client.subscribe(ARRIVED_TOPIC)
    client.on_message = on_message

    timeout = time.time() + 60  # Wait for max 60 seconds
    while not arrived_flag:
        if time.time() > timeout:
            return False
        time.sleep(1)

    return True

# Start listening for the start trigger
connect_mqtt()
listen_for_start()
