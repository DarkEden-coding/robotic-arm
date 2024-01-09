from stepper_motor_controller import StepperMotorController, cleanup
from constants import (
    max_speed_stepper,
    acceleration_stepper,
    starting_speed_stepper,
    microstepping,
)

yaw_motor = StepperMotorController(
    enable_pin=2,
    dir_pin=27,
    step_pin=17,
    micro_step_pins=(3, 4),
    acceleration=acceleration_stepper,
    max_speed=max_speed_stepper,
    starting_speed=starting_speed_stepper,
    gear_ratio=4,
)

pitch_motor = StepperMotorController(
    enable_pin=0,
    dir_pin=12,
    step_pin=1,
    micro_step_pins=(5, 6),
    acceleration=acceleration_stepper,
    max_speed=max_speed_stepper,
    starting_speed=starting_speed_stepper,
    gear_ratio=2,
)

yaw_motor.enable_motor()
pitch_motor.enable_motor()

yaw_motor.set_micro_steps(microstepping)
pitch_motor.set_micro_steps(microstepping)

try:
    yaw_motor.move_to_angle(-180)
    pitch_motor.move_to_angle(90)

    yaw_motor.move_to_angle(180)
    pitch_motor.move_to_angle(-90)
except KeyboardInterrupt:
    print("KeyboardInterrupt")
    pass

yaw_motor.disable_motor()
pitch_motor.disable_motor()

cleanup()
