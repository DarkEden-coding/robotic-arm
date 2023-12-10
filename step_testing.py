import RPi.GPIO as GPIO
import time

# Pin Definitions
dir_pin = 3  # Direction GPIO Pin
step_pin = 5  # Step GPIO Pin

# Setup
GPIO.setmode(GPIO.BOARD)  # Use physical GPIO numbering
GPIO.setup(dir_pin, GPIO.OUT)
GPIO.setup(step_pin, GPIO.OUT)

# Set the rotation direction
direction = True  # True for clockwise, False for counterclockwise
GPIO.output(dir_pin, direction)

# Drive the motor
steps = 200  # Change this to the number of steps you want
delay = 0.01  # Delay between each step

for i in range(steps):
    print(i)
    GPIO.output(step_pin, GPIO.HIGH)
    time.sleep(delay)
    GPIO.output(step_pin, GPIO.LOW)
    time.sleep(delay)

# Cleanup
GPIO.cleanup()
