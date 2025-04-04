import firebase_admin
import socket
from firebase_admin import credentials, firestore
import time
import json

# Initialize Firebase Admin SDK
cred = credentials.Certificate('wevolt-4d8a8-2e9079117595.json')  # Path to your credentials file
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

def get_first_user():
    # Query the 'users' collection and order by document ID (or another field like a timestamp)
    users_ref = db.collection('users')
    users = users_ref.limit(1).get()  # Get only the first user

    if users:
        # Fetch the first user document
        user = users[0]  # Since we limited to 1, it's safe to access the first document

        # Get the document data (attributes of the first user)
        user_data = user.to_dict()
        
        print(f"User Data: {user_data}")
        return user_data
    else:
        print("No users found in the database.")
        return None
    

first_user = get_first_user()
user_id = first_user["aruco_id"]
spot_nb = first_user["spot_nb"]
duration = first_user["duration"]
message2 = f"UserID:{user_id},SpotNbr:{spot_nb},Duration:{duration}, START"



if first_user:
    print(f"First user's data: {first_user}")

# Raspberry Pi's IP address and the same port number
HOST = '10.31.198.177'  # Replace this with your Raspberry Pi's IP address
PORT = 65432              # This must match the server's port

# Create a socket (IPv4, TCP)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Connect to the Raspberry Pi server
    s.connect((HOST, PORT))
    s.sendall(message2.encode())

   

first_user = get_first_user()
if first_user:
    print(f"First user's data: {first_user}")

