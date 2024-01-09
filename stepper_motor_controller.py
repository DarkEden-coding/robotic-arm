import RPi.GPIO as GPIO
import time
import math
from constants import trapezoidal_step, degrees_per_step
from threading import Thread

GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering


def cleanup():
    """
    Cleanup the GPIO pins
    :return:
    """
    GPIO.cleanup()


def get_movement_lengths(max_speed, accel, initial_speed, target_distance):
    """
    Get the length of the acceleration and linear movement
    :param max_speed: the maximum speed of the motor in rotations per second
    :param accel: the acceleration of the motor in rotations per second per second
    :param initial_speed: the initial speed of the motor in rotations per second
    :param target_distance: the target distance in degrees
    :return:
    """
    accel_time = max_speed / accel
    dist_over_accel = (initial_speed * accel_time) + (1 / 2 * accel * (accel_time ** 2))
    linear_movement_length = target_distance - (2 * dist_over_accel)

    return dist_over_accel, linear_movement_length


def total_movement_time(acceleration, max_speed, linear_movement_length, target):
    """
    Get the total movement time
    :param acceleration: the acceleration of the motor in rotations per second per second
    :param max_speed: the maximum speed of the motor in rotations per second
    :param linear_movement_length: the length of the linear movement
    :param target: the target distance
    :return:
    """
    if linear_movement_length > 0:
        acceleration_time = max_speed / acceleration
        linear_movement_time = linear_movement_length / max_speed

        accel_and_linear_movement_time = (acceleration_time * 2) + linear_movement_time
        return accel_and_linear_movement_time
    else:
        final_velocity = math.sqrt(2 * acceleration * (target / 2))
        acceleration_time = final_velocity / acceleration
        return 2 * acceleration_time


def get_speed(
        current_speed,
        max_speed,
        acceleration,
        dist_over_accel,
        linear_movement_length,
        position,
        target_distance,
        stage=0,
):
    """
    Get the speed of the motor
    :param current_speed: the current speed of the object in units per second
    :param max_speed: the maximum speed of the object in units per second
    :param acceleration: the acceleration of the object in units per second per second
    :param dist_over_accel: the distance over the acceleration
    :param linear_movement_length: the length of the linear movement
    :param position: the current position of the object
    :param target_distance: the target distance of the object
    :param stage: the stage of the movement
    :return:
    """
    if linear_movement_length <= 0:
        if position < (target_distance / 2):
            current_speed += acceleration * trapezoidal_step
        else:
            current_speed -= acceleration * trapezoidal_step
        return current_speed, 0
    else:
        if current_speed < max_speed and stage == 0:
            current_speed = float(current_speed) + float(acceleration * trapezoidal_step)
        elif position < target_distance - dist_over_accel and (
                stage == 0 or stage == 1
        ):
            stage = 1
            current_speed = max_speed
            pass
        elif stage == 1 or stage == 2:
            current_speed -= acceleration * trapezoidal_step
            stage = 2

        return current_speed, stage


microstep_map = {
    8: (GPIO.LOW, GPIO.LOW),
    16: (GPIO.HIGH, GPIO.HIGH),
    32: (GPIO.HIGH, GPIO.LOW),
    64: (GPIO.LOW, GPIO.HIGH),
}


