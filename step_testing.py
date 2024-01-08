from stepper_motor_controller import StepperMotorController, cleanup

max_speed = 1
acceleration = 0.1

yaw_motor = StepperMotorController(
    enable_pin=2,
    dir_pin=27,
    step_pin=17,
    micro_step_pins=(3, 4),
    acceleration=acceleration,
    max_speed=max_speed,
)

pitch_motor = StepperMotorController(
    enable_pin=0,
    dir_pin=12,
    step_pin=1,
    micro_step_pins=(5, 6),
    acceleration=acceleration,
    max_speed=max_speed,
)

yaw_motor.enable_motor()
pitch_motor.enable_motor()

yaw_motor.set_micro_steps(64)
pitch_motor.set_micro_steps(64)

"""yaw_motor.move_to_angle(90)
pitch_motor.move_to_angle(90)
"""

yaw_motor.force_move_steps(12800, .0001)
pitch_motor.force_move_steps(6400, .0001)

yaw_motor.force_move_steps(-12800, .0001)
pitch_motor.force_move_steps(-6400, .0001)

yaw_motor.disable_motor()
pitch_motor.disable_motor()

cleanup()
