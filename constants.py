from MathFunctions.geometry import Cube


class CanIds:
    base_nodeid = 0
    shoulder_nodeid = 1
    elbow_nodeid = 2


class Lengths:
    arm_1_length = 378
    arm_2_length = 546.77
    end_effector_length = (
        134 - 4.37968
    )  # this is to the very center of the rotating bar


class Offsets:
    shoulder_y_offset = -30.06119
    height_to_shoulder = 216.41039
    position_error_offsets = (0, 0, 0)


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

    max_speed_stepper = 360
    acceleration_stepper = 240
    starting_speed_stepper = 0


class NetworkTablesConstants:
    ip = "arm.local"
    port = 1735


restricted_areas = [
    Cube((125, -1000, 0), (-450, 800, -715)),
    Cube((-450, -1000, 500), (-800, 1000, -715)),
    Cube((-450, 800, 0), (230, 1280, 750)),
]

return_map = {
    "setup": False,
    "move": False,
    "shutdown": False,
    "enable_motors": False,
    "disable_motors": False,
    "set_percent_speed": False,
    "emergency_stop": False,
    "get_position": True,
}
