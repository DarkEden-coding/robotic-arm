from CAN_Control.odrive_controller import odrive_controller
from CAN_Control.can_functions import shutdown
import math

from constants import (
    arm_1_length,
    arm_2_length,
)


def get_angles(x_pos, y_pos, z_pos):
    """
    Get the angles of the robot arm
    :param x_pos: x position of the end effector
    :param y_pos: y position of the end effector
    :param z_pos: z position of the end effector
    :return: angles in radians (base angle, shoulder angle, elbow angle)
    """
    # soh cah toa
    z_pos -= 180

    target_distance = math.sqrt(x_pos**2 + y_pos**2 + z_pos**2)
    if target_distance > arm_1_length + arm_2_length:
        raise ValueError("Target position is out of reach")

    base_angle = math.atan2(y_pos, x_pos)

    y_flat_distance = math.sqrt((0 - x_pos) ** 2 + (0 - y_pos) ** 2)

    rotated_point = (y_flat_distance, z_pos)

    x_flat_distance = math.sqrt(
        (0 - rotated_point[0]) ** 2 + (0 - rotated_point[1]) ** 2
    )

    shoulder_offset = math.atan2(rotated_point[1], rotated_point[0])

    shoulder_angle = math.acos(
        (arm_1_length**2 + x_flat_distance**2 - arm_2_length**2)
        / (2 * arm_1_length * x_flat_distance)
    )

    shoulder_angle += shoulder_offset

    elbow_angle = math.acos(
        (arm_2_length**2 + arm_1_length**2 - x_flat_distance**2)
        / (2 * arm_2_length * arm_1_length)
    )

    # convert to degrees
    base_angle = math.degrees(base_angle)
    shoulder_angle = 90 - math.degrees(shoulder_angle)
    elbow_angle = 180 - math.degrees(elbow_angle)

    return base_angle, shoulder_angle, -elbow_angle


def get_trajectory(
    base_angle,
    shoulder_angle,
    elbow_angle,
    base_controller,
    shoulder_controller,
    elbow_controller,
):
    """
    Get the relative speeds for the robot arm joints
    :param base_angle: base angle in degrees
    :param shoulder_angle: shoulder angle in degrees
    :param elbow_angle: elbow angle in degrees
    :param base_controller: base controller object
    :param shoulder_controller: shoulder controller object
    :param elbow_controller: elbow controller object
    :return: relative speeds for base, shoulder, and elbow joints
    """
    base_angle, shoulder_angle, elbow_angle = (
        abs(base_angle - base_controller.requested_position),
        abs(shoulder_angle - shoulder_controller.requested_position),
        abs(elbow_angle - elbow_controller.requested_position),
    )

    print(f"Base angle: {base_angle}")
    print(f"Shoulder angle: {shoulder_angle}")
    print(f"Elbow angle: {elbow_angle}")

    # Find the maximum angle
    max_angle = max(base_angle, shoulder_angle, elbow_angle)

    # Calculate relative speeds
    base_speed = 1 if base_angle == 0 else base_angle / max_angle
    shoulder_speed = 1 if shoulder_angle == 0 else shoulder_angle / max_angle
    elbow_speed = 1 if elbow_angle == 0 else elbow_angle / max_angle

    print(f"Base speed: {base_speed}")
    print(f"Shoulder speed: {shoulder_speed}")
    print(f"Elbow speed: {elbow_speed}")
    return base_speed, shoulder_speed, elbow_speed


controller_1 = odrive_controller(0)
controller_2 = odrive_controller(1, gear_ratio=125)
controller_3 = odrive_controller(2)

controller_1.enable_motor()
controller_2.enable_motor()
controller_3.enable_motor()

angles = get_angles(400, 0, 0)
base_offset, shoulder_offset, elbow_offset = get_trajectory(
    *angles, controller_1, controller_2, controller_3
)

controller_1.move_to_angle(angles[0], base_offset)
controller_2.move_to_angle(angles[1], shoulder_offset)
controller_3.move_to_angle(angles[2], elbow_offset)

controller_1.wait_for_move()
controller_2.wait_for_move()
controller_3.wait_for_move()

input("Press enter to continue")
print("\n")

angles = get_angles(400, 400, 0)
base_offset, shoulder_offset, elbow_offset = get_trajectory(
    *angles, controller_1, controller_2, controller_3
)

controller_1.move_to_angle(angles[0], base_offset)
controller_2.move_to_angle(angles[1], shoulder_offset)
controller_3.move_to_angle(angles[2], elbow_offset)

controller_1.wait_for_move()
controller_2.wait_for_move()
controller_3.wait_for_move()

input("Press enter to continue")
print("\n")

angles = get_angles(400, 0, 0)
base_offset, shoulder_offset, elbow_offset = get_trajectory(
    *angles, controller_1, controller_2, controller_3
)

controller_1.move_to_angle(angles[0], base_offset)
controller_2.move_to_angle(angles[1], shoulder_offset)
controller_3.move_to_angle(angles[2], elbow_offset)

controller_1.wait_for_move()
controller_2.wait_for_move()
controller_3.wait_for_move()

input("Press enter to continue")
print("\n")

controller_1.move_to_angle(0)
controller_2.move_to_angle(-2)
controller_3.move_to_angle(0)

controller_1.wait_for_move()
controller_2.wait_for_move()
controller_3.wait_for_move()

controller_1.disable_motor()
controller_2.disable_motor()
controller_3.disable_motor()

shutdown()
