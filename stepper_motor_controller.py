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
    32: (GPIO.LOW, GPIO.HIGH),
    64: (GPIO.HIGH, GPIO.LOW),
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
    ):
        """
        Stepper motor controller class
        :param enable_pin: the enable pin of the stepper motor
        :param dir_pin: the direction pin of the stepper motor
        :param step_pin: the step pin of the stepper motor
        :param micro_step_pins: the micro step pins of the stepper motor (tuple)
        :param acceleration: the acceleration of the stepper motor in rotations per second per second
        :param max_speed: the maximum speed of the stepper motor in rotations per second
        """
        self.enable_pin = enable_pin
        self.dir_pin = dir_pin
        self.step_pin = step_pin
        self.micro_step_pins = micro_step_pins
        self.acceleration = acceleration
        self.max_speed = max_speed

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

    def move_to_angle(self, target_angle):
        """
        Move the stepper motor to a specific angle
        :param target_angle: the target angle in degrees
        :return:
        """
        # Calculate the number of steps needed to reach the target angle
        target_steps = int(target_angle / degrees_per_step)

        # Calculate the distance to be covered
        distance = abs(target_steps - self.angle)

        # Calculate the acceleration time required to reach max speed
        acceleration_time = self.max_speed / self.acceleration

        # Adjust acceleration based on distance
        adjusted_acceleration = min(
            self.acceleration, 0.5 * distance / acceleration_time
        )

        # Acceleration phase
        current_speed = 0
        while current_speed < self.max_speed:
            self._move_steps(target_steps, current_speed)
            current_speed += adjusted_acceleration

        # Constant speed phase
        self._move_steps(target_steps, self.max_speed)

        # Deceleration phase
        while current_speed > 0:
            self._move_steps(target_steps, current_speed)
            current_speed -= adjusted_acceleration

    def _move_steps(self, target_steps, speed):
        """
        Move the stepper motor a specific number of steps at a given speed
        :param target_steps: the number of steps to move
        :param speed: the speed of the stepper motor in rotations per second
        :return:
        """
        steps_per_rotation = 360 / degrees_per_step

        # Ensure that speed is not zero to avoid division by zero
        if speed == 0:
            return

        delay = 1 / (speed * steps_per_rotation)
        print(f"Delay: {delay}")

        # Set the direction based on the target angle
        direction = GPIO.HIGH if target_steps > 0 else GPIO.LOW
        GPIO.output(self.dir_pin, direction)

        # Move the motor the specified number of steps at the given speed
        for _ in range(abs(target_steps)):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(delay)

    def force_move_steps(self, steps, delay):
        """
        Force the stepper motor to move a specific number of steps
        :param delay: the delay between steps
        :param steps: the number of steps to move
        :return:
        """

        direction = GPIO.HIGH if steps > 0 else GPIO.LOW
        GPIO.output(self.dir_pin, direction)

        # Move the motor the specified number of steps at the given speed
        for _ in range(abs(steps)):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(delay)
