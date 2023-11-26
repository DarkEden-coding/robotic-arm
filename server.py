import socket

HOST = "arm.local"  # The server's hostname or IP address
PORT = 1098  # The port used by the server

# Create a socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Bind the socket to the server address and port
    s.bind((HOST, PORT))

    # Listen for incoming connections
    s.listen()

    print(f"Server listening on {HOST}:{PORT}")

    # Accept a connection from a client
    conn, addr = s.accept()

    while True:
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"Received: {data.decode()}")
