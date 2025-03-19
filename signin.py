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

def sign_up_user(username, email, password, role="user"):
    """Creates a user in Firebase Authentication and Firestore with an incrementing Aruco ID."""
    try:
        existing_users = db.collection("users").where("username", "==", username).stream()
        if any(existing_users):
            return {"success": False, "error": "Username already exists. Please choose another."}

        user = auth.create_user(
            email=email,
            password=password,
            display_name=username
        )

        aruco_id = get_next_aruco_id()

        db.collection("users").document(user.uid).set({
            "username": username,
            "email": email,
            "role": role,
            "uid": user.uid,
            "aruco_id": aruco_id
        })

        return {"success": True, "user": user}
    except auth.EmailAlreadyExistsError:
        time.sleep(4)
        return {"success": False, "error": "This email is already in use. Try logging in."}
    except Exception as e:
        return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}

def app(navigate):
    st.write("Sign-Up Page")
    
    email = st.text_input("", placeholder="Enter your email")
    password = st.text_input("", placeholder="Enter your password")
    username = st.text_input("", placeholder="Enter your unique username")
    
    # Load and encode the background image (Same as login page)
    image_file = 'signup.png'  
    with open(image_file, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()

    # Apply custom styling to match login page
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
            padding-top: 20%;
        }}
        input[type="text"], input[type="password"] {{
            background-color: #717775;
            color: black !important;
            border-radius: 5px !important;
            border: 2px solid #717775 !important;
            font-size: 16px !important;
            caret-color: black !important;
            width: 300px;
            height: 40px;
            margin-left: 6%;
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
            margin-left: 6%;
            width: 200px;
            height: 40px;
        }}
        div.stButton > button:hover {{
            background-color: #4caf5087 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    if st.button("Create Account"):
        if not username or not password or not email:
            st.warning("⚠️ Please enter all required information.")
        else:
            result = sign_up_user(username, email, password)
            if result["success"]:
                st.success("🎉 Account created successfully!")
                st.markdown("✅ Redirecting to login page....")
                time.sleep(2)
                navigate("login")
            else:
                st.error(f"❌ Sign-up failed: {result['error']}")
    
    if st.button("Home"):
        navigate('home')
