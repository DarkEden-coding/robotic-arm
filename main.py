import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib

direction = 14  # Direction (DIR) GPIO Pin
step = 15  # Step GPIO Pin

# Declare a instance of class pass GPIO pins numbers and the motor type
mymotortest = RpiMotorLib.A4988Nema(direction, step, (21, 21, 21), "DRV8825")

mymotortest.motor_go(
    False,  # True=Clockwise, False=Counter-Clockwise
    "Full",  # Step type (Full,Half,1/4,1/8,1/16,1/32)
    50,  # number of steps
    0.0005,  # step delay [sec]
    False,  # True = print verbose output
    0.05,
)  # initial delay [sec]

mymotortest.motor_go(
    True,  # True=Clockwise, False=Counter-Clockwise
    "Full",  # Step type (Full,Half,1/4,1/8,1/16,1/32)
    50,  # number of steps
    0.0005,  # step delay [sec]
    False,  # True = print verbose output
    0.05,
)  # initial delay [sec]

GPIO.cleanup()  # clear GPIO allocations after run
