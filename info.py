import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import base64
import time
import datetime
import json
import os
import sort_users
import subprocess

# Initialize Firebase Admin SDK (Only initialize once)
#firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
#if firebase_credentials:
#    json_creds = json.loads(base64.b64decode(firebase_credentials).decode("utf-8"))
#    cred = credentials.Certificate(json_creds)
#    if not firebase_admin._apps:
#        firebase_admin.initialize_app(cred)
#else:
#    raise FileNotFoundError("Firebase credentials not found in Streamlit secrets.")

cred = credentials.Certificate('wevolt-4d8a8-2e9079117595.json')

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
    
db = firestore.client()

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

        /* Override the unwanted light grey background */
        .st-b7 {{
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}

        /* Style text input fields */
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

        .st-emotion-cache-1weic72 {{
            font-size: 0.875rem;
            color: rgb(250, 250, 250);
            display: flex;
            visibility: hidden;
            margin-bottom: 0.25rem;
            height: auto;
            min-height: 1.5rem;
            vertical-align: middle;
            flex-direction: row;
            -webkit-box-align: center;
            align-items: center;
            margin-bottom: -20px;
        }}

        /* Placeholder text color */
        input::placeholder, textarea::placeholder {{
            color: lightgrey !important;
            font-style: italic !important;
            opacity: 1 !important;
        }}

        /* Hover effect for inputs */
        input[type="text"]:hover, textarea:hover, input[type="password"]:hover {{
            background-color: #d3d3d3 !important;
        }}

        /* Button styles */
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

        /* Button hover effect */
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
            # Validate leave time format
            leave_time = datetime.datetime.strptime(leave_time_str, "%H:%M").time()
            current_time = datetime.datetime.now().time()
            
            # Validate charging duration
            charging_duration = float(charging_duration_str)
            
            if leave_time <= current_time:
                st.warning("⚠️ Exit time must be later than the current time.")
                return
            
            if not (0 < charging_duration <= 5):
                st.warning("⚠️ Charging duration must be greater than 0 and less than or equal to 5 hours.")
                return
            
            # If validations pass, update user info
            
            update_user_info({
                "leave_time": leave_time_str,
                "duration": charging_duration_str,
                "spot_nb": spot_nb
            })

            

            # Call external Python script to send information to the Raspberry Pi
            
            # Check the result of the script execution
            
            #if result.returncode == 0:
             #   st.success("✅ Information sent to Raspberry Pi successfully!")
            #else:
              #  st.error(f"❌ Failed to send information to Raspberry Pi: {result.stderr}")
        
            sort_users.sort_users()
            result = subprocess.run(['.venv/Scripts/python', 'trial.py'], capture_output=True, text=True, env=os.environ)
        except ValueError:
            st.warning("⚠️ Please enter valid time format (HH:MM) and numeric charging duration.")
