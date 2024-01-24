from constants import (
    arm_1_length,
    arm_2_length,
    end_effector_length,
    shoulder_y_offset,
    height_to_shoulder,
    position_error_offsets,
)
import math
import numpy as np
from geometry import (
    Vector3,
    rotate_point,
    rotate_point_around_axis,
    is_point_in_any_cube,
)


def get_angles(x_pos, y_pos, z_pos, restricted_ares):
    """
    Get the angles of the robot arm
    :param x_pos: x position of the end effector
    :param y_pos: y position of the end effector
    :param z_pos: z position of the end effector
    :param restricted_ares: list of restricted areas for the robot arm, each area is a Cube object
    :return: angles in radians (base angle, shoulder angle, elbow angle)
    """
    # soh cah toa
    z_pos -= height_to_shoulder

    x_pos += position_error_offsets[0]
    y_pos += position_error_offsets[1]
    z_pos += position_error_offsets[2]

    if is_point_in_any_cube(restricted_ares, (x_pos, y_pos, z_pos)):
        raise ValueError("Target position is in a restricted area")

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

    # correct for offset
    base_angle -= math.degrees(math.tan(shoulder_y_offset / y_flat_distance))

    return -base_angle, -shoulder_angle, -elbow_angle


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
        abs(base_angle - base_controller.position),
        abs(shoulder_angle - shoulder_controller.position),
        abs(elbow_angle - elbow_controller.position),
    )

    # Find the maximum angle
    max_angle = max(base_angle, shoulder_angle, elbow_angle)

    # Calculate relative speeds
    base_speed = 1 if base_angle == 0 else base_angle / max_angle
    shoulder_speed = 1 if shoulder_angle == 0 else shoulder_angle / max_angle
    elbow_speed = 1 if elbow_angle == 0 else elbow_angle / max_angle

    return base_speed, shoulder_speed, elbow_speed


def get_wrist_position(position, wrist_angles):
    """
    Get the wrist position
    :param position: position of the end target point (x, y, z)
    :param wrist_angles: wrist angles in degrees (x_axis, y_axis, z_axis)
    :return: wrist position (x, y, z)
    """
    end_effector_vector = Vector3(position, wrist_angles, end_effector_length)

    return end_effector_vector.end_point


def get_wrist_angles(arm_angles, target_position, wrist_position):
    """
    Get the wrist angles
    :param arm_angles: arm angles in degrees (base, shoulder, elbow)
    :param target_position: target position of the end effector (x, y, z)
    :param wrist_position: wrist position (x, y, z)
    :return: wrist angles in degrees (x_axis, y_axis, z_axis)
    """
    total_arm_angle = abs(arm_angles[1] + arm_angles[2])

    target_position = np.array(target_position)
    wrist_position = np.array(wrist_position)

    yaw_rotation = math.degrees(math.atan2(wrist_position[1], wrist_position[0]))

    target_position = rotate_point(target_position, (0, 0, 0), (0, 0, -yaw_rotation))
    wrist_position = rotate_point(wrist_position, (0, 0, 0), (0, 0, -yaw_rotation))

    target_position -= wrist_position

    target_position = rotate_point(target_position, (0, 0, 0), (0, total_arm_angle, 0))

    needed_wrist_z_angle = math.degrees(
        math.atan2(target_position[0], target_position[1])
    )

    flat_distance = math.sqrt(target_position[0] ** 2 + target_position[1] ** 2)

    needed_wrist_y_angle = math.degrees(math.atan2(target_position[2], flat_distance))

    return 90 + needed_wrist_z_angle, 90 - needed_wrist_y_angle


def get_pos_from_angles(arm_angles, wrist_angles):
    """
    Get the position (x, y, z) of the robot arm end effector
    :param wrist_angles: the wrist angles in degrees (x_axis, y_axis, z_axis)
    :param arm_angles (base angle, shoulder angle, elbow angle) in degrees
    :return: x, y, z coordinates of the end effector
    """
    base_angle, shoulder_angle, elbow_angle = arm_angles

    base_vector = Vector3((0, 0, 0), (0, 0, 0), height_to_shoulder)

    transfer_vector = Vector3(
        base_vector.end_point,
        (90, 0, 0),
        shoulder_y_offset,
        angle_order="xyz",
    )
    transfer_vector.rotate_global((0, 0, base_angle))

    shoulder_vector = Vector3(
        transfer_vector.end_point,
        (0, shoulder_angle, 0),
        arm_1_length,
        angle_order="yxz",
    )
    shoulder_vector.rotate_global((0, 0, base_angle))

    elbow_vector = Vector3(
        shoulder_vector.end_point,
        (0, elbow_angle + shoulder_angle, 0),
        arm_2_length,
        angle_order="yxz",
    )
    elbow_vector.rotate_global((0, 0, base_angle))

    wrist_vector = Vector3(
        elbow_vector.end_point,
        (0, shoulder_angle + elbow_angle + wrist_angles[1], 0),
        end_effector_length,
        angle_order="xyz",
    )
    wrist_vector.rotate_global((0, 0, base_angle))

    end_position = tuple(
        rotate_point_around_axis(
            wrist_vector.end_point,
            elbow_vector.end_point,
            elbow_vector.starting_point,
            wrist_angles[0],
        )
    )

    return end_position
