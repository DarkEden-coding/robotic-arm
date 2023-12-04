import socket
from constants import (
    socket_constants,
    restricted_areas,
    base_nodeid,
    shoulder_nodeid,
    elbow_nodeid,
    return_map,
)
import pickle

HOST = socket_constants["host"]
PORT = socket_constants["port"]
PASSWORD = socket_constants["password"]

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Connecting to server")

server_socket.connect((HOST, PORT))

print("Connection to server established.")


def send_command(command):
    print(f"Sending command: {command['function_name']}")
    command["password"] = PASSWORD
    return_from_function = return_map[command["function_name"]]

    # send the message to the server
    # Serialize and send the object
    serialized_data = pickle.dumps(command)
    server_socket.sendall(serialized_data)

    if socket_constants["function_check"]:
        print("Waiting for server to receive the message")

        # Receive data
        received_data = b""
        while True:
            chunk = server_socket.recv(4096)
            if not chunk:
                break
            received_data += chunk
            # if data is a complete object, break
            try:
                pickle.loads(received_data)
                break
            except Exception as e:
                print(e)
                continue

        if received_data == serialized_data:
            print("Server received the message")
        else:
            print("Server did not receive the message")
            print(f"Sent: {command}")
            print(f"Received: {pickle.loads(received_data)}")

            # raise ConnectionError("Server did not receive the message")

    if return_from_function:
        # Receive data
        received_data = b""
        while True:
            chunk = server_socket.recv(4096)
            if not chunk:
                break
            received_data += chunk
            # if data is a complete object, break
            try:
                pickle.loads(received_data)
                break
            except Exception as e:
                print(e)
                continue

        # Deserialize the received data
        received_object = pickle.loads(received_data)

        if received_object:
            if "Error" in received_object:
                print(f"{received_object}")
            else:
                print(f"Server response: {received_object}")
                return received_object


def setup():
    send_command(
        {
            "function_name": "setup",
            "args": [base_nodeid, shoulder_nodeid, elbow_nodeid, restricted_areas],
            "password": PASSWORD,
        }
    )


def enable_motors():
    send_command({"function_name": "enable_motors", "args": [], "password": PASSWORD})


def disable_motors():
    send_command({"function_name": "disable_motors", "args": [], "password": PASSWORD})


def shutdown():
    send_command({"function_name": "shutdown", "args": [], "password": PASSWORD})


def set_percent_speed(percent_speed):
    send_command(
        {
            "function_name": "set_percent_speed",
            "args": [percent_speed],
            "password": PASSWORD,
        }
    )


def move(pos, wait_for_finish=True):
    send_command(
        {"function_name": "move", "args": [pos, wait_for_finish], "password": PASSWORD}
    )


def emergency_stop():
    send_command({"function_name": "emergency_stop", "args": [], "password": PASSWORD})


def close_connection():
    server_socket.close()


def get_position():
    return send_command(
        {"function_name": "get_position", "args": [], "password": PASSWORD}
    )
