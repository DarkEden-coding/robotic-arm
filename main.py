from CAN_Control.odrive_controller import odrive_controller
from CAN_Control.can_functions import shutdown


def get_angles(x_pos, y_pos, z_pos):
    """
    Get the angles of the robot arm
    :param x_pos: x position of the end effector
    :param y_pos: y position of the end effector
    :param z_pos: z position of the end effector
    :return: angles in radians (base angle, shoulder angle, elbow angle)
    """

    base_angle = atan2(y_pos, x_pos)

    target_distance = math.sqrt((0 - x_pos) ** 2 + (0 - y_pos) ** 2 + (0 - z_pos) ** 2)
    flat_distance = math.sqrt((0 - x_pos) ** 2 + (0 - y_pos) ** 2)

    return base_angle, shoulder_angle, elbow_angle


controller_1 = odrive_controller(0)
controller_2 = odrive_controller(1)
controller_3 = odrive_controller(2)

controller_1.enable_motor()
controller_2.enable_motor()
controller_3.enable_motor()

controller_1.move_to_angle(0)
controller_2.move_to_angle(15)
controller_3.move_to_angle(15)

sleep(1)

controller_1.move_to_angle(0)
controller_2.move_to_angle(0)
controller_3.move_to_angle(0)

controller_1.disable_motor()
controller_2.disable_motor()
controller_3.disable_motor()

shutdown()
