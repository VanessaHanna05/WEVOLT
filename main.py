
import base64
from firebase_admin import credentials, firestore
from firebase_admin import auth
import firebase_admin
import streamlit as st
import json

firebase_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
cred = credentials.Certificate(firebase_dict)
# Initialize Firebase Admin SDK
firebase_admin.initialize_app(cred)


import home
import signin
import login
import contact
import info

import os



#cred = credentials.Certificate('wevolt-4d8a8-2e9079117595.json')
#firebase_admin.initialize_app(cred)

#firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")

# Use the direct path to the credentials file
#cred = credentials.Certificate('wevolt-4d8a8-2e9079117595.json')




#if firebase_credentials:
#    json_creds = json.loads(base64.b64decode(firebase_credentials).decode("utf-8"))
#    cred = credentials.Certificate(json_creds)
#    if not firebase_admin._apps:
#        firebase_admin.initialize_app(cred)
#else:
#    raise FileNotFoundError("Firebase credentials not found in Streamlit secrets.")

db = firestore.client()
# Initialize session state for current_page if it doesn't exist.
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'home'

def navigate(page):
    st.session_state['current_page'] = page
    st.rerun()  # Force a rerun after navigation.

current_page = st.session_state['current_page']

if current_page == 'home':
    home.app(navigate)
elif current_page == 'signin':
    signin.app(navigate)
elif current_page == 'login':
    login.app(navigate)
elif current_page == 'contact':
    contact.app(navigate)
elif current_page == 'info':
    info.app(navigate)
