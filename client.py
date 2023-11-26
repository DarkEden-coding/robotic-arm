import socket

HOST = "arm.local"  # The server's hostname or IP address
PORT = 1098  # The port used by the server

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.connect((HOST, PORT))


def send_message(message):
    # Send a message to the server
    server_socket.sendall(message.encode())


# loop until the user enters 'quit'
while True:
    # get input from the user
    user_input = input("Enter a message: ")

    # check if the user wants to quit
    if user_input == "quit":
        break

    # send the message to the server
    send_message(user_input)

server_socket.close()
