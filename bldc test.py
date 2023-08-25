import RPi.GPIO as GPIO
import time

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin for PWM control
motor_pin = 4

# Set up the GPIO pin for PWM with a frequency of 1000 Hz
GPIO.setup(motor_pin, GPIO.OUT)
pwm = GPIO.PWM(motor_pin, 1000)  # 1000 Hz frequency

# Start PWM with an initial duty cycle of 0%
pwm.start(0)

try:
    """while True:
    for duty_cycle in range(0, 101, 5):  # Vary duty cycle from 0% to 100%
        pwm.ChangeDutyCycle(duty_cycle)
        print("Duty Cycle:", duty_cycle)
        time.sleep(0.5)  # Wait for a moment before changing speed"""
    while True:
        pwm.ChangeDutyCycle(int(input("Duty Cycle: ")))
        time.sleep(5)

except KeyboardInterrupt:
    # Clean up GPIO settings
    pwm.stop()
    GPIO.cleanup()
