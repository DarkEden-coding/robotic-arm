import datetime


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


# Get the current time
current_time = datetime.datetime.now()

# Round the time to the nearest minute
rounded_time = current_time.replace(second=0, microsecond=0)

# Convert the rounded time to a number (you can choose the format)
rounded_number = int(rounded_time.strftime("%Y%m%d%H%M"))


base_nodeid = 0
shoulder_nodeid = 1
elbow_nodeid = 2

arm_1_length = 380
arm_2_length = 445

max_speed = 5  # rps
max_accel = 0.6  # rps/s
max_decel = 0.6  # rps/s

socket_constants = {
    "host": "arm.local",
    "port": rounded_number,
    "password": "ScytheIndustries",
}

restricted_areas = [
    Cube((125, -1000, 0), (-450, 800, -715)),
    Cube((-450, -1000, 500), (-800, 1000, -715)),
    Cube((-450, 800, 0), (230, 1280, 750)),
]
