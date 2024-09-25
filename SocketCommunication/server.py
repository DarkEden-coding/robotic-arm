import json
import os
import pickle
import socket
import threading
import traceback
from datetime import datetime


def start_thread(target):
    thread = threading.Thread(target=target)
    thread.start()
    return thread


class Server:
    def __init__(self, host="127.0.0.1", port=65432, name="Server"):
        """
        Server class that can accept client connections through 3 sockets
        :param host: The host to target (server ip address)
        :param port: The starting port to host on (each socket uses ports added onto this ie: x, x+1, x+2)
        :param name: The name that the server will display to clients
        """
        self.host = host
        self.port = port
        self.name = name
        self.password = None
        self.client_public_key = None
        self.data = {"server_logs": ""}
        self.file_path = os.path.dirname(os.path.realpath(__file__))
        self.log_thread_lock = threading.Lock()

        self._load_settings()

        self.command_socket = self._setup_socket(self.port)
        self.data_socket = self._setup_socket(self.port + 1)
        self.get_data_socket = self._setup_socket(self.port + 2)

        self.command_handler = None

        start_thread(self._listen_for_commands)
        start_thread(self._listen_for_data)
        start_thread(self._listen_for_get_request)

        self._print_log("Server started successfully.")

    def _print_log(self, message):
        with self.log_thread_lock:
            # print message with timestamp and add message to server logs
            time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{time_stamp} - {message}")
            self.data["server_logs"] += f"{time_stamp} - {message}\n"

    def _load_settings(self):
        if os.path.exists(f"{self.file_path}/network-settings.json"):
            with open(f"{self.file_path}/network-settings.json", "r") as f:
                settings = json.load(f)
            self.host = settings.get("host", self.host)
            self.port = settings.get("port", self.port)
            self.password = settings.get("password", self.password)
        self._print_log(f"Server settings: {self.host}:{self.port}")

    def _setup_socket(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, port))
        sock.settimeout(5)
        sock.listen()
        self._print_log(f"Socket set up on {self.host}:{port}")
        return sock

    def register_command_handler(self, handler):
        """
        Use this command to register a command handler, you need to call this with a function arg at least once to use the command interface
        :param handler: the function to be called apon command request
        """
        self.command_handler = handler
        self._print_log("Command handler registered.")

    def _listen_for_commands(self):
        self._listen(self.command_socket, self._process_command)

    def _listen_for_data(self):
        self._listen(self.data_socket, self._process_data)

    def _listen_for_get_request(self):
        self._listen(self.get_data_socket, self._process_get_request)

    def _listen(self, sock, process_func):
        while True:
            try:
                conn, addr = sock.accept()
                with conn:
                    self._authenticate_client(conn, addr)
                    self._handle_client_connection(conn, addr, process_func)
            except socket.timeout:
                continue
            except Exception as _:
                self._print_log(f"Error in listen function: {traceback.format_exc()}")

    def _authenticate_client(self, conn, addr):
        while True:
            self._print_log(f"Connected by {addr}, waiting for authentication...")
            data = pickle.loads(conn.recv(2048))
            if data == self.password:
                self._print_log("Password accepted.")
                conn.sendall(pickle.dumps({"status": "success"}))
                break
            else:
                conn.sendall(
                    pickle.dumps({"status": "error", "message": "Invalid password."})
                )
                self._print_log(f"Invalid password from {addr}.")
                conn.close()

    def _handle_client_connection(self, conn, addr, process_func):
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    self._print_log(f"Connection closed by {addr}.")
                    break
                data = pickle.loads(data)
                response = process_func(data)

                if not data.get("periodic", False):
                    self._print_log(f"Processed data: {data} Response: {response}")

                conn.sendall(pickle.dumps(response))
            except socket.timeout:
                continue
            except ConnectionResetError:
                self._print_log(f"Connection reset by {addr}.")
                break
            except Exception as _:
                self._print_log(
                    f"Error in client connection function: {traceback.format_exc()}"
                )

    def _process_command(self, data):
        command, args = data.get("command"), data.get("args")
        if command and self.command_handler:
            try:
                return self.command_handler(command, args)
            except Exception as e:
                self._print_log(
                    f"Error occurred while executing command: {command} Error: {e}"
                )
                return {
                    "status": "error",
                    "message": f"An error occurred in the command: {e}",
                }
        return {
            "status": "error",
            "message": "Invalid command or no handler registered.",
        }

    def _process_data(self, data):
        key, value = data.get("key"), data.get("data")
        if key and value:
            self.data[key] = value
            return {"status": "success", "message": f"Data updated: {self.data}"}
        return {"status": "error", "message": "Invalid data format."}

    def _process_get_request(self, data):
        key = data.get("key")
        request_all = data.get("request_all", False)
        if request_all:
            return {"status": "success", "data": self.data}
        return {"status": "success", "data": self.data.get(key, "Key not found.")}


if __name__ == "__main__":
    server = Server()
    input("Press Enter to close the server.")
