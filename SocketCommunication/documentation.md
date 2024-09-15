# Usage Documentation for Client-Server System

This document provides instructions on how to use the client-server system developed in Python with socket communication, RSA encryption, and `pickle` serialization. Below are the steps for setting up and running the server and client, along with example usage scenarios.

## Prerequisites
Before starting, ensure that you have the following dependencies installed:
- `rsa` (for encryption)
- `pickle` (for serialization, included in Python standard library)
- `socket` (included in Python standard library)
- `json` (included in Python standard library)
- `threading` (included in Python standard library)
  
You can install the `rsa` library using pip:
```bash
pip install rsa
```

## Server Setup

### Initialization

1. **Create a Server Instance**:
   The server can be started by importing the `Server` class and creating an instance with default or custom configurations for the host and port.
   
   Example:
   ```python
   from server import Server

   server = Server()  # Defaults: host='127.0.0.1', port=65432, name='Client'
   ```

2. **Command Handler Registration**:
   The server must be configured to handle specific commands by registering a command handler function. This handler processes the commands received from the client.
   
   Example command handler registration:
   ```python
   def handle_command(command, args):
       if command == "print":
           if not args:
               return {"status": "error", "message": "No arguments provided."}
           print(args)
           return {"status": "success", "message": "Printed successfully."}
       elif command == "add":
           if not args:
               return {"status": "error", "message": "No arguments provided."}
           print(f"Sum: {sum(args)}...")
           return {"status": "success", "message": "Added successfully."}

   server.register_command_handler(handle_command)
   ```

3. **Start the Server**:
   The server automatically listens for connections once the `Server` instance is created and threads for handling commands, data, and get requests are started.

### Command Handler
- **print**: Accepts a string as an argument and prints it.
- **add**: Accepts a list of numbers, calculates their sum, and prints the result.

## Client Setup

### Initialization

1. **Create a Client Instance**:
   The client connects to the server using the same host and port values. Optionally, the client can load configurations from a `settings.json` file if it exists.

   Example:
   ```python
   from client import Client

   client = Client()  # Defaults: host='127.0.0.1', port=65432, name='Client'
   ```

### Sending Commands and Data

2. **Sending Commands**:
   The client can send commands to the server using the `send_command` method, where the command and its arguments (if any) are passed.

   Example:
   ```python
   client.send_command("print", "Hello, Server!")
   client.send_command("add", [1, 2, 3])
   ```

3. **Sending Data**:
   To store data on the server, use the `send_data` method. This method requires a key and data to store.

   Example:
   ```python
   client.send_data("example_key", {"some": "data"})
   ```

4. **Retrieving Data**:
   To retrieve stored data, the client can use the `get_data` method by providing a key or requesting all data.

   Example:
   ```python
   client.get_data("example_key")  # Get specific data
   client.get_data(request_all=True)  # Get all stored data
   ```

### Running the Client

To run the client interactively:
```python
if __name__ == "__main__":
    client = Client()

    while True:
        command = input("Enter command: ")
        if command == "exit":
            break
        print(f"{client.send_command(command, input('Enter arguments: '))} \n")
```

### Error Handling

Both the server and client handle errors during communication:
- **Timeouts**: If a connection takes too long, a timeout error will be returned.
- **Invalid Commands**: The server will return an error message if a command is not recognized or no command handler is registered.
- **Invalid Data**: Both client and server provide error messages if data formatting or encryption fails.

## Server Configuration

Optionally, a `settings.json` file can be used to configure the server and client. The file should be located in the same directory as the script and can contain the following fields:
```json
{
  "host": "127.0.0.1",
  "port": 65432,
  "password": "my_secure_password"
}
```

This configuration allows dynamic setup of server and client properties like the host, port, and password for authentication.

---

By following these instructions, you can run and test the client-server system using RSA encryption for secure communication and `pickle` for data serialization.