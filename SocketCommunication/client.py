import json
import os
import pickle
import socket


class Client:
    def __init__(self, host="127.0.0.1", port=65432, name="Client"):
        """
        Client class that can send connections through 3 sockets to a server
        :param host: The host to target (server ip address)
        :param port: The starting port to target (each socket uses ports added onto this ie: x, x+1, x+2)
        :param name: The name that the client will display to the server
        """
        self.host = host
        self.port = port
        self.name = name
        self.password = None
        self.server_public_key = None
        self.log = ""
        self.file_path = os.path.dirname(os.path.realpath(__file__))

        self._load_settings()
        self.sockets = self._create_sockets()

    def _print_log(self, message):
        self.log += message + "\n"
        print(message)

    def _load_settings(self):
        if os.path.exists(f"{self.file_path}/network-settings.json"):
            with open(f"{self.file_path}/network-settings.json", "r") as f:
                settings = json.load(f)
            self.host = settings.get("host", self.host)
            self.port = settings.get("port", self.port)
            self.password = settings.get("password", self.password)

    def _create_sockets(self):
        sockets = []
        for i in range(3):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port + i))
            self._print_log(f"Connected to {self.host}:{self.port + i}")
            self._authenticate(s)
            s.settimeout(5)
            sockets.append(s)
        return sockets

    def _authenticate(self, sock):
        sock.sendall(pickle.dumps(self.password))
        self._print_log(f"{self.name} sent password. Waiting for server reply...")
        reply = pickle.loads(sock.recv(2048))
        if reply.get("status") == "error":
            self._print_log(f"Error: {reply.get('message')}")
            raise ConnectionRefusedError("Server refused connection.")
        else:
            self._print_log(f"{self.name} connected successfully.")

    def _send_and_receive(self, sock, data):
        try:
            sock.sendall(pickle.dumps(data))
            if not data.get("periodic", False):
                self._print_log(f"{self.name} sent: {data}")
            response = pickle.loads(sock.recv(1024))
            if not data.get("periodic", False):
                self._print_log(f"{self.name} received: {response}")
            return response
        except socket.timeout:
            return {"status": "error", "message": "Timed out."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def send_command(self, command, args=None, periodic=False):
        """
        Function to send a command request to the server
        :param command: command name to send
        :param args: args to the command that is sent
        :param periodic: weather to pass the request as a periodic request (excludes from logs)
        :return: the return of the command or errors therein
        """
        return self._send_and_receive(
            self.sockets[0], {"command": command, "args": args, "periodic": periodic}
        )

    def send_data(self, key, data, periodic=False):
        """
        Function to send data that will be stored in the shared data bus on the server
        :param key: what key to access
        :param data: what data to set the key to
        :param periodic: weather to pass the request as a periodic request (excludes from logs)
        :return: the result of the request
        """
        return self._send_and_receive(
            self.sockets[1], {"key": key, "data": data, "periodic": periodic}
        )

    def get_data(self, key, request_all=False, periodic=False):
        """
        Function to get data that is stored on the server
        :param key: what key value to get
        :param request_all: weather to request all data or only the provided key
        :param periodic: weather to pass the request as a periodic request (excludes from logs)
        :return: the result of the request
        """
        return self._send_and_receive(
            self.sockets[2],
            {"key": key, "request_all": request_all, "periodic": periodic},
        )
