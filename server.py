import socket
from CAN_Control.odrive_controller import odrive_controller
from inverse_kinematics import get_angles, get_trajectory, get_pos_from_angles
import sys
import traceback
from constants import socket_constants
import pickle

HOST = socket_constants["host"]
PORT = socket_constants["port"]
PASSWORD = socket_constants["password"]

global arm_object, function_map


class Arm:
    def __init__(self, base_nodeid, shoulder_nodeid, elbow_nodeid, restricted_areas):
        self.base_controller = odrive_controller(base_nodeid)
        self.shoulder_controller = odrive_controller(shoulder_nodeid, gear_ratio=125)
        self.elbow_controller = odrive_controller(elbow_nodeid)
        self.restricted_areas = restricted_areas

    def move(self, pos, wait_for_move=True):
        wait_for_move = bool(wait_for_move)

        angles = get_angles(pos[0], pos[1], pos[2], self.restricted_areas)
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

    def enable_motors(self):
        self.base_controller.enable_motor()
        self.shoulder_controller.enable_motor()
        self.elbow_controller.enable_motor()

    def disable_motors(self):
        self.base_controller.disable_motor()
        self.shoulder_controller.disable_motor()
        self.elbow_controller.disable_motor()

    def set_percent_speed(self, percent):
        percent = float(percent)
        self.base_controller.set_percent_traj(percent)
        self.shoulder_controller.set_percent_traj(percent)
        self.elbow_controller.set_percent_traj(percent)

    def emergency_stop(self):
        self.base_controller.emergency_stop()
        self.shoulder_controller.emergency_stop()
        self.elbow_controller.emergency_stop()

    def get_position(self):
        return get_pos_from_angles(
            (
                self.base_controller.get_encoder_pos(),
                self.shoulder_controller.get_encoder_pos(),
                self.elbow_controller.get_encoder_pos(),
            )
        )


def setup(base_nodeid, shoulder_nodeid, elbow_nodeid, restricted_areas):
    global arm_object, function_map
    arm_object = Arm(
        int(base_nodeid), int(shoulder_nodeid), int(elbow_nodeid), restricted_areas
    )

    function_map = {
        "setup": setup,
        "move": arm_object.move,
        "shutdown": arm_object.shutdown,
        "enable_motors": arm_object.enable_motors,
        "disable_motors": arm_object.disable_motors,
        "set_percent_speed": arm_object.set_percent_speed,
        "emergency_stop": arm_object.emergency_stop,
    }


function_map = {
    "setup": setup,
}


def decode_and_call(data):

    function_name = data["function_name"]
    args = data["args"]

    print(f"Calling function: {function_name} with args: {args}")

    # Get the corresponding function from the dictionary
    func = function_map.get(function_name)

    if func is None:
        raise ValueError(f"Function '{function_name}' not found")

    # Call the function with the arguments
    result = func(*args)

    if result:
        print(f"Function {function_name} returned: {result}")

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
                # Receive data
                received_data = b""
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    received_data += chunk

                if not received_data:
                    continue

                # Deserialize the received data
                received_object = pickle.loads(received_data)
                print(f"Received: {received_object}")

                if 'password' not in received_object:
                    print("Missing password")
                    break
                else:
                    if received_object['password'] != PASSWORD:
                        print("Incorrect password")
                        break

                conn.sendall(received_data)

                try:
                    result = decode_and_call(received_object)

                    # Serialize and send the object
                    serialized_data = pickle.dumps(result)
                    conn.sendall(serialized_data)
                except Exception as e:
                    # Send the error message to the client
                    eexc_type, exc_obj, exc_tb = sys.exc_info()
                    traceback_details = traceback.extract_tb(exc_tb)
                    last_traceback = traceback_details[-1]
                    line_number = last_traceback[1]

                    error_file = traceback.format_exc()

                    # Serialize and send the object
                    serialized_data = pickle.dumps(f"Error: {str(e)} on line: {line_number} in file: {error_file}")
                    conn.sendall(serialized_data)

                    print(
                        f"Error calling function: {e} on line: {line_number} in file: {error_file}"
                    )

            print(f"Connection closed by {addr}")
