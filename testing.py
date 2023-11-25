from CAN_Control.odrive_controller import odrive_controller
from CAN_Control.can_functions import shutdown
from time import sleep

controller_1 = odrive_controller(0)
controller_2 = odrive_controller(1, gear_ratio=125)
controller_3 = odrive_controller(2)

controller_1.enable_motor()
controller_2.enable_motor()
controller_3.enable_motor()

controller_2.move_to_angle(30)

controller_2.wait_for_move()

sleep(2)

controller_2.set_speed(26)
controller_2.set_accel_decel(1, 1)

controller_2.move_to_angle(0)

controller_2.wait_for_move()

controller_1.disable_motor()
controller_2.disable_motor()
controller_3.disable_motor()

shutdown()
