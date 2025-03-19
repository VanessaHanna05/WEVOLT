import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os
import json
import base64

def app():
    # Initialize Firebase Admin SDK (if not already initialized)
    firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
    if firebase_credentials:
        json_creds = json.loads(base64.b64decode(firebase_credentials).decode("utf-8"))
        cred = credentials.Certificate(json_creds)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
    else:
        raise FileNotFoundError("Firebase credentials not found in Streamlit secrets.")

    db = firestore.client()

def parse_time(time_str):
    """Convert HH:MM time string to a datetime.time object for sorting."""
    try:
        return datetime.datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        return None  # Handle invalid format

def sort_users():
    """Retrieve users, sort them based on exit time and charging duration, and update Firestore."""
    db = firestore.client()
    users_ref = db.collection("users")
    users = users_ref.stream()
    
    user_list = []
    current_time = datetime.datetime.now().time()

    for user in users:
        user_data = user.to_dict()
        exit_time = parse_time(user_data.get("leave_time", ""))
        duration = float(user_data.get("duration", 0))

        if exit_time:
            # If the exit time has passed, set duration to -1
            if exit_time <= current_time:
                duration = -1
                db.collection("users").document(user.id).update({"duration": -1})

            user_list.append({
                "uid": user.id,
                "username": user_data.get("username", ""),
                "exit_time": user_data.get("leave_time", ""),  # Keep as string for Firestore
                "duration": duration
            })

    # Sort users: first by exit time (earlier first), then by duration (longer first)
    sorted_users = sorted(user_list, key=lambda u: (parse_time(u["exit_time"]), -u["duration"]))

    # Store sorted list in Firestore collection (correct method)
    sorted_ref = db.collection("sorted_users")
    
    # Delete previous sorted list to avoid duplicate data
    for doc in sorted_ref.stream():
        doc.reference.delete()
    
    # Add each user as a document inside the `sorted_users` collection
    for idx, user in enumerate(sorted_users):
        sorted_ref.document(f"user_{idx}").set(user)

    print("✅ User list sorted and updated in Firestore.")

# Run sorting when script is called
if __name__ == "__main__":
    sort_users()
