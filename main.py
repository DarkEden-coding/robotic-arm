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


def rotate_stepper_motor(angle, direction, delay):
    steps_per_revolution = 200  # Number of steps per full revolution
    total_steps = int(
        angle / 360 * steps_per_revolution
    )  # Calculate total steps based on desired angle

    # Set the motor direction
    GPIO.output(direction_pin, direction)

    # Generate step pulses to rotate the motor
    for _ in range(total_steps):
        GPIO.output(step_pin, GPIO.HIGH)
        sleep(delay)
        GPIO.output(step_pin, GPIO.LOW)
        sleep(delay)


# Repeat the process 10 times
for _ in range(10):
    # Rotate 360 degrees counterclockwise
    print("Rotating 360 degrees counterclockwise")
    rotate_stepper_motor(360, COUNTERCLOCKWISE, 0.05)
    sleep(1)  # Wait for 1 second between rotations
    print("Rotating 360 degrees clockwise")
    rotate_stepper_motor(360, CLOCKWISE, 0.05)
    sleep(1)  # Wait for 1 second between rotations

# Clean up GPIO
GPIO.cleanup()
