import can
import struct
import json
import subprocess

with open("flat_endpoints.json", "r") as f:
    endpoint_data = json.load(f)
    endpoints = endpoint_data["endpoints"]

command = "sudo ip link set can0 up type can bitrate 250000"
try:
    subprocess.run(command, shell=True, check=True)
    print("CAN Connection command executed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")

OPCODE_READ = 0x00
OPCODE_WRITE = 0x01

# See https://docs.python.org/3/library/struct.html#format-characters
format_lookup = {
    "bool": "?",
    "uint8": "B",
    "int8": "b",
    "uint16": "H",
    "int16": "h",
    "uint32": "I",
    "int32": "i",
    "uint64": "Q",
    "int64": "q",
    "float": "f",
}

bus = can.interface.Bus("can0", bustype="socketcan")


def send_bus_message(value, obj_path, node_id, return_value=False):
    """
    Send a CAN message to an ODrive
    :param return_value: if True, return any output
    :param value: What value to send
    :param obj_path: Path of the property to send to
    :param node_id: Node id of the ODrive controller
    :return:
    """
    # Convert path to endpoint ID
    endpoint_id = endpoints[obj_path]["id"]
    endpoint_type = endpoints[obj_path]["type"]

    if endpoint_type == "function":
        if value is None:
            bus.send(
                can.Message(
                    arbitration_id=(node_id << 5 | 0x04),  # 0x04: RxSdo
                    data=struct.pack(
                        "<BHB",
                        OPCODE_WRITE,
                        endpoint_id,
                        0,
                    ),
                    is_extended_id=False,
                )
            )
        else:
            bus.send(
                can.Message(
                    arbitration_id=(node_id << 5 | 0x04),  # 0x04: RxSdo
                    data=struct.pack(
                        "<BHB"
                        + format_lookup[endpoints[obj_path]["inputs"][0]["type"]],
                        OPCODE_WRITE,
                        endpoint_id,
                        0,
                        value,
                    ),
                    is_extended_id=False,
                )
            )

        if return_value and len(endpoints[obj_path]["outputs"]) > 0:
            # Await reply
            for msg in bus:
                if msg.arbitration_id == (node_id << 5 | 0x05):  # 0x05: TxSdo
                    break

            # Unpack and print reply
            _, _, _, return_value = struct.unpack(
                "<BHB" + format_lookup[endpoint_type], msg.data
            )
            return return_value
        return

    # Send write command
    bus.send(
        can.Message(
            arbitration_id=(node_id << 5 | 0x04),  # 0x04: RxSdo
            data=struct.pack(
                "<BHB" + format_lookup[endpoint_type],
                OPCODE_WRITE,
                endpoint_id,
                0,
                value,
            ),
            is_extended_id=False,
        )
    )

    if "outputs" in endpoints[obj_path] and return_value:
        # Await reply
        for msg in bus:
            if msg.arbitration_id == (node_id << 5 | 0x05):  # 0x05: TxSdo
                break

        # Unpack and print reply
        _, _, _, return_value = struct.unpack(
            "<BHB" + format_lookup[endpoint_type], msg.data
        )
        return return_value


def get_property_value(obj_path, node_id):
    """
    Get the value of a property from an ODrive
    :param obj_path: Path of the property to get
    :param node_id: Node id of odrive controller
    :return:
    """
    # Convert path to endpoint ID
    endpoint_id = endpoints[obj_path]["id"]
    print(endpoint_id)
    endpoint_type = endpoints[obj_path]["type"]

    # Flush CAN RX buffer so there are no more old pending messages
    while not (bus.recv(timeout=0) is None):
        pass

    # Send read command
    bus.send(
        can.Message(
            arbitration_id=(node_id << 5 | 0x04),  # 0x04: RxSdo
            data=struct.pack("<BHB", OPCODE_READ, endpoint_id, 0),
            is_extended_id=False,
        )
    )

    # Await reply
    for msg in bus:
        if msg.arbitration_id == (node_id << 5 | 0x05):  # 0x05: TxSdo
            break

    print(msg.data)
    # Unpack and print reply
    _, _, _, return_value = struct.unpack(
        "<BHB" + format_lookup[endpoint_type], msg.data
    )
    return return_value


def shutdown():
    """
    Shutdown CAN bus
    :return:
    """
    bus.shutdown()
