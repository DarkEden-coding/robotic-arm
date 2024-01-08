from stepper_motor_controller import StepperMotorController, cleanup

max_speed = 36
acceleration = 6
starting_speed = 1

yaw_motor = StepperMotorController(
    enable_pin=2,
    dir_pin=27,
    step_pin=17,
    micro_step_pins=(3, 4),
    acceleration=acceleration,
    max_speed=max_speed,
    starting_speed=starting_speed,
    gear_ratio=4,
)

pitch_motor = StepperMotorController(
    enable_pin=0,
    dir_pin=12,
    step_pin=1,
    micro_step_pins=(5, 6),
    acceleration=acceleration,
    max_speed=max_speed,
    starting_speed=starting_speed,
    gear_ratio=2,
)

yaw_motor.enable_motor()
pitch_motor.enable_motor()

yaw_motor.set_micro_steps(8)
pitch_motor.set_micro_steps(8)

"""yaw_motor.move_to_angle(90)
pitch_motor.move_to_angle(90)
"""

yaw_motor.move_to_angle(90)
pitch_motor.move_to_angle(90)

yaw_motor.move_to_angle(-90)
pitch_motor.move_to_angle(-90)

yaw_motor.disable_motor()
pitch_motor.disable_motor()

cleanup()
