from CAN_Control.can_functions import (
    bus,
    send_bus_message,
    get_property_value,
    endpoints,
    endpoint_data,
)
import can
import struct
from time import sleep


def setup(node_id):
    print(f"Setting up CAN for ODrive with id: {node_id}")

    print("Waiting for main power...")
    while get_property_value("vbus_voltage", node_id) < 40:
        print(get_property_value("vbus_voltage", node_id))
        pass
    print("Main power detected")

    cmd_id = 0x01  # heartbeat command ID
    message_id = node_id << 5 | cmd_id

    for msg in bus:
        if msg.arbitration_id == message_id:
            print(f"ODrive with id {node_id}: step 1 complete")
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
            print(f"ODrive with id {node_id}: step 2 complete")
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
        assert (
            endpoint_data["hw_version"]
            == f"{hw_product_line}.{hw_version}.{hw_variant}"
        )
    except AssertionError:
        print(
            f"Error: Endpoint JSON file is for hardware version {endpoint_data['hw_version']} and firmware version {endpoint_data['fw_version']}, but the connected hardware is version {hw_product_line}.{hw_version}.{hw_variant} and firmware version {fw_major}.{fw_minor}.{fw_revision}"
        )
        exit(1)

    # clear errors
    print("Clearing errors...")
    send_bus_message(None, "clear_errors", node_id)
    print("ODrive errors cleared")

    send_bus_message(10, "axis0.trap_traj.config.vel_limit", node_id)

    send_bus_message(5, "axis0.controller.config.input_mode", node_id)
    send_bus_message(0.8, "axis0.trap_traj.config.accel_limit", node_id)
    send_bus_message(0.8, "axis0.trap_traj.config.decel_limit", node_id)

    print(f"------------------ ODrive with id {node_id} setup complete ------------------")


def warning_message(message):
    yellow_text = "\033[93m"
    reset_text = "\033[0m"
    print(f"{yellow_text}Warning: {message}{reset_text}")


def error_message(message):
    red_text = "\033[91m"
    reset_text = "\033[0m"
    print(f"{red_text}Error: {message}{reset_text}")


class odrive_controller:
    def __init__(self, id_number):
        self.node_id = id_number
        self.enabled = False
        self.position = 0
        self.requested_position = 0

        setup(self.node_id)
        self.zero_motor()

    def enable_motor(self):
        send_bus_message(8, "axis0.requested_state", self.node_id)
        self.enabled = True

    def disable_motor(self):
        send_bus_message(1, "axis0.requested_state", self.node_id)
        self.enabled = False

    def zero_motor(self):
        send_bus_message(0, "axis0.set_abs_pos", self.node_id)
        # print(f"Motor position offset by {offset} counts")
        self.position = 0

    def get_encoder_pos(self):
        return get_property_value("axis0.controller.pos_setpoint", self.node_id)

    def get_encoder_vel(self):
        return get_property_value("encoder_estimator0.vel_estimate", self.node_id)

    def set_speed(self, speed):
        """
        Set the speed of the motor
        :param speed: speed in a percentage of 10 rps
        :return:
        """
        speed = speed / 10
        send_bus_message(speed, "axis0.trap_traj.config.vel_limit", self.node_id)
        print(f"Speed set to {speed} rps")

    def set_torque(self, torque):
        """
        Set the torque of the motor
        :param torque: Torque in Nm
        """
        send_bus_message(torque, "axis0.controller.input_torque", self.node_id)

    def wait_for_move(self, delay=0.05):
        while (
                abs(self.requested_position - self.get_encoder_pos()) > 0.1
        ):
            pass
        sleep(delay)
        print("Move complete")

    def move_to_pos(self, pos):
        """
        Move to a position
        :param pos: pos in revolutions
        :return:
        """
        print(f"Moving to position {pos}...")
        if not self.enabled:
            warning_message("Motor is not enabled, enabling...")
            self.enable_motor()
        send_bus_message(pos, "axis0.controller.input_pos", self.node_id)

        self.requested_position = pos

    def move_to_angle(self, angle):
        """
        Move to an angle
        :param angle: angle in degrees
        :return:
        """
        revolutions = (angle / 360)*25

        print(f"Moving to angle {angle} by going to {revolutions} revolutions...")
        if not self.enabled:
            warning_message("Motor is not enabled, enabling...")
            self.enable_motor()
        send_bus_message(revolutions, "axis0.controller.input_pos", self.node_id)

        self.requested_position = revolutions
