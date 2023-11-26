import socket
from CAN_Control.odrive_controller import odrive_controller
from inverse_kinematics import get_angles, get_trajectory

HOST = "arm.local"  # The server's hostname or IP address
PORT = 1098  # The port used by the server

global arm_object


class Arm:
    def __init__(self, base_nodeid, shoulder_nodeid, elbow_nodeid, restricted_areas):
        self.base_controller = odrive_controller(base_nodeid)
        self.shoulder_controller = odrive_controller(shoulder_nodeid, gear_ratio=125)
        self.elbow_controller = odrive_controller(elbow_nodeid)
        self.restricted_areas = restricted_areas

    def move(self, pos, wait_for_move=True):
        angles = get_angles(pos[0], pos[0], pos[0], self.restricted_areas)
        base_offset, shoulder_offset, elbow_offset = get_trajectory(
            *angles,
            self.base_controller,
            self.shoulder_controller,
            self.elbow_controller,
        )

        self.base_controller.move_to_angle(angles[0], base_offset)
        self.shoulder_controller.move_to_angle(angles[1], shoulder_offset)
        self.elbow_controller.move_to_angle(angles[2], elbow_offset)

        if wait_for_move:
            self.base_controller.wait_for_move()
            self.shoulder_controller.wait_for_move()
            self.elbow_controller.wait_for_move()

    def shutdown(self):
        # move to home position
        self.base_controller.move_to_angle(0)
        self.shoulder_controller.move_to_angle(0)
        self.elbow_controller.move_to_angle(0)

        self.base_controller.wait_for_move()
        self.shoulder_controller.wait_for_move()
        self.elbow_controller.wait_for_move()

        self.base_controller.disable_motor()
        self.shoulder_controller.disable_motor()
        self.elbow_controller.disable_motor()


def setup(base_nodeid, shoulder_nodeid, elbow_nodeid, restricted_areas):
    global arm_object
    arm_object = Arm(base_nodeid, shoulder_nodeid, elbow_nodeid, restricted_areas)


function_map = {
    "setup": setup,
    "move": arm_object.move,
    "shutdown": arm_object.shutdown,
}


def decode_and_call(input_string):
    # Split the input string into individual words
    words = input_string.split()

    # Check if the string contains at least one word
    if len(words) < 1:
        raise ValueError("Invalid input string")

    # Extract the function name and its arguments
    func_name = words[0]
    args = words[1:]

    # Get the corresponding function from the dictionary
    func = function_map.get(func_name)

    if func is None:
        raise ValueError(f"Function '{func_name}' not found")

    # Call the function with the arguments
    result = func(*args)

    return result


# Create a socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Bind the socket to the server address and port
    s.bind((HOST, PORT))

    # Listen for incoming connections
    s.listen()

    print(f"Server listening on {HOST}:{PORT}")

    while True:
        # Accept a connection from a client
        conn, addr = s.accept()

        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                print(f"Received: {data}")
                conn.sendall(data.encode())

                try:
                    result = decode_and_call(data)

                    # Send the result to the client
                    conn.sendall(f"function return {str(result)}".encode())
                except Exception as e:
                    # Send the error message to the client
                    conn.sendall(f"Error: {str(e)}".encode())
                    print(f"Error calling function: {e}")

            print(f"Connection closed by {addr}")
