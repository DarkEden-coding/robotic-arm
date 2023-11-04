from CAN_Control.odrive_controller import odrive_controller
from CAN_Control.can_functions import shutdown
from time import sleep

controller_1 = odrive_controller(0)
# controller_2 = odrive_controller(1)

controller_1.enable_motor()
print(controller_1.get_encoder_pos())
# controller_2.enable_motor()

sleep(10)

controller_1.disable_motor()
# controller_2.disable_motor()

shutdown()
