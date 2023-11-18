import math
from CAN_Control.odrive_controller import odrive_controller
from CAN_Control.can_functions import shutdown

arm_1_length = 575
arm_2_length = 650


def get_angles(x_pos, y_pos, z_pos):
    """
    Get the angles of the robot arm
    :param x_pos: x position of the end effector
    :param y_pos: y position of the end effector
    :param z_pos: z position of the end effector
    :return: angles in radians (base angle, shoulder angle, elbow angle)
    """
    # soh cah toa

    base_angle = math.atan2(y_pos, x_pos)

    y_flat_distance = math.sqrt((0 - x_pos) ** 2 + (0 - y_pos) ** 2)

    rotated_point = (y_flat_distance, z_pos)

    x_flat_distance = math.sqrt(
        (0 - rotated_point[0]) ** 2 + (0 - rotated_point[1]) ** 2
    )

    shoulder_offset = math.atan2(rotated_point[1], rotated_point[0])

    shoulder_angle = math.acos(
        (arm_1_length**2 + x_flat_distance**2 - arm_2_length**2)
        / (2 * arm_1_length * x_flat_distance)
    )

    shoulder_angle += shoulder_offset

    elbow_angle = math.acos(
        (arm_2_length**2 + arm_1_length**2 - x_flat_distance**2)
        / (2 * arm_2_length * arm_1_length)
    )

    # convert to degrees
    base_angle = math.degrees(base_angle)
    shoulder_angle = 90 - math.degrees(shoulder_angle)
    elbow_angle = 180 - math.degrees(elbow_angle)

    return base_angle, shoulder_angle, -elbow_angle


print(get_angles(600, 0, 0))
angles = get_angles(600, 0, 0)


controller_1 = odrive_controller(0)
controller_2 = odrive_controller(1, gear_ratio=125)
controller_3 = odrive_controller(2)

controller_1.enable_motor()
controller_2.enable_motor()
controller_3.enable_motor()

# controller_1.move_to_angle(0)
controller_2.move_to_angle(angles[1])
controller_3.move_to_angle(angles[2])

controller_2.wait_for_move()
controller_3.wait_for_move()

input("Press enter to move to next position...")

# controller_1.move_to_angle(0)
controller_2.move_to_angle(0)
controller_3.move_to_angle(0)

controller_2.wait_for_move()
controller_3.wait_for_move()

input("Press enter to disable...")

controller_1.disable_motor()
controller_2.disable_motor()
controller_3.disable_motor()

shutdown()
