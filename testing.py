from CAN_Control.odrive_controller import odrive_controller
from CAN_Control.can_functions import shutdown
from time import sleep

controller_1 = odrive_controller(0)
controller_2 = odrive_controller(1, gear_ratio=125)
controller_3 = odrive_controller(2)

sleep(2)

shutdown()
