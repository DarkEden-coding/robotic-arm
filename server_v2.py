from MotorControllerLibs.CANControlledMotors.odrivecontroller import OdriveController
from MathFunctions.inverse_kinematics import (
    get_angles,
    get_trajectory,
    get_pos_from_angles,
    get_wrist_position,
    get_wrist_angles,
)
from MotorControllerLibs.stepper_motor_controller import StepperMotorController
from constants import CanIds, StepperConstants, NetworkTablesConstants, Colors
from networktables import NetworkTables
from time import sleep, time
from MathFunctions.geometry import decode_string_to_cube


class Arm:
    def __init__(self, restricted_areas):
        """
        Arm object that contains all the motors and functions to control the arm
        :param restricted_areas: the restricted areas of the arm
        """
        self.base_controller = OdriveController(CanIds.base_nodeid, motor_reversed=True)
        self.shoulder_controller = OdriveController(
            CanIds.shoulder_nodeid, gear_ratio=125
        )
        self.elbow_controller = OdriveController(
            CanIds.elbow_nodeid, motor_reversed=True
        )

        self.yaw_motor = StepperMotorController(
            enable_pin=2,
            dir_pin=27,
            step_pin=17,
            micro_step_pins=(3, 4),
            acceleration=StepperConstants.acceleration,
            max_speed=StepperConstants.max_speed,
            starting_speed=StepperConstants.starting_speed,
            gear_ratio=4,
        )

        self.pitch_motor = StepperMotorController(
            enable_pin=0,
            dir_pin=12,
            step_pin=1,
            micro_step_pins=(5, 6),
            acceleration=StepperConstants.acceleration,
            max_speed=StepperConstants.max_speed,
            starting_speed=StepperConstants.starting_speed,
            gear_ratio=2,
        )

        self.restricted_areas = restricted_areas

        self.moving = False

        self.motors_enabled = False

        self.percentage_speed = 100

    def move(self, pos, rotations, wait_for_move=True):
        """
        Move the arm to a position
        :param pos: the target position
        :param rotations: the target rotations of the end effector, (x-axis, y-axis)
        :param wait_for_move: whether to wait for the arm to finish moving
        :return:
        """
        wait_for_move = bool(wait_for_move)

        angles = get_angles(pos[0], pos[1], pos[2], self.restricted_areas)
        base_offset, shoulder_offset, elbow_offset = get_trajectory(
            *angles,
            self.base_controller,
            self.shoulder_controller,
            self.elbow_controller,
        )

        target_wrist_pos = get_wrist_position(pos, rotations)
        wrist_angles = get_wrist_angles(angles, pos, target_wrist_pos)

        self.moving = True

        self.yaw_motor.move_to_angle(wrist_angles[0])
        self.pitch_motor.move_to_angle(wrist_angles[1])

        self.base_controller.move_to_angle(angles[0], base_offset)
        self.shoulder_controller.move_to_angle(angles[1], shoulder_offset)
        self.elbow_controller.move_to_angle(angles[2], elbow_offset)

        if wait_for_move:
            self.base_controller.wait_for_move()
            self.shoulder_controller.wait_for_move()
            self.elbow_controller.wait_for_move()
            self.yaw_motor.wait_for_move()
            self.pitch_motor.wait_for_move()

            self.moving = False

    def check_moving(self):
        """
        Check if the arm is moving
        :return: boolean
        """
        if self.moving:
            return True
        else:
            if any(
                (
                    self.base_controller.moving,
                    self.shoulder_controller.moving,
                    self.elbow_controller.moving,
                    self.yaw_motor.moving,
                    self.pitch_motor.moving,
                )
            ):
                return True
            else:
                return False

    def shutdown(self):
        """
        Shutdown the arm
        :return:
        """
        # move to home position
        self.base_controller.move_to_angle(0)
        self.shoulder_controller.move_to_angle(0)
        self.elbow_controller.move_to_angle(0)

        self.yaw_motor.move_to_angle(0)
        self.pitch_motor.move_to_angle(0)

        self.base_controller.wait_for_move()
        self.shoulder_controller.wait_for_move()
        self.elbow_controller.wait_for_move()
        self.yaw_motor.wait_for_move()
        self.pitch_motor.wait_for_move()

        self.disable_motors()

    def enable_motors(self):
        """
        Enable the motors
        :return:
        """
        if not self.motors_enabled:
            self.base_controller.enable_motor()
            self.shoulder_controller.enable_motor()
            self.elbow_controller.enable_motor()

            self.yaw_motor.enable_motor()
            self.pitch_motor.enable_motor()

            self.motors_enabled = True

    def disable_motors(self):
        """
        Disable the motors
        :return:
        """
        if self.motors_enabled:
            self.base_controller.disable_motor()
            self.shoulder_controller.disable_motor()
            self.elbow_controller.disable_motor()

            self.yaw_motor.disable_motor()
            self.pitch_motor.disable_motor()

    def set_percent_speed(self, percent):
        """
        Set the percent speed of the arm
        :param percent: float
        :return:
        """
        if float(percent) != self.percentage_speed:
            self.percentage_speed = float(percent)
            self.base_controller.set_percent_traj(self.percentage_speed)
            self.shoulder_controller.set_percent_traj(self.percentage_speed)
            self.elbow_controller.set_percent_traj(self.percentage_speed)

    def emergency_stop(self):
        """
        Emergency stop the arm, !!!WILL NEED RESET AFTER USE!!!
        :return:
        """
        self.base_controller.emergency_stop()
        self.shoulder_controller.emergency_stop()
        self.elbow_controller.emergency_stop()

        self.yaw_motor.emergency_stop()
        self.pitch_motor.emergency_stop()

    def get_position(self):
        """
        Get the estimated position of the arm
        :return: tuple
        """
        return get_pos_from_angles(
            (
                self.base_controller.get_angle(),
                self.shoulder_controller.get_angle(),
                self.elbow_controller.get_angle(),
            ),
            (
                self.yaw_motor.get_angle(),
                self.pitch_motor.get_angle(),
            ),
        )


