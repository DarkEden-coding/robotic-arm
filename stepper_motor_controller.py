import RPi.GPIO as GPIO
import time
import numpy as np

GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering

degrees_per_step = 1.8


def cleanup():
    """
    Cleanup the GPIO pins
    :return:
    """
    GPIO.cleanup()


def get_movement_lengths(max_speed, accel, initial_speed, target_distance):
    accel_time = max_speed / accel
    dist_over_accel = (initial_speed * accel_time) + (1 / 2 * accel * (accel_time ** 2))
    linear_movement_length = target_distance - (2 * dist_over_accel)

    return dist_over_accel, linear_movement_length


def total_movement_time(acceleration, max_speed, linear_movement_length, target):
    if linear_movement_length > 0:
        acceleration_time = max_speed / acceleration
        linear_movement_time = linear_movement_length / max_speed

        accel_and_linear_movement_time = (acceleration_time * 2) + linear_movement_time
        return accel_and_linear_movement_time
    else:
        final_velocity = np.sqrt(2 * acceleration * (target / 2))
        acceleration_time = final_velocity / acceleration
        return 2 * acceleration_time


def get_speed(current_speed, max_speed, acceleration, dist_over_accel, linear_movement_length, position, target_distance,
              stage=0):
    if linear_movement_length < 0:
        if position < (target_distance / 2) + .01:
            current_speed += acceleration * .001
        else:
            current_speed -= acceleration * .001
        return current_speed, 0
    else:
        if current_speed < max_speed and stage == 0:
            current_speed += acceleration * .001
        elif position < target_distance - dist_over_accel and (stage == 0 or stage == 1):
            stage = 1
            current_speed = max_speed
            pass
        elif stage == 1 or stage == 2:
            current_speed -= acceleration * .001
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

        self.enabled = False
        self.angle = 0
        self.micro_steps = 8
        self.speed = 0

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

    def move_to_angle(self, target_angle):
        """
        Move the stepper motor to a specific angle
        :param target_angle: the target angle in degrees
        :return:
        """
        fixed_degrees_per_step = 1.8 / self.micro_steps
        steps = target_angle / fixed_degrees_per_step

        steps = steps * self.gear_ratio

        print(f"Steps: {steps}")

        direction = GPIO.HIGH if steps > 0 else GPIO.LOW
        GPIO.output(self.dir_pin, direction)

        movement_step_lengths = get_movement_lengths(
            self.max_speed, self.acceleration, self.starting_speed, int(abs(steps))
        )
        total_time = total_movement_time(
            self.acceleration,
            self.max_speed,
            movement_step_lengths[1],
            int(abs(steps)),
        )
        print(f"Total time: {total_time}")

        self.speed = self.starting_speed
        # Move the motor the specified number of steps at the given speed
        for step in range(int(abs(steps))):
            self.speed = get_speed(
                self.speed,
                self.max_speed,
                self.acceleration,
                *movement_step_lengths,
                step,
                int(abs(steps)),
            )
            # na
            print(f"Speed: {self.speed}")

            # convert degrees per second to steps per second
            delay = 1 / (self.speed * fixed_degrees_per_step)

            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(delay)

        self.speed = 0
        self.angle = target_angle
