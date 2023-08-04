import RPi.GPIO as GPIO
from time import sleep
from multiprocessing import Process

CLOCKWISE = GPIO.HIGH
COUNTERCLOCKWISE = GPIO.LOW
GPIO.setmode(GPIO.BCM)

microstepping_dict = {
    1: (GPIO.LOW, GPIO.LOW, GPIO.LOW),
    2: (GPIO.HIGH, GPIO.LOW, GPIO.LOW),
    3: (GPIO.LOW, GPIO.HIGH, GPIO.LOW),
    4: (GPIO.HIGH, GPIO.HIGH, GPIO.LOW),
    5: (GPIO.HIGH, GPIO.HIGH, GPIO.HIGH),
}


class StepperMotor:
    def __init__(
        self,
        direction_pin,
        step_pin,
        ms_pins,
        enable_pin,
        max_speed,
        starting_speed,
        acceleration,
        microstepping=1,
    ):
        """
        Makes a stepper motor object that can be used to control a stepper motor
        :param direction_pin: What GPIO pin is the direction pin connected to?
        :param step_pin: What GPIO pin is the step pin connected to?
        :param ms_pins: What GPIO pins are the microstepping pins connected to?
        :param enable_pin: What GPIO pin is the enable pin connected to?
        :param max_speed: The maximum speed of the motor in steps per second
        :param starting_speed: The starting speed of the motor in steps per second
        :param acceleration: The acceleration of the motor in steps per second^2
        :param microstepping: The microstepping of the motor (1: full step, 2: half step, 3: quarter step, ..., 5: 1/16 step)
        """
        self.microstepping = microstepping
        self.ms_pins = ms_pins
        self.direction_pin = direction_pin
        self.step_pin = step_pin
        self.steps = 0
        self.clockwise = True
        self.step_speed = starting_speed
        self.position = 0
        self.MAX_SPEED = max_speed
        self.STARTING_SPEED = starting_speed
        self.acceleration = acceleration
        self.motor_process = None
        self.enable_pin = enable_pin

        # Set up GPIO pins as outputs
        GPIO.setup(self.direction_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.ms_pins[0], GPIO.OUT)
        GPIO.setup(self.ms_pins[1], GPIO.OUT)
        GPIO.setup(self.ms_pins[2], GPIO.OUT)
        GPIO.setup(self.enable_pin, GPIO.OUT)

    def move(self, steps, clockwise, debug=False, blocking=False):
        """
        Moves the motor a certain number of steps
        :param steps: How many steps to move the motor
        :param clockwise: Whether to move the motor clockwise or counterclockwise
        :param debug: Whether to print debug information
        :param blocking: Whether to block the main thread while the motor is moving
        :return:
        """
        microstepping_values = microstepping_dict[self.microstepping]
        GPIO.output(self.ms_pins[0], microstepping_values[0])
        GPIO.output(self.ms_pins[1], microstepping_values[1])
        GPIO.output(self.ms_pins[2], microstepping_values[2])

        if blocking:
            self._move_process(steps, clockwise, debug)
        else:
            self.motor_process = Process(
                target=self._move_process, args=(steps, clockwise, debug)
            )
            self.motor_process.start()

    def enable(self):
        """
        Enables the motor
        """
        GPIO.output(self.enable_pin, GPIO.LOW)

    def disable(self):
        """
        Disables the motor
        """
        GPIO.output(self.enable_pin, GPIO.HIGH)

    def _move_process(self, steps, clockwise, debug):
        """
        !!!UTIL FUNCTION DO NOT CALL!!!
        """
        self.steps = steps
        self.clockwise = clockwise
        if self.clockwise:
            GPIO.output(self.direction_pin, CLOCKWISE)
        else:
            GPIO.output(self.direction_pin, COUNTERCLOCKWISE)

        for step in range(self.steps):
            if (
                step < (self.MAX_SPEED / self.acceleration) - 1
                and self.step_speed < self.MAX_SPEED
            ):
                self.step_speed += self.acceleration
            elif (
                step
                > (
                    self.steps
                    - ((self.MAX_SPEED - self.STARTING_SPEED) / self.acceleration)
                )
                - 1
                and self.step_speed > self.STARTING_SPEED
            ):
                self.step_speed -= self.acceleration
            if self.step_speed == 0:
                self.step_speed = 0.0001
            GPIO.output(self.step_pin, GPIO.HIGH)
            sleep(1 / self.step_speed)
            GPIO.output(self.step_pin, GPIO.LOW)
            sleep(1 / self.step_speed)
            if self.step_speed == 0.0001:
                self.step_speed = 0
            if self.clockwise:
                self.position -= 1
            else:
                self.position += 1
            if debug:
                print(
                    f"Step: {step + 1} Speed: {self.step_speed} Position: {self.position} Clockwise: {self.clockwise}"
                )
