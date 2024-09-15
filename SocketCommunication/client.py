import socket
import pickle
import os
import json
import rsa


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

        self._load_settings()
        self.public_key, self.private_key = rsa.newkeys(2048)
        self.sockets = self._create_sockets()

    def _load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
            self.host = settings.get("host", self.host)
            self.port = settings.get("port", self.port)
            self.password = settings.get("password", self.password)

    def _create_sockets(self):
        sockets = []
        for i in range(3):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port + i))
            print(f"Connected to {self.host}:{self.port + i}")
            self._setup_encryption(s)
            s.settimeout(5)
            sockets.append(s)
        return sockets

    def _setup_encryption(self, sock):
        sock.sendall(pickle.dumps(self.password))
        print(f"{self.name} sent password. Waiting for server reply...")
        reply = pickle.loads(sock.recv(2048))
        if reply.get("status") == "error":
            raise ConnectionRefusedError("Server refused connection.")
        self.server_public_key = rsa.PublicKey.load_pkcs1(reply["public_key"])
        sock.sendall(pickle.dumps(self.public_key.save_pkcs1()))
        print(f"Server public key received: {self.server_public_key}")

    def encrypt_data(self, data):
        """
        Encrypts data that will be sent to the server
        :param data: The data to be encrypted
        :return: The encrypted data
        """
        return rsa.encrypt(data, self.server_public_key)

    def decrypt_data(self, data):
        """
        Decrypts data that was sent from the server
        :param data: The data to be decrypted
        :return: The decrypted data
        """
        return rsa.decrypt(data, self.private_key)

    def _send_and_receive(self, sock, data):
        try:
            sock.sendall(self.encrypt_data(pickle.dumps(data)))
            print(f"{self.name} sent: {data}")
            response = pickle.loads(self.decrypt_data(sock.recv(1024)))
            return response
        except socket.timeout:
            return {"status": "error", "message": "Timed out."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def send_command(self, command, args=None):
        """
        Function to send a command request to the server
        :param command: command name to send
        :param args: args to the command that is sent
        :return: the return of the command or errors therein
        """
        return self._send_and_receive(
            self.sockets[0], {"command": command, "args": args}
        )

    def send_data(self, key, data):
        """
        Function to send data that will be stored in the shared data bus on the server
        :param key: what key to access
        :param data: what data to set the key to
        :return: the result of the request
        """
        return self._send_and_receive(self.sockets[1], {"key": key, "data": data})

    def get_data(self, key, request_all=False):
        """
        Function to get data that is stored on the server
        :param key: what key value to get
        :param request_all: weather to request all data or only the provided key
        :return: the result of the request
        """
        return self._send_and_receive(
            self.sockets[2], {"key": key, "request_all": request_all}
        )


if __name__ == "__main__":
    client = Client()
    while True:
        command = input("Enter command: ")
        if command == "exit":
            break
        print(client.send_command(command, input("Enter arguments: ")))