def main():
    print(Colors.GREEN + "Starting server..." + Colors.RESET)
    print(
        Colors.YELLOW
        + f"Connecting Network Tables to: {NetworkTablesConstants.ip}"
        + Colors.RESET
    )

    NetworkTables.initialize()
    data_table = NetworkTables.getTable("RoboticArmData")

    print(Colors.GREEN + "Connected to Network Tables" + Colors.RESET)
    print(Colors.YELLOW + "Waiting for setup..." + Colors.RESET)

    while data_table.getBoolean("setup", False) is False:
        sleep(0.1)

    restricted_areas = data_table.getStringArray("restricted_areas", [])

    restricted_areas_decoded = []
    for area in restricted_areas:
        restricted_areas_decoded.append(decode_string_to_cube(area))

    arm_object = Arm(restricted_areas_decoded)

    print(Colors.GREEN + "Setup complete" + Colors.RESET)

    while True:
        frame_start = time()

        if data_table.getBoolean("shutdown", False):
            print(Colors.RED + "Shutting down..." + Colors.RESET)
            arm_object.shutdown()
            print(Colors.YELLOW + "Shutdown complete" + Colors.RESET)
            break

        if data_table.getBoolean("emergency_stop", False):
            print(Colors.RED + "Emergency stopping..." + Colors.RESET)
            arm_object.emergency_stop()
            print(Colors.YELLOW + "Emergency stop complete" + Colors.RESET)
            break

        if data_table.getBoolean("enable_motors", False):
            arm_object.enable_motors()
            print(Colors.GREEN + "Motors enabled" + Colors.RESET)

        if not data_table.getBoolean("enable_motors", False):
            arm_object.disable_motors()
            print(Colors.YELLOW + "Motors disabled" + Colors.RESET)

        if data_table.getBoolean("request_move", False):
            arm_object.move(
                data_table.getValue("target_position", (0, 0, 0)),
                data_table.getValue("target_rotations", (0, 0)),
                wait_for_move=True,
            )
            print(
                Colors.GREEN
                + f"""Moving to position: {data_table.getValue("target_position", (0, 0, 0))}"""
                + Colors.RESET
            )

            data_table.putBoolean("request_move", False)

        data_table.putBoolean("moving", arm_object.check_moving())
        data_table.putValue("current_position", arm_object.get_position())

        arm_object.set_percent_speed(data_table.getNumber("percentage_speed", 1))

        frame_end = time()
        frame_time = frame_end - frame_start
        sleep_time = 1 / NetworkTablesConstants.refresh_rate - frame_time

        if sleep_time > 0:
            sleep(sleep_time)
            data_table.putNumber("server_refresh_rate", 1 / (frame_time + sleep_time))
        else:
            data_table.putNumber("server_refresh_rate", 1 / frame_time)


if __name__ == "__main__":
    main()
