from constants import (
    arm_1_length,
    arm_2_length,
)
import math


class Cube:
    def __init__(self, corner1, corner2):
        """
        Initialize the cube with two opposite corners.
        :param corner1: Tuple (x, y, z) representing one corner of the cube.
        :param corner2: Tuple (x, y, z) representing the opposite corner of the cube.
        """
        self.min_x = min(corner1[0], corner2[0])
        self.max_x = max(corner1[0], corner2[0])
        self.min_y = min(corner1[1], corner2[1])
        self.max_y = max(corner1[1], corner2[1])
        self.min_z = min(corner1[2], corner2[2])
        self.max_z = max(corner1[2], corner2[2])

    def contains_point(self, point):
        """
        Check if a point is inside the cube.
        :param point: Tuple (x, y, z) representing a point in 3D space.
        :return: Boolean indicating whether the point is inside the cube.
        """
        x, y, z = point
        return (
            self.min_x <= x <= self.max_x
            and self.min_y <= y <= self.max_y
            and self.min_z <= z <= self.max_z
        )


def is_point_in_any_cube(cubes, point):
    """
    Check if the point is inside any of the given cubes.
    :param cubes: List of Cube objects.
    :param point: Tuple (x, y, z) representing a point in 3D space.
    :return: Boolean indicating whether the point is in any of the cubes.
    """
    return any(cube.contains_point(point) for cube in cubes)


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
    z_pos -= 180

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
        abs(base_angle - base_controller.position),
        abs(shoulder_angle - shoulder_controller.position),
        abs(elbow_angle - elbow_controller.position),
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


def get_pos_from_angles(angles):
    """
    Get the position of the end effector from the angles
    :param angles: angles in radians (base angle, shoulder angle, elbow angle)
    :return: position of the end effector (x, y, z)
    """
    base_angle, shoulder_angle, elbow_angle = angles

    base_angle = math.radians(base_angle)
    shoulder_angle = math.radians(shoulder_angle)
    elbow_angle = math.radians(elbow_angle)

    x_pos = (
        math.cos(base_angle)
        * (arm_1_length * math.cos(shoulder_angle) + arm_2_length * math.cos(elbow_angle))
    )
    y_pos = (
        math.sin(base_angle)
        * (arm_1_length * math.cos(shoulder_angle) + arm_2_length * math.cos(elbow_angle))
    )
    z_pos = arm_1_length * math.sin(shoulder_angle) + arm_2_length * math.sin(elbow_angle)

    return x_pos, y_pos, z_pos
