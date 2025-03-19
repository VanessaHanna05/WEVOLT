import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import base64
import time
import datetime
import json
import os

# Initialize Firebase Admin SDK (Only initialize once)
firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
if firebase_credentials:
    json_creds = json.loads(base64.b64decode(firebase_credentials).decode("utf-8"))
    cred = credentials.Certificate(json_creds)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
else:
    raise FileNotFoundError("Firebase credentials not found in Streamlit secrets.")

db = firestore.client()

def get_next_aruco_id():
    """Fetches the last used Aruco ID and increments it."""
    doc_ref = db.collection("metadata").document("aruco_counter")
    doc = doc_ref.get()
    if doc.exists:
        last_id = doc.to_dict().get("last_id", 0)
    else:
        last_id = 0
    new_id = last_id + 1
    doc_ref.set({"last_id": new_id})
    return new_id

def app(navigate):
    user = st.session_state.get('logged_in_user')
    if not user:
        st.warning("⚠️ No user logged in. Please log in first.")
        return

    def update_user_info(new_attributes):
        doc_id = user["uid"]  # Get Firestore document ID
        try:
            db.collection("users").document(doc_id).update(new_attributes)
            st.session_state["logged_in_user"].update(new_attributes)
            st.success("✅ User information updated successfully!")
        except Exception as e:
            st.error(f"❌ Failed to update user info: {e}")

    # Assign Aruco ID if not set
    if "aruco_id" not in user:
        new_aruco_id = get_next_aruco_id()
        update_user_info({"aruco_id": new_aruco_id})

    # Load and encode the background image
    image_file = 'infoback.png'
    with open(image_file, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()

    # Apply custom styling with the embedded background image
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/png;base64,{encoded}") no-repeat center center fixed;
            background-size: cover;
        }}
        
        div[data-testid="stVerticalBlock"] {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding-top:50%;
            padding-left:6%;
        }}
        
        .st-b7 {{
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}
        
        input[type="text"] {{
            background-color: #717775;
            color: black !important;
            border-radius: 5px !important;
            border: 2px solid #717775 !important;
            font-size: 12px !important;
            caret-color: black !important;
            width: 300px;
            height: 30px;
            margin-left: 0%;
        }}
        
        input::placeholder, textarea::placeholder {{
            color: lightgrey !important;
            font-style: italic !important;
            opacity: 1 !important;
        }}
        
        div.stButton > button {{
            background-color: #4CAF50 !important;
            color: white !important;
            border-radius: 30px !important;
            border: none !important;
            padding: 20px 20px !important;
            margin-top: 5%;
            width: 150px;
            height:40px;
        }}
        
        div.stButton > button:hover {{
            background-color: #4caf5087 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # Input fields
    leave_time_str = st.text_input("Exit Time", placeholder="HH:MM (24-hour format)")
    charging_duration_str = st.text_input("Charging Duration", placeholder="Charging duration (in hours)")
    spot_nb = st.text_input("Spot no.", placeholder="Check Which Spot you are parked on")
    
    # Submit button
    if st.button("Submit"):
        if not leave_time_str or not charging_duration_str or not spot_nb:
            st.warning("⚠️ Please fill in all the fields.")
            return
        
        try:
            leave_time = datetime.datetime.strptime(leave_time_str, "%H:%M").time()
            current_time = datetime.datetime.now().time()
            
            charging_duration = float(charging_duration_str)
            
            if leave_time <= current_time:
                st.warning("⚠️ Exit time must be later than the current time.")
                return
            
            if not (0 < charging_duration <= 5):
                st.warning("⚠️ Charging duration must be greater than 0 and less than or equal to 5 hours.")
                return
            
            update_user_info({
                "leave_time": leave_time_str,
                "duration": charging_duration_str,
                "spot_nb": spot_nb
            })
        
        except ValueError:
            st.warning("⚠️ Please enter valid time format (HH:MM) and numeric charging duration.")
