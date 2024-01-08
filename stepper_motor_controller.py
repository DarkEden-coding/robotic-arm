import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering

degrees_per_step = 1.8


def cleanup():
    """
    Cleanup the GPIO pins
    :return:
    """
    GPIO.cleanup()


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
        :param gear_ratio: the gear ratio of the stepper motor in a decimal form
        """
        self.enable_pin = enable_pin
        self.dir_pin = dir_pin
        self.step_pin = step_pin
        self.micro_step_pins = micro_step_pins
        self.acceleration = acceleration
        self.max_speed = max_speed
        self.gear_ratio = gear_ratio

        self.enabled = False
        self.angle = 0
        self.micro_steps = 8

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

    def move_to_angle(self, target_angle, delay):
        """
        Move the stepper motor to a specific angle
        :param delay:
        :param target_angle: the target angle in degrees
        :return:
        """
        fixed_degrees_per_step = 1.8 / self.micro_steps
        steps = target_angle / fixed_degrees_per_step

        steps = steps * self.gear_ratio
        delay = delay / self.gear_ratio

        print(f"Steps: {steps}")
        print(f"Delay: {delay}")

        direction = GPIO.HIGH if steps > 0 else GPIO.LOW
        GPIO.output(self.dir_pin, direction)

        # Move the motor the specified number of steps at the given speed
        for _ in range(abs(steps)):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(delay)
