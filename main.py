from RpiMotorLib import RpiMotorLib
from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

direction = 14  # Direction (DIR) GPIO Pin
step = 15  # Step GPIO Pin

# Declare a instance of class pass GPIO pins numbers and the motor type
mymotortest = RpiMotorLib.A4988Nema(direction, step, (-1, -1, -1), "DRV8825")

while True:
    print("Counter-Clockwise Test")
    mymotortest.motor_go(
        False,  # True=Clockwise, False=Counter-Clockwise
        "Full",  # Step type (Full,Half,1/4,1/8,1/16,1/32)
        50,  # number of steps
        0.1,  # step delay [sec]
        False,  # True = print verbose output
        0.05,
    )  # initial delay [sec]

    print("Clockwise Test")
    mymotortest.motor_go(
        False,  # True=Clockwise, False=Counter-Clockwise
        "Full",  # Step type (Full,Half,1/4,1/8,1/16,1/32)
        50,  # number of steps
        0.1,  # step delay [sec]
        False,  # True = print verbose output
        0.05,
    )  # initial delay [sec]
    sleep(1)
