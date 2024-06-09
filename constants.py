from MathFunctions.geometry import Cube, Vector3


class CanIds:
    base_nodeid = 0
    shoulder_nodeid = 1
    elbow_nodeid = 2


class Vectors:
    m_base_vector = Vector3([0, 0, 0], [0, 0, 225.76])

    m_upper_arm_vector_one = Vector3(m_base_vector.get_end_point(), [0, 0, 379.64695])

    m_upper_arm_vector_two = Vector3(
        m_upper_arm_vector_one.get_end_point(), [29.42254, 0, 59.39554]
    )

    m_projected_upper_arm_vector = m_upper_arm_vector_one + m_upper_arm_vector_two

    m_fore_arm_vector = Vector3(
        m_upper_arm_vector_two.get_end_point(), [0, 0, 389.09462]
    )

    m_end_effector_vector = Vector3(m_fore_arm_vector.get_end_point(), [0, 0, 130])


class OdriveSpeeds:
    max_speed = 5 * 2  # rps
    max_accel = 0.6 * 2  # rps/s
    max_decel = 0.6 * 2  # rps/s


class SocketConstants:
    host = "arm.local"
    port = 50135
    password = "ScytheIndustries"
    function_check = True


class StepperConstants:
    degrees_per_step = 1.8  # direct degrees per step
    trapezoidal_step = (
        0.01  # time between speed updates in trapezoidal profile (seconds)
    )
    microstepping = 16  # microstepping of the stepper motor (8, 16, 32, 64)

    # -----------
    # Speed Curve
    # -----------

    max_speed = 360
    acceleration = 240
    starting_speed = 0


class NetworkTablesConstants:
    ip = "arm.local"
    refresh_rate = 60  # hz
    heart_beat_timeout = 10  # seconds


restricted_areas = [
    Cube((125, -1000, 0), (-450, 800, -715)),
    Cube((-450, -1000, 500), (-800, 1000, -715)),
    Cube((-450, 800, 0), (230, 1280, 750)),
]
# encode restricted areas into one string
restricted_areas_encoded = []
for area in restricted_areas:
    restricted_areas_encoded.append(area.encode())


# ANSI escape codes for colors
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
