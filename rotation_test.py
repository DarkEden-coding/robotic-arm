import RPi.GPIO as GPIO
import time

# GPIO pin connected to the PWM output of the encoder
PWM_GPIO_PIN = 2  # Change this to the correct GPIO pin number

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_GPIO_PIN, GPIO.IN)

# Initialize variables
pulse_start_time = None
pulse_end_time = None
last_pulse_duration = None

# Callback function to be called when a rising edge is detected
def rising_edge_callback(channel):
    global pulse_start_time
    pulse_start_time = time.time()

# Callback function to be called when a falling edge is detected
def falling_edge_callback(channel):
    global pulse_end_time, last_pulse_duration
    pulse_end_time = time.time()
    if pulse_start_time is not None:
        last_pulse_duration = pulse_end_time - pulse_start_time

# Add event detections
GPIO.add_event_detect(PWM_GPIO_PIN, GPIO.RISING, callback=rising_edge_callback)
GPIO.add_event_detect(PWM_GPIO_PIN, GPIO.FALLING, callback=falling_edge_callback)

try:
    while True:
        if last_pulse_duration is not None:
            # Calculate rotations based on pulse duration
            # The calculation will depend on the specifics of your encoder
            rotations = last_pulse_duration  # Placeholder calculation
            print("Absolute Rotations: {}".format(rotations))
            last_pulse_duration = None
        time.sleep(0.1)  # Reduce CPU usage with a sleep

except KeyboardInterrupt:
    print("Read interrupted by user")

except Exception as e:
    print("An error occurred: {}".format(e))

finally:
    GPIO.cleanup()
