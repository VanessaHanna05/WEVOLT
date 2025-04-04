#ip = 10.31.198.177

import socket
import firebase_admin


    

# Raspberry Pi's IP address and the same port number
HOST = '10.31.198.177'  # Replace this with your Raspberry Pi's IP address
PORT = 65432              # This must match the server's port

# Create a socket (IPv4, TCP)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Connect to the Raspberry Pi server
    s.connect((HOST, PORT))
    # Send a simple message
    message = "START"
    s.sendall(message.encode())  # Send the message
    print(f"Sent message: {message}")

first_user = get_first_user()
if first_user:
    print(f"First user's data: {first_user}")

