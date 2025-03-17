import streamlit as st
import home
import signin
import login
import contact
import info
import firebase_admin
import os
import json
import base64
from firebase_admin import credentials, firestore
from firebase_admin import auth


cred = credentials.Certificate('wevolt-4d8a8-2e9079117595.json')
#firebase_admin.initialize_app(cred)



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
