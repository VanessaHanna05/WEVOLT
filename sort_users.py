import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import json
import streamlit as st
import os



firebase_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
cred = credentials.Certificate(firebase_dict)


def parse_time(time_str):
    """Convert HH:MM time string to a datetime.time object for sorting."""
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        return None

def sort_users():
    # Initialize Firebase only if not already initialized
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    db = firestore.client()

    users_ref = db.collection("users")
    users = users_ref.stream()

    user_list = []
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")

    for user in users:
        user_data = user.to_dict()

        exit_time_str = user_data.get("leave_time", "")
        exit_time = parse_time(exit_time_str)
        duration = float(user_data.get("duration", 0))
        aruco_id = int(user_data.get("aruco_id", 0))
        spot_nb = int(user_data.get("spot_nb", 0))
        user_date = user_data.get("date", "")

        if not exit_time:
            print(f"⏭️ Skipping user {user.id}: invalid exit_time format")
            continue

        # Only allow today's users
        if user_date != today_str:
            print(f"📆 Skipping user {user.id}: date {user_date} != today")
            continue

        parsed_exit = datetime.combine(now.date(), exit_time)
        start_time = parsed_exit - timedelta(hours=duration)

        if start_time <= now:
            print(f"⛔ Skipping user {user.id}: charging window already started/expired")
            db.collection("users").document(user.id).update({"duration": -1})
            continue

        # User is valid, add to list
        user_list.append({
            "uid": user.id,
            "username": user_data.get("username", ""),
            "email": user_data.get("email", ""),
            "exit_time": exit_time_str,
            "duration": duration,
            "aruco_id": aruco_id,
            "spot_nb": spot_nb,
            "date": user_date
        })

    # Sort valid users
    sorted_users = sorted(user_list, key=lambda u: (parse_time(u["exit_time"]), -u["duration"]))
    sorted_ref = db.collection("sorted_users")

    # Clear old sorted list
    for doc in sorted_ref.stream():
        doc.reference.delete()

    # Add sorted users
    for idx, user in enumerate(sorted_users):
        sorted_ref.document(f"user_{idx}").set(user)

    print("✅ Sorted users list updated.")

# Run when script is executed directly
if __name__ == "__main__":
    sort_users()
