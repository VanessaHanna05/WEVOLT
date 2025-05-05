import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import os
import json
import base64
import streamlit as st

def app():
    # Initialize Firebase Admin SDK (if not already initialized)
    #firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
    firebase_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])

    if firebase_dict:
        cred = credentials.Certificate(firebase_dict)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
    else:
        raise FileNotFoundError("Firebase credentials not found in Streamlit secrets.")

    db = firestore.client()

def parse_time(time_str):
    """Convert HH:MM time string to a datetime.time object for sorting."""
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        return None  # Handle invalid format

def sort_users():
    # Initialize Firestore
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    db = firestore.client()

    users_ref = db.collection("users")
    users = users_ref.stream()
    
    user_list = []
    now = datetime.now()

    for user in users:
        user_data = user.to_dict()
        exit_time_str = user_data.get("leave_time", "")
        exit_time = parse_time(exit_time_str)
        duration = float(user_data.get("duration", 0))
        aruco_id = int(user_data.get("aruco_id"))
        spot_nb = int(user_data.get("spot_nb"))

        if not exit_time:
            continue  # Skip users with invalid exit time

        parsed_exit = datetime.combine(now.date(), exit_time)
        projected_end = now + timedelta(hours=duration)

        # If exit is earlier than now, assume it's next day
        if parsed_exit < now:
            parsed_exit += timedelta(days=1)

        # If user's duration will overlap with or exceed their exit time
        if parsed_exit <= now or parsed_exit <= projected_end:
            duration = -1
            db.collection("users").document(user.id).update({"duration": -1})

        # Add user to the list (expired or not)
        user_list.append({
            "uid": user.id,
            "username": user_data.get("username", ""),
            "email": user_data.get("email",""),
            "exit_time": exit_time_str,
            "duration": duration,
            "aruco_id": aruco_id,
            "spot_nb": spot_nb
        })

    # Sort by exit time first, then by descending duration
    sorted_users = sorted(user_list, key=lambda u: (parse_time(u["exit_time"]), -u["duration"]))

    sorted_ref = db.collection("sorted_users")

    # Clear old sorted list
    for doc in sorted_ref.stream():
        doc.reference.delete()

    # Store new sorted users
    for idx, user in enumerate(sorted_users):
        sorted_ref.document(f"user_{idx}").set(user)

    # Clean up users with duration <= 0 from sorted_users
    for user in sorted_ref.stream():
        data = user.to_dict()
        duration = float(data.get("duration", 0))

        if duration <= 0:
            sorted_ref.document(user.id).delete()
            print(f"🗑️ Deleted expired user from sorted_users: {user.id}")

    print("✅ User list sorted and updated in Firestore.")

# Run when script is executed
if __name__ == "__main__":
    sort_users()
