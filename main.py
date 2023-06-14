import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

direction_pin = 14  # Direction (DIR) GPIO Pin
step_pin = 15  # Step GPIO Pin

# Set up GPIO pins as outputs
GPIO.setup(direction_pin, GPIO.OUT)
GPIO.setup(step_pin, GPIO.OUT)

# Define motor rotation constants
CLOCKWISE = GPIO.HIGH
COUNTERCLOCKWISE = GPIO.LOW
MAX_SPEED = 100  # 0.5 ms
STARTING_SPEED = 10
ACCELERATION = 2


class StepperMotor:
    def __init__(self, direction_pin, step_pin):
        self.direction_pin = direction_pin
        self.step_pin = step_pin
        self.steps = 0
        self.clockwise = True
        self.acceleration = 0
        self.step_speed = STARTING_SPEED
        self.position = 0

    def move(self, steps, clockwise, acceleration):
        if clockwise:
            GPIO.output(self.direction_pin, CLOCKWISE)
        else:
            GPIO.output(self.direction_pin, COUNTERCLOCKWISE)
        self.steps = steps
        self.clockwise = clockwise
        self.acceleration = acceleration

        for step in range(self.steps):
            if step < MAX_SPEED / ACCELERATION and self.step_speed < MAX_SPEED:
                self.step_speed += self.acceleration
            elif step > (self.step_speed - STARTING_SPEED) / ACCELERATION and self.step_speed > STARTING_SPEED:
                self.step_speed -= self.acceleration
            GPIO.output(self.step_pin, GPIO.HIGH)
            sleep(1 / self.step_speed)
            GPIO.output(self.step_pin, GPIO.LOW)
            sleep(1 / self.step_speed)
            if clockwise:
                self.position -= 1
            else:
                self.position += 1
            print(
                f"Step: {step + 1} Speed: {self.step_speed} Position: {self.position}"
            )


motor = StepperMotor(direction_pin, step_pin)

# Repeat the process 10 times
for _ in range(10):
    # Rotate 360 degrees counterclockwise with acceleration of 1000 steps per second squared
    print("Rotating 360 degrees counterclockwise")
    motor.move(steps=200, clockwise=False, acceleration=ACCELERATION)
    sleep(1)  # Wait for 1 second between rotations
    # Rotate 360 degrees clockwise with acceleration of -1000 steps per second squared (deceleration)
    print("Rotating 360 degrees clockwise")
    motor.move(steps=200, clockwise=True, acceleration=ACCELERATION)
    sleep(1)  # Wait for 1 second between rotations

# Clean up GPIO
GPIO.cleanup()
