import RPi.GPIO as GPIO
import time

# GPIO pin connected to the PWM output of the encoder
PWM_GPIO_PIN = 18  # Change this to the correct GPIO pin number

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_GPIO_PIN, GPIO.IN)

# Initialize variables
last_edge_time = None
pulse_duration = None

# Callback function to be called when any edge is detected
def edge_callback(channel):
    global last_edge_time, pulse_duration
    current_time = time.time()
    if last_edge_time is not None:
        pulse_duration = current_time - last_edge_time
    last_edge_time = current_time

# Add event detection for both rising and falling edges
GPIO.add_event_detect(PWM_GPIO_PIN, GPIO.BOTH, callback=edge_callback)

try:
    while True:
        if pulse_duration is not None:
            # Calculate rotations based on pulse duration
            # The calculation will depend on the specifics of your encoder
            rotations = pulse_duration  # Placeholder calculation
            print("Pulse Duration: {} seconds".format(pulse_duration))
            pulse_duration = None
        time.sleep(0.1)  # Reduce CPU usage with a sleep

except KeyboardInterrupt:
    print("Read interrupted by user")

except Exception as e:
    print("An error occurred: {}".format(e))

finally:
    GPIO.cleanup()
