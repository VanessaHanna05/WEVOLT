import streamlit as st
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json
import os
import time

# Initialize Firebase Admin SDK
firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")

if firebase_credentials:
    json_creds = json.loads(base64.b64decode(firebase_credentials).decode("utf-8"))
    cred = credentials.Certificate(json_creds)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
else:
    raise FileNotFoundError("Firebase credentials not found in Streamlit secrets.")

def app(navigate):
    db = firestore.client()
    image_file = 'contactback.png'  # Background Image
    with open(image_file, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()
    
    # Apply custom styling
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
            padding-top: 10%;
        }}
        input[type="text"], textarea {{
            background-color: #717775;
            color: black !important;
            border-radius: 5px !important;
            border: 2px solid #717775 !important;
            font-size: 16px !important;
            width: 300px;
            height: 40px;
            margin: 5px;
        }}
        div.stButton > button {{
            background-color: #4CAF50 !important;
            color: white !important;
            border-radius: 30px !important;
            padding: 15px 20px !important;
            width: 150px;
            margin-top: 10px;
        }}
        div.stButton > button:hover {{
            background-color: #4caf5087 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
   
    col1, col2 = st.columns(2)

    with col1:
        email = st.text_input("Email", placeholder="Enter your email")

    with col2:
        name = st.text_input("Name", placeholder="Enter your name")

    message = st.text_area("Message", placeholder="Write your message here")
    
    if st.button("Submit"):
        if email and name and message:
            user_ref = db.collection("users").where("email", "==", email).stream()
            user_exists = any(user_ref)
            
            if user_exists:
                contact_data = {"email": email, "name": name, "message": message}
                db.collection("contact_messages").add(contact_data)
                st.success("Message sent successfully!")
            else:
                st.warning("You are not a registered user. Redirecting to Sign Up...")
                time.sleep(2)
                navigate("signin")
                
        else:
            st.warning("Please fill all fields before submitting.")
    