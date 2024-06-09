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


def rotate_array_around_point(x, y, z, array, point):
    # rotate the array around the point
    array = array - point

    # convert angles to radians
    x = np.radians(x)
    y = np.radians(y)
    z = np.radians(z)

    # rotation matrix
    rotation_matrix = np.array(
        [
            [
                np.cos(y) * np.cos(z),
                np.cos(z) * np.sin(x) * np.sin(y) - np.cos(x) * np.sin(z),
                np.sin(x) * np.sin(z) + np.cos(x) * np.cos(z) * np.sin(y),
            ],
            [
                np.cos(y) * np.sin(z),
                np.cos(x) * np.cos(z) + np.sin(x) * np.sin(y) * np.sin(z),
                np.cos(x) * np.sin(y) * np.sin(z) - np.cos(z) * np.sin(x),
            ],
            [-np.sin(y), np.cos(y) * np.sin(x), np.cos(x) * np.cos(y)],
        ]
    )

    array = np.dot(rotation_matrix, array)

    return array + point


class Vector3:
    def __init__(self, start, component):
        self.start = np.array(start)
        self.component = np.array(component)
        self.end = self.start + self.component
        self.orientation = np.eye(3)  # Initial orientation is the identity matrix

    def get_end_point(self):
        return self.end

    def get_start_point(self):
        return self.start

    def get_component(self):
        return self.component

    def move_absolute(self, point):
        self.start = np.array(point)
        self.end = self.start + self.component

    def rotate_around_point(self, x, y, z, point):
        point = np.array(point)

        # Rotate the start point around the given point
        self.start = rotate_array_around_point(x, y, z, self.start, point)

        # Rotate the end point around the given point
        self.end = rotate_array_around_point(x, y, z, self.end, point)

        # Update the component based on the new start and end points
        self.component = self.end - self.start

    def rotate_locally(self, x, y, z):
        # Local rotation matrices
        rx = np.array(
            [[1, 0, 0], [0, np.cos(x), -np.sin(x)], [0, np.sin(x), np.cos(x)]]
        )
        ry = np.array(
            [[np.cos(y), 0, np.sin(y)], [0, 1, 0], [-np.sin(y), 0, np.cos(y)]]
        )
        rz = np.array(
            [[np.cos(z), -np.sin(z), 0], [np.sin(z), np.cos(z), 0], [0, 0, 1]]
        )

        # Combine the local rotations
        local_rotation = np.dot(np.dot(rz, ry), rx)

        # Update the orientation matrix with the new local rotation
        self.orientation = np.dot(self.orientation, local_rotation)

        # Rotate the component using the updated orientation matrix
        self.component = np.dot(self.orientation, self.component)

        # Update the end point
        self.end = self.start + self.component

    def __len__(self):
        return np.linalg.norm(self.component)

    def __add__(self, other):
        return Vector3(self.start, self.component + other.component)

    def __sub__(self, other):
        return Vector3(self.start, self.component - other.component)

    def __copy__(self):
        return Vector3(self.start, self.component)


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


def is_point_in_any_cube(cubes, point):
    """
    Check if the point is inside any of the given cubes.
    :param cubes: List of Cube objects.
    :param point: Tuple (x, y, z) representing a point in 3D space.
    :return: Boolean indicating whether the point is in any of the cubes.
    """
    return any(cube.contains_point(point) for cube in cubes)
