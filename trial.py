import firebase_admin
import socket
from firebase_admin import credentials, firestore
import time
import json
import sort_users

# Initialize Firebase Admin SDK
cred = credentials.Certificate('wevolt-4d8a8-2e9079117595.json')  # Path to your credentials file
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

def remove_user(user_id):
    # Query the 'sorted_users' collection to find the document with the specific user_id
    users_ref = db.collection('sorted_users')
    query = users_ref.where('aruco_id', '==', user_id)  # Assuming 'aruco_id' is the key you're searching by
    users = query.get()

    # Check if the user exists
    if users:
        for user in users:
            # Document exists, now delete it
            users_ref.document(user.id).delete()
            print(f"User with aruco_id {user_id} has been removed from the database.")

    else:
        print(f"No user found with aruco_id {user_id}.")
         
def update_user_duration(user_id):
    # Query the 'users' collection to find the document with the specific user_id
    users_ref = db.collection('users')
    query = users_ref.where('aruco_id', '==', user_id)  # Assuming 'aruco_id' is the key you're searching by
    users = query.get()

    # Check if the user exists and update the duration
    if users:
        for user in users:
            # Document exists, now update the 'duration' field to -1
            users_ref.document(user.id).update({'duration': -1})
            print(f"User with aruco_id {user_id}'s duration has been set to -1.")
    else:
        print(f"No user found with aruco_id {user_id} in users collection.")


def get_first_user():
    # Query the 'users' collection and order by document ID (or another field like a timestamp)
    users_ref = db.collection('sorted_users')
    users = users_ref.limit(1).get()  # Get only the first user

    if users:
        
        # Fetch the first user document
        user = users[0]  # Since we limited to 1, it's safe to access the first document
        print(users[0].to_dict())
        # Get the document data (attributes of the first user)
        user_data = user.to_dict()
        return user_data
    else:
        print("No users found in the database.")
        return None
    

def is_collection_empty(collection_name):
    # Get a reference to the collection
    collection_ref = db.collection(collection_name)
    
    # Try to get the first document in the collection
    docs = collection_ref.limit(1).get()
    
    # Check if there are any documents in the collection
    if len(docs) == 0:
        print(f"The collection '{collection_name}' is empty.")
        return True  # Collection is empty
    else:
        print(f"The collection '{collection_name}' is not empty.")
        return False  # Collection is not empty


# Raspberry Pi's IP address and the same port number
HOST = '10.31.198.177'  # Replace this with your Raspberry Pi's IP address
PORT = 65432              # This must match the server's port

while True:
    try:
            with socket.create_connection((HOST, PORT), timeout=1) as sock:
                sort_users.sort_users()
                

                first_user = get_first_user()

                if first_user is None:
                    # If no user exists, send the "END" message and continue
                    message3 = f"UserID:0,SpotNbr:0,Duration:0,END"
                    sock.sendall(message3.encode())
                    print("No users found, sending END message.")
                    # Skip the rest of the loop and start again
                else:
                    user_id = first_user["aruco_id"]
                    spot_nb = first_user["spot_nb"]
                    response = sock.recv(1024).decode()
                    print(f"📥 Response from Pi: {response}")
                    if response == "Charging STARTCOMPLETE":
                        #remove user
                        print("user removed")
                        remove_user(user_id)
                        update_user_duration(user_id)

                    if is_collection_empty("sorted_users"):
                        message3 = f"UserID:0,SpotNbr:0,Duration:0,END"
                        sock.sendall(message3.encode())
                    else:    
                        duration = int(int(first_user["duration"])*3600)
                        message2 = f"UserID:{user_id},SpotNbr:{spot_nb},Duration:{duration}, START"
                        sock.sendall(message2.encode())
                            
                    if first_user:
                        print(f"First user's data: {first_user}")


    except Exception as e:
                print(f"❌ Failed to connect/send: {e}")




