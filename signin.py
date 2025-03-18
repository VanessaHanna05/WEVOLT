import streamlit as st
import warnings
import firebase_admin
import time
import base64
from firebase_admin import credentials, auth, firestore
import os
import json

def app(navigate):
    st.write("Sign-Up Page")
    
    email = st.text_input("", placeholder="Enter your email")
    password = st.text_input("", placeholder="Enter your password")
    username = st.text_input("", placeholder="Enter your unique username")

    firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")

    if firebase_credentials:
            json_creds = json.loads(base64.b64decode(firebase_credentials).decode("utf-8"))
            cred = credentials.Certificate(json_creds)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
    else:
        raise FileNotFoundError("Firebase credentials not found in Streamlit secrets.")

    
    db = firestore.client()

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

        .st-emotion-cache-1cvow4s {{
            font-family: "Source Sans Pro", sans-serif;
            font-size: 20px;
            color: inherit;
            
}}

        /* Override the unwanted light grey background */
        .st-b7 {{
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}

        /* Style text input fields to match login page */
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
        
            margin-left: 6%;
            width: 200px;
            height: 20px;
        }}

        /* Button hover effect */
        div.stButton > button:hover {{
            background-color: #4caf5087 !important;
        }}
   
        </style>
        """,
        unsafe_allow_html=True
    )

    def sign_up_user(username, email, password, role="user"):
        """Creates a user in Firebase Authentication and Firestore"""
        try:
            # Check if username already exists in Firestore
            existing_users = db.collection("users").where("username", "==", username).stream()
            if any(existing_users):
                return {"success": False, "error": "Username already exists. Please choose another."}

            # Create user in Firebase Authentication
            user = auth.create_user(
                email=email,
                password=password,
                display_name=username
            )

            # Save user details in Firestore under 'users' collection
            db.collection("users").document(user.uid).set({
                "username": username,
                "email": email,
                "role": role,
                "uid": user.uid
            })

            return {"success": True, "user": user}

        except auth.EmailAlreadyExistsError:
            time.sleep(4)  # Wait for 2 seconds before navigating
            navigate("login")
            return {"success": False, "error": "This email is already in use. Try logging in."}
            
        #except auth.InvalidEmailError:
           # return {"success": False, "error": "Invalid email format. Please enter a valid email address."}
        
        #except auth.WeakPasswordError:
           # return {"success": False, "error": "Weak password. Use at least 6 characters."}

        #except Exception as e:
           # return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}

    # Handle Sign-Up Button Click
    if st.button("Create Account"):
        if not username or not password or not email:
            st.warning("⚠️ Please enter all required information.")
        else:
            result = sign_up_user(username, email, password)
            print("trying to signup")

            if result["success"]:
                st.success("🎉 Account created successfully!")
                st.markdown("✅ Redirecting to login page....")
                time.sleep(2)  # Wait for 2 seconds before navigating
                navigate("login")
            else:
                st.error(f"❌ Sign-up failed: {result['error']}")
    
    if st.button("Home"):
        navigate('home')

