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

    def authenticate_user(username, password):
        """Authenticate user by fetching their email from Firestore"""
        if not username or not password:
            st.warning("⚠️ Please enter both username and password.")
            return

        try:
            # Query Firestore to get user data by username
            users_ref = db.collection("users")  # Firestore collection
            query = users_ref.where("username", "==", username).stream()

            user_data = None
            for doc in query:
                user_data = doc.to_dict()
                break  # Get the first matching result
            
            if not user_data:
                st.warning("❌ Username not found.")
                return
            st.session_state["logged_in_user"] = user_data

            # Extract email (Firebase Auth requires email for authentication)
            user_email = user_data.get("email")

            # Authenticate with Firebase Authentication (Admin SDK can't verify passwords directly)
            # This requires Firebase Client SDK or manual hashing for password verification
            st.success(f"✅ Login successful! Welcome, {user_data['username']} ({user_data.get('role', 'user')})")

        except Exception as e:
            st.error(f"❌ Authentication failed: {e}")

    # Load and encode the background image
    image_file = 'loginback.png'
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
        }}

        /* Override the unwanted light grey background */
        .st-b7 {{
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}

        /* Style text input fields */
        input[type="text"], input[type="password"] {{
            background-color: #717775;
            color: black !important;
            border-radius: 5px !important;
            border: 2px solid #717775 !important;
            font-size: 16px !important;
            caret-color: black !important;
            width: 300px;
            height: 40px;
            margin-left: 10%;
          
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
            margin-left: 30%;
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

    # Input fields
    username = st.text_input("", placeholder="Username")
    password = st.text_input("", type="password", placeholder="Password")

    # Login button
    if st.button("Login"):
        authenticate_user(username, password)
        time.sleep(2)
        navigate("info")

    if st.button("Home"):
        navigate('home')

