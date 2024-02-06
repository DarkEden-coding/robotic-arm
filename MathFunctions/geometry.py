import math
import numpy as np


def decode_string_to_cube(string):
    """
    Decode a string into a Cube object.
    :param string: the string to decode
    :return:
    """
    corner1 = tuple(map(float, string.split(" ")[:3]))
    corner2 = tuple(map(float, string.split(" ")[3:]))
    return Cube(corner1, corner2)


class Cube:
    def __init__(self, corner1, corner2):
        """
        Initialize the cube with two opposite corners.
        :param corner1: Tuple (x, y, z) representing one corner of the cube.
        :param corner2: Tuple (x, y, z) representing the opposite corner of the cube.
        """
        self.corner1 = corner1
        self.corner2 = corner2
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

    def encode(self):
        return f"{self.corner1[0]} {self.corner1[1]} {self.corner1[2]} {self.corner2[0]} {self.corner2[1]} {self.corner2[2]}"


class Vector3:
    def __init__(self, starting_point, angles, length, angle_order="zyx"):
        """
        Initialize the vector
        :param starting_point: Tuple (x, y, z) representing the starting point of the vector
        :param angles: Tuple (x, y, z) representing the angles of the vector on the x, y, and z global axes
        :param length: Length of the vector
        """
        self.starting_point = starting_point
        if len(angles) == 3:
            self.x_angle, self.y_angle, self.z_angle = -angles[0], angles[1], angles[2]
        else:
            self.x_angle, self.y_angle = -angles[0], angles[1]
            self.z_angle = 0
        self.length = length
        self.angle_order = angle_order

        self.end_point = np.array(
            [
                self.starting_point[0],
                self.starting_point[1],
                self.length + self.starting_point[2],
            ]
        )

        self.end_point = rotate_point(
            self.end_point,
            self.starting_point,
            (self.x_angle, self.y_angle, self.z_angle),
            self.angle_order,
        )

    def rotate_global(self, angles):
        """
        Rotate the vector
        :param angles: Tuple (x, y, z) representing the angles of the vector on the x, y, and z axes
        :return: None
        """
        self.end_point = rotate_point(
            self.end_point,
            self.starting_point,
            angles,
            self.angle_order,
        )

    def __str__(self):
        return f"Vector3(starting_point={tuple(self.starting_point)}, end_point={tuple(self.end_point)}, length={self.length}"


def rotate_point(point, origin, angles, order="zyx"):
    """
    Rotate a point
    :param point: Tuple (x, y, z) representing the point to rotate
    :param origin: Tuple (x, y, z) representing the origin of the rotation
    :param angles: Tuple (x, y, z) representing the angles of the vector on the x, y, and z axes
    :param order: String representing the order of the rotations
    :return: Tuple (x, y, z) representing the rotated point
    """
    x_matrix = np.array(
        [
            [1, 0, 0],
            [0, math.cos(math.radians(angles[0])), -math.sin(math.radians(angles[0]))],
            [0, math.sin(math.radians(angles[0])), math.cos(math.radians(angles[0]))],
        ]
    )

    y_matrix = np.array(
        [
            [math.cos(math.radians(-angles[1])), 0, math.sin(math.radians(-angles[1]))],
            [0, 1, 0],
            [
                -math.sin(math.radians(-angles[1])),
                0,
                math.cos(math.radians(-angles[1])),
            ],
        ]
    )

    z_matrix = np.array(
        [
            [math.cos(math.radians(angles[2])), -math.sin(math.radians(angles[2])), 0],
            [math.sin(math.radians(angles[2])), math.cos(math.radians(angles[2])), 0],
            [0, 0, 1],
        ]
    )

    mapping = {
        "xyz": x_matrix @ y_matrix @ z_matrix,
        "xzy": x_matrix @ z_matrix @ y_matrix,
        "yxz": y_matrix @ x_matrix @ z_matrix,
        "yzx": y_matrix @ z_matrix @ x_matrix,
        "zxy": z_matrix @ x_matrix @ y_matrix,
        "zyx": z_matrix @ y_matrix @ x_matrix,
    }

    rotation_matrix = np.around(mapping[order], 5)

    point = np.array(point)
    origin = np.array(origin)

    point -= origin

    point = rotation_matrix @ point

    point += origin

    return point


def rotate_point_around_axis(point, axis_start, axis_end, angle_degrees):
    # Convert angle to radians
    angle_radians = np.radians(angle_degrees)

    # Create a unit vector representing the axis of rotation
    axis_vector = np.array(axis_end) - np.array(axis_start)
    axis_unit_vector = axis_vector / np.linalg.norm(axis_vector)

    # Create the rotation matrix
    rotation_matrix = np.array(
        [
            [
                np.cos(angle_radians)
                + axis_unit_vector[0] ** 2 * (1 - np.cos(angle_radians)),
                axis_unit_vector[0] * axis_unit_vector[1] * (1 - np.cos(angle_radians))
                - axis_unit_vector[2] * np.sin(angle_radians),
                axis_unit_vector[0] * axis_unit_vector[2] * (1 - np.cos(angle_radians))
                + axis_unit_vector[1] * np.sin(angle_radians),
            ],
            [
                axis_unit_vector[1] * axis_unit_vector[0] * (1 - np.cos(angle_radians))
                + axis_unit_vector[2] * np.sin(angle_radians),
                np.cos(angle_radians)
                + axis_unit_vector[1] ** 2 * (1 - np.cos(angle_radians)),
                axis_unit_vector[1] * axis_unit_vector[2] * (1 - np.cos(angle_radians))
                - axis_unit_vector[0] * np.sin(angle_radians),
            ],
            [
                axis_unit_vector[2] * axis_unit_vector[0] * (1 - np.cos(angle_radians))
                - axis_unit_vector[1] * np.sin(angle_radians),
                axis_unit_vector[2] * axis_unit_vector[1] * (1 - np.cos(angle_radians))
                + axis_unit_vector[0] * np.sin(angle_radians),
                np.cos(angle_radians)
                + axis_unit_vector[2] ** 2 * (1 - np.cos(angle_radians)),
            ],
        ]
    )

    # Convert point and axis to NumPy arrays for easier manipulation
    point = np.array(point)
    axis_start = np.array(axis_start)

    # Translate the point to the origin, rotate, and translate back
    rotated_point = np.dot(rotation_matrix, point - axis_start) + axis_start

    return rotated_point.tolist()


def is_point_in_any_cube(cubes, point):
    """
    Check if the point is inside any of the given cubes.
    :param cubes: List of Cube objects.
    :param point: Tuple (x, y, z) representing a point in 3D space.
    :return: Boolean indicating whether the point is in any of the cubes.
    """
    return any(cube.contains_point(point) for cube in cubes)
