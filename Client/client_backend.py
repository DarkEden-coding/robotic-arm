from SocketCommunication.client import Client

try:
    client = Client()
except ConnectionRefusedError:
    print("Server is not running or refused connection.")
    exit(1)


def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    return wrapper


@handle_errors
def send_command(text):
    command, *args = text.split(" ")
    response = client.send_command(command, args)
    return response


@handle_errors
def get_current_position():
    response = client.get_data("current_position")
    return response


@handle_errors
def get_current_speed():
    response = client.get_data("speed_percentage")
    return response


@handle_errors
def set_speed(speed):
    response = client.send_command("set_speed", [speed])
    return response


@handle_errors
def emergency_stop():
    client.send_data("emergency_stop", True)
    response = client.send_command("emergency_stop")
    return response


@handle_errors
def setup():
    response = client.send_command("setup")
    return response


@handle_errors
def get_server_logs():
    response = client.get_data("server_logs", periodic=True)
    return response


@handle_errors
def set_target_position(position):
    response = client.send_command("set_target_position", [position])
    return response


@handle_errors
def get_log():
    return client.log
