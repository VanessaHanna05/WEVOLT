
import base64
from firebase_admin import credentials, firestore
from firebase_admin import auth
import firebase_admin
import streamlit as st
import json

cred = credentials.Certificate('secretsWEVOLT.json')
firebase_admin.initialize_app(cred)
db = firestore.client()