from time import sleep
from motor import StepperMotor

direction_pin = 14  # Direction (DIR) GPIO Pin
step_pin = 15  # Step GPIO Pin
ms_pins = (17, 22, 27)
enable_pin = 2  # Enable GPIO Pin


motor = StepperMotor(
    direction_pin=direction_pin,
    step_pin=step_pin,
    max_speed=300,
    starting_speed=0,
    acceleration=5,
    microstepping=2,
    ms_pins=ms_pins,
    enable_pin=enable_pin,
)

motor.enable()
motor.move(1000, blocking=True, clockwise=True, debug=True)

motor.move(1000, blocking=True, clockwise=False, debug=True)

motor.disable()
