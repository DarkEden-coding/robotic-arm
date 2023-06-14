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


def rotate_stepper_motor(angle, direction, acceleration):
    steps_per_revolution = 200  # Number of steps per full revolution
    total_steps = int(
        angle / 360 * steps_per_revolution
    )  # Calculate total steps based on desired angle

    # Set the motor direction
    GPIO.output(direction_pin, direction)

    # Calculate acceleration and deceleration parameters
    acceleration_steps = int(
        total_steps / 2
    )  # Number of steps for acceleration and deceleration
    acceleration = abs(acceleration)  # Ensure positive acceleration value

    # Calculate the delay at maximum speed
    max_speed_delay = (1 / (acceleration * acceleration_steps)) ** 0.5

    # Generate step pulses to rotate the motor
    current_delay = max_speed_delay
    for step in range(total_steps):
        GPIO.output(step_pin, GPIO.HIGH)
        sleep(current_delay)
        GPIO.output(step_pin, GPIO.LOW)
        sleep(current_delay)

        # Adjust the delay for acceleration and deceleration
        if step < acceleration_steps:
            current_delay -= (2 * acceleration * current_delay) ** 0.5
        elif step >= total_steps - acceleration_steps:
            current_delay += (2 * acceleration * current_delay) ** 0.5

        # Ensure the delay does not go below the maximum speed delay
        current_delay = max(current_delay, max_speed_delay)


# Repeat the process 10 times
for _ in range(10):
    # Rotate 360 degrees counterclockwise with acceleration of 1000 steps per second squared
    print("Rotating 360 degrees counterclockwise")
    rotate_stepper_motor(360, COUNTERCLOCKWISE, 1)
    sleep(1)  # Wait for 1 second between rotations
    # Rotate 360 degrees clockwise with acceleration of -1000 steps per second squared (deceleration)
    print("Rotating 360 degrees clockwise")
    rotate_stepper_motor(360, CLOCKWISE, -1)
    sleep(1)  # Wait for 1 second between rotations

# Clean up GPIO
GPIO.cleanup()
