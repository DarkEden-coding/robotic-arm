from SocketCommunication.server import Server


server_connection = Server()


def command_handler(command, args):
    if command == "move":
        return {"status": "success", "result": sum(args)}
    return {"status": "error", "message": "Invalid command."}


server_connection.register_command_handler(command_handler)
