import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import base64
import time
import home, main


# Initialize Firebase Admin SDK (Only initialize once)
if not firebase_admin._apps:
    cred = credentials.Certificate("wevolt-4d8a8-2e9079117595.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def app(navigate):

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
            padding-top:70%;
            padding-left:25%;
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
            font-size: 16px !important;
            caret-color: black !important;
            width: 300px;
            height: 40px;
            margin-left: 0%;
          
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
            margin-left: 20%;
            width: 150px;
            
            
        }}

        /* Button hover effect */
        div.stButton > button:hover {{
            background-color: #4caf5087 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    user = st.session_state['logged_in_user']

    def update_user_info(new_attributes):

        if "logged_in_user" not in st.session_state:
            st.warning("⚠️ No user logged in. Please log in first.")
            return

        user = st.session_state["logged_in_user"]
        doc_id = user["uid"]  # Get Firestore document ID

        try:
            # Update the user document in Firestore
            db.collection("users").document(doc_id).update(new_attributes)

            # Update session state with new attributes
            st.session_state["logged_in_user"].update(new_attributes)

            st.success("✅ User information updated successfully!")
        
        except Exception as e:
            st.error(f"❌ Failed to update user info: {e}")



    # Input fields
    leave_time = st.text_input("Exit Time", placeholder="leave time hh:mm")
    charging_duration = st.text_input("Charging Duration", placeholder="Charging duration (in hours)")
    spot_nb = st.text_input("Spot no.", placeholder="Check Which Spot are u parked on")

    # Login button
    if st.button("submit"):
        if not leave_time or not charging_duration or not spot_nb:
            st.warning("⚠️ Please enter both inputs.")
            return
        else:
            update_user_info({
                "leave_time":leave_time,
                "duration":charging_duration,
                "spot_nb": spot_nb
            })




    