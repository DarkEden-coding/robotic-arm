import json
import can
import struct
import subprocess

print("Starting CAN Testing")

command = "sudo ip link set can0 up type can bitrate 250000"
try:
    subprocess.run(command, shell=True, check=True)
    print("CAN Connection command executed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")

with open("flat_endpoints.json", "r") as f:
    endpoint_data = json.load(f)
    endpoints = endpoint_data["endpoints"]

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

print("Setting up CAN")

bus = can.interface.Bus("can0", bustype="socketcan")

# Flush CAN RX buffer so there are no more old pending messages
while not (bus.recv(timeout=0) is None):
    pass

node_id = 0  # must match `<odrv>.axis0.config.can.node_id`. The default is 0.
cmd_id = 0x01  # heartbeat command ID
message_id = node_id << 5 | cmd_id

for msg in bus:
    if msg.arbitration_id == message_id:
        error, state, result, traj_done = struct.unpack("<IBBB", bytes(msg.data[:7]))
        print(error, state, result, traj_done)
        break

# Flush CAN RX buffer so there are no more old pending messages
while not (bus.recv(timeout=0) is None):
    pass

# Send read command
bus.send(
    can.Message(
        arbitration_id=(node_id << 5 | 0x00),  # 0x00: Get_Version
        data=b"",
        is_extended_id=False,
    )
)

# Await reply
for msg in bus:
    if msg.arbitration_id == (node_id << 5 | 0x00):  # 0x00: Get_Version
        break

(
    _,
    hw_product_line,
    hw_version,
    hw_variant,
    fw_major,
    fw_minor,
    fw_revision,
    fw_unreleased,
) = struct.unpack("<BBBBBBBB", msg.data)

try:
    # If one of these asserts fail, you're probably not using the right flat_endpoints.json file
    assert endpoint_data["fw_version"] == f"{fw_major}.{fw_minor}.{fw_revision}"
    assert endpoint_data["hw_version"] == f"{hw_product_line}.{hw_version}.{hw_variant}"
except AssertionError:
    print(
        f"Error: Endpoint JSON file is for hardware version {endpoint_data['hw_version']} and firmware version {endpoint_data['fw_version']}, but the connected hardware is version {hw_product_line}.{hw_version}.{hw_variant} and firmware version {fw_major}.{fw_minor}.{fw_revision}"
    )
    exit(1)

# ----------------------------------------setup-end----------------------------------------

print("Done setting up CAN")


def send_bus_message(value, obj_path):
    # Convert path to endpoint ID
    endpoint_id = endpoints[obj_path]["id"]
    endpoint_type = endpoints[obj_path]["type"]

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


def get_property_value(obj_path):
    # Convert path to endpoint ID
    endpoint_id = endpoints[obj_path]["id"]
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

    # Unpack and print reply
    _, _, _, return_value = struct.unpack(
        "<BHB" + format_lookup[endpoint_type], msg.data
    )
    return return_value


path = "vbus_voltage"
print(f"Current Voltage: {get_property_value(path)}")

while get_property_value(path) < 20:
    pass

print("--Voltage Is Above Required--")

print("Enabling Closed Loop Control")
send_bus_message(8, "axis0.requested_state")

print("moving to position 12.5")
send_bus_message(12.5, "axis0.controller.input_pos")
input("Press Enter to continue...")

print("moving to position 0")
send_bus_message(0, "axis0.controller.input_pos")

input("Press Enter to continue...")

print("moving to position -12.5")
send_bus_message(-12.5, "axis0.controller.input_pos")

input("Press Enter to continue...")

print("moving to position 0")
send_bus_message(0, "axis0.controller.input_pos")

print("Disabling Closed Loop Control")
send_bus_message(1, "axis0.requested_state")

# Shutdown the CAN bus
bus.shutdown()
