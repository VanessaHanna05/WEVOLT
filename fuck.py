
import base64
from firebase_admin import credentials, firestore
from firebase_admin import auth
import firebase_admin
import streamlit as st
import json

firebase_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
cred = credentials.Certificate(firebase_dict)
st.write(firebase_dict)