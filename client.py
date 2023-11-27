import socket
from constants import socket_constants
from inverse_kinematics import Cube

HOST = socket_constants["host"]
PORT = socket_constants["port"]
PASSWORD = socket_constants["password"]

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.connect((HOST, PORT))

restricted_ares = [
    Cube((125, -1000, 0), (-450, 800, -715)),
    Cube((-450, -1000, 500), (-800, 1000, -715)),
    Cube((-450, 800, 0), (230, 1280, 750)),
]


def send_message(message):
    # Send a message to the server
    server_socket.sendall(message.encode())


# loop until the user enters 'quit'
while True:
    # get input from the user
    user_input = input("Enter a message: ") + PASSWORD

    # check if the user wants to quit
    if user_input == "quit":
        break

    # send the message to the server
    send_message(user_input)

    # check to see if the server sent back the request
    data = server_socket.recv(1024).decode()

    if data == user_input:
        print("Server received the message")

    # get the response from the server
    data = server_socket.recv(1024).decode()

    if "Error" in data:
        print(f"{data}")
    else:
        print(f"Server response: {data}")

server_socket.close()
