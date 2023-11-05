from CAN_Control.odrive_controller import odrive_controller
from CAN_Control.can_functions import shutdown


def test_move():
    controller_1.move_to_pos(6.25)
    controller_2.move_to_pos(6.25)

    controller_1.wait_for_move()
    controller_2.wait_for_move()

    controller_1.move_to_pos(-6.25)
    controller_2.move_to_pos(-6.25)

    controller_1.wait_for_move()
    controller_2.wait_for_move()

    controller_1.move_to_pos(0)
    controller_2.move_to_pos(0)

    controller_1.wait_for_move()
    controller_2.wait_for_move()


controller_1 = odrive_controller(0)
controller_2 = odrive_controller(1)

controller_1.enable_motor()
controller_2.enable_motor()

test_move()

controller_1.set_speed(50)
controller_2.set_speed(50)

controller_1.disable_motor()
controller_2.disable_motor()

shutdown()
