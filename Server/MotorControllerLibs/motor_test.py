from time import sleep

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

pins = [17, 12, 0, [5, 6]]


# run stepper motor 10 steps in one direction then the other

GPIO.setup(pins[0], GPIO.OUT)
GPIO.setup(pins[1], GPIO.OUT)
GPIO.setup(pins[2], GPIO.OUT)
GPIO.setup(pins[3][0], GPIO.OUT)
GPIO.setup(pins[3][1], GPIO.OUT)

GPIO.output(pins[2], GPIO.HIGH)

GPIO.output(pins[3][0], GPIO.LOW)
GPIO.output(pins[3][1], GPIO.LOW)

try:
    while True:
        print("Running stepper motor 10 steps forward")
        GPIO.output(pins[1], GPIO.HIGH)
        for i in range(10):
            GPIO.output(pins[0], GPIO.HIGH)
            sleep(.1)
            GPIO.output(pins[0], GPIO.LOW)
            sleep(.1)
        print("Running stepper motor 10 steps backward")
        sleep(1)
        GPIO.output(pins[1], GPIO.LOW)
        for i in range(10):
            GPIO.output(pins[0], GPIO.HIGH)
            sleep(.1)
            GPIO.output(pins[0], GPIO.LOW)
            sleep(.1)
except KeyboardInterrupt:
    print("Cleaning up GPIO")
    GPIO.cleanup()
