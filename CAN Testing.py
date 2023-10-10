import json
import can
import struct

print("Starting CAN Testing")

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

# If one of these asserts fail, you're probably not using the right flat_endpoints.json file
assert endpoint_data["fw_version"] == f"{fw_major}.{fw_minor}.{fw_revision}"
assert endpoint_data["hw_version"] == f"{hw_product_line}.{hw_version}.{hw_variant}"

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


def get_bus_prop_value(obj_path):
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


def call_function(obj_path):
    # Convert path to endpoint ID
    endpoint_id = endpoints[obj_path]['id']
    endpoint_type = endpoints[obj_path]["type"]

    bus.send(can.Message(
        arbitration_id=(node_id << 5 | 0x04),  # 0x04: RxSdo
        data=struct.pack('<BHB', OPCODE_WRITE, endpoint_id, 0),
        is_extended_id=False
    ))

    for msg in bus:
        _, _, _, return_value = struct.unpack(
            "<BHB" + format_lookup[endpoint_type], msg.data
        )
        print(return_value)


path = "vbus_voltage"
call_function(path)

while call_function(path) < 20:
    pass

path = "odrv0.axis0.controller.config.input_filter_bandwidth"
value_to_write = 2

send_bus_message(value_to_write, path)

path = "odrv0.axis0.controller.config.input_mode"
value_to_write = "InputMode.POS_FILTER"

send_bus_message(value_to_write, path)

path = "odrv0.axis0.controller.input_pos"
value_to_write = 25

send_bus_message(value_to_write, path)
