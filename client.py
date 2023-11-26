import socket

HOST = "arm.local"  # The server's hostname or IP address
PORT = 1098  # The port used by the server

# Create a socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Connect to the server
    s.connect((HOST, PORT))

    # Send a message to the server
    message = "Hello, server!"
    s.sendall(message.encode())

print("Message sent to server.")