class StepperMotorController:
    def __init__(
            self,
            enable_pin: int,
            dir_pin: int,
            step_pin: int,
            micro_step_pins: tuple,
            acceleration: float,
            max_speed: float,
            starting_speed: float,
            gear_ratio: float,
    ):
        """
        Stepper motor controller class
        :param enable_pin: the enable pin of the stepper motor
        :param dir_pin: the direction pin of the stepper motor
        :param step_pin: the step pin of the stepper motor
        :param micro_step_pins: the micro step pins of the stepper motor (tuple)
        :param acceleration: the acceleration of the stepper motor in rotations per second per second
        :param max_speed: the maximum speed of the stepper motor in rotations per second
        :param starting_speed: the starting speed of the stepper motor in rotations per second
        :param gear_ratio: the gear ratio of the stepper motor in a decimal form
        """
        self.enable_pin = enable_pin
        self.dir_pin = dir_pin
        self.step_pin = step_pin
        self.micro_step_pins = micro_step_pins
        self.acceleration = acceleration
        self.max_speed = max_speed
        self.gear_ratio = gear_ratio
        self.starting_speed = starting_speed

        self.position_data = []
        self.speed_data = []

        self.enabled = False
        self.micro_steps = 8
        self.speed = 0
        self.step_position = 0

        self.process = None

        GPIO.setup(self.enable_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.micro_step_pins, GPIO.OUT)

    def enable_motor(self):
        """
        Enable the stepper motor
        :return:
        """
        GPIO.output(self.enable_pin, GPIO.LOW)
        self.enabled = True

    def disable_motor(self):
        """
        Disable the stepper motor
        :return:
        """
        GPIO.output(self.enable_pin, GPIO.HIGH)
        self.enabled = False

    def set_micro_steps(self, micro_steps):
        """
        Set the micro steps of the stepper motor
        :param micro_steps: the micro steps of the stepper motor
        :return:
        """
        print(f"setting pins to {microstep_map[micro_steps]}")
        GPIO.output(self.micro_step_pins, microstep_map[micro_steps])
        self.micro_steps = micro_steps

    def _move_to_angle(self, target_angle):
        GPIO.setmode(GPIO.BCM)

        fixed_degrees_per_step = degrees_per_step / self.micro_steps
        steps = target_angle / fixed_degrees_per_step

        steps = steps * self.gear_ratio

        direction = GPIO.HIGH if steps > 0 else GPIO.LOW
        GPIO.output(self.dir_pin, direction)

        steps = abs(steps)

        max_speed_steps = self.max_speed / fixed_degrees_per_step
        acceleration_steps = self.acceleration / fixed_degrees_per_step
        starting_speed_steps = self.starting_speed / fixed_degrees_per_step

        dist_over_accel, linear_movement_length = get_movement_lengths(
            max_speed_steps, acceleration_steps, starting_speed_steps, steps
        )

        time_estimate = total_movement_time(
            acceleration_steps, max_speed_steps, linear_movement_length, steps
        )

        stage = 0
        self.speed = starting_speed_steps
        self.step_position = 0
        while True:
            self.speed, stage = get_speed(
                self.speed,
                max_speed_steps,
                acceleration_steps,
                dist_over_accel,
                linear_movement_length,
                self.step_position,
                steps,
                stage,
            )

            if self.speed * trapezoidal_step <= 0:
                break
            else:
                delay = (trapezoidal_step / (self.speed * trapezoidal_step)) / 2

            # print(f"steps: {self.speed * trapezoidal_step}")

            for _ in range(int(self.speed * trapezoidal_step)):
                GPIO.output(self.step_pin, GPIO.HIGH)
                time.sleep(delay)
                GPIO.output(self.step_pin, GPIO.LOW)
                time.sleep(delay)
                self.step_position += 1

            if self.step_position >= steps:
                break

    def wait_until_stopped(self):
        """
        Wait until the stepper motor is stopped
        :return:
        """
        self.process.join()

    def move_to_angle(self, target_angle, threaded=False):
        """
        Move the stepper motor to a specific angle
        :param target_angle: the target angle in degrees
        :param threaded: whether or not to thread the movement
        :return:
        """
        if threaded:
            self.process = Thread(target=self._move_to_angle, args=(target_angle,))
            self.process.start()
        else:
            self._move_to_angle(target_angle)

    def force_move_steps(self, steps):
        """
        Force the stepper motor to move a specific number of steps, not recommended for use
        :param steps: the number of steps to move
        :return:
        """
        direction = GPIO.HIGH if steps > 0 else GPIO.LOW
        GPIO.output(self.dir_pin, direction)

        steps = abs(steps)

        for step in range(int(steps)):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(0.001)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(0.001)
