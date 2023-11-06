from CAN_Control.odrive_controller import odrive_controller
from CAN_Control.can_functions import shutdown


def test_move():
    controller_1.move_to_angle(45)

    controller_1.wait_for_move()

    controller_1.move_to_angle(0)
    controller_2.move_to_angle(22.5)

    controller_1.wait_for_move()
    controller_2.wait_for_move(delay=0.1)

    controller_1.move_to_angle(0)
    controller_2.move_to_angle(0)

    controller_1.wait_for_move()
    controller_2.wait_for_move(delay=0.1)


controller_1 = odrive_controller(0)
controller_2 = odrive_controller(1)

controller_1.enable_motor()
controller_2.enable_motor()

while True:
    test_move()

controller_1.disable_motor()
controller_2.disable_motor()

shutdown()
