import pigpio
import time

# GPIO pin connected to the PWM output of the encoder
PWM_GPIO_PIN = 2  # Change this to the correct GPIO pin number

# Initialize pigpio
pi = pigpio.pi()

# If the initialization failed
if not pi.connected:
    exit()


# Function to calculate rotations from pulse width
def calculate_rotations(pulse_width):
    # This function will depend on how your specific encoder translates pulse width to rotations.
    # You would need to calibrate this function according to your encoder's specifications.
    rotations = pulse_width  # Placeholder for the actual calculation
    return rotations


try:
    # Start reading the PWM pulses
    while True:
        # Get the pulse width in microseconds
        pulse_width = pi.get_servo_pulsewidth(PWM_GPIO_PIN)

        # Convert the pulse width to absolute rotations
        rotations = calculate_rotations(pulse_width)

        print(f"Absolute Rotations: {rotations}")

        time.sleep(0.1)  # Add a short delay to limit the output frequency

except KeyboardInterrupt:
    print("Read interrupted by user")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    pi.stop()
