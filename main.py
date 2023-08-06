from time import sleep
from motor import StepperMotor

direction_pin = 14  # Direction (DIR) GPIO Pin
step_pin = 15  # Step GPIO Pin
ms_pins = (17, 27, 22)
enable_pin = 2  # Enable GPIO Pin


motor = StepperMotor(
    direction_pin=direction_pin,
    step_pin=step_pin,
    max_speed=1000,
    starting_speed=0,
    acceleration=10,
    microstepping=5,
    ms_pins=ms_pins,
    enable_pin=enable_pin,
)

dist = 180

motor.enable()

motor.move(dist, blocking=True, clockwise=True, debug=True)

motor.move(dist, blocking=True, clockwise=False, debug=True)

"""motor.move(dist, blocking=True, clockwise=True, debug=True)

motor.move(dist, blocking=True, clockwise=False, debug=True)

motor.move(dist, blocking=True, clockwise=True, debug=True)

motor.move(dist, blocking=True, clockwise=False, debug=True)

motor.move(dist, blocking=True, clockwise=True, debug=True)

motor.move(dist, blocking=True, clockwise=False, debug=True)"""

motor.disable()
