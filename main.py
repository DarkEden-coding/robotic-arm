from CAN_Control.odrive_controller import odrive_controller
from time import sleep

controller_1 = odrive_controller(1)
controller_2 = odrive_controller(2)

controller_1.enable_motor()
controller_2.enable_motor()

sleep(10)

controller_1.disable_motor()
controller_2.disable_motor()
