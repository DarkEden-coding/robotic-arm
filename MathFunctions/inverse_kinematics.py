from constants import (
    Vectors,
)
import numpy as np
from MathFunctions.geometry import (
    Vector3,
    is_point_in_any_cube,
)


def get_angles(target_position, target_rotation, restricted_ares):
    """
    Get the angles of the robot arm
    :param target_position: target position of the robot arm end effector
    :param target_rotation: target rotation of the robot arm end effector
    :param restricted_ares: list of restricted areas for the robot arm, each area is a Cube object
    :return: angles in degrees (base angle, shoulder angle, elbow angle)
    """
    if any(is_point_in_any_cube(target_position, restricted_ares)):
        raise ValueError("Target position is in a restricted area")

    m_end_effector_vector = Vector3(
        Vectors.m_fore_arm_vector.get_end_point(), [0, 0, 130]
    )
    m_end_effector_vector.move_absolute(target_position)
    m_end_effector_vector.rotate_around_point(
        target_rotation[0], target_rotation[1], 0, target_position
    )

    wrist_target_position = m_end_effector_vector.get_end_point()

    # angle between projected_upper_arm_vector and upper_arm_vector_one to correct for the error
    upper_arm_error_angle = np.arccos(
        np.dot(
            Vectors.m_projected_upper_arm_vector.get_end_point()
            - Vectors.m_base_vector.get_end_point(),
            Vectors.m_upper_arm_vector_one.get_end_point()
            - Vectors.m_base_vector.get_end_point(),
        )
        / (
            len(Vectors.m_projected_upper_arm_vector)
            * len(Vectors.m_upper_arm_vector_one)
        )
    ) * (180 / np.pi)

    # calculate the base angle to the target
    base_angle = np.arctan2(wrist_target_position[1], wrist_target_position[0]) * (
        180 / np.pi
    )

    # the distance between the end of the base vector and the target pos
    target_base_distance = np.linalg.norm(
        wrist_target_position - Vectors.m_base_vector.get_end_point()
    )

    # use some triangle rules to find the shoulder angles given all side lengths
    shoulder_angle = np.arccos(
        (
            len(Vectors.m_projected_upper_arm_vector) ** 2
            + target_base_distance**2
            - len(Vectors.m_fore_arm_vector) ** 2
        )
        / (2 * len(Vectors.m_projected_upper_arm_vector) * target_base_distance)
    ) * (180 / np.pi)

    # use some triangle rules to find the elbow angle given all side lengths
    elbow_angle = (
        -90
        + np.arccos(
            (
                len(Vectors.m_fore_arm_vector) ** 2
                + len(Vectors.m_projected_upper_arm_vector) ** 2
                - target_base_distance**2
            )
            / (
                2
                * len(Vectors.m_fore_arm_vector)
                * len(Vectors.m_projected_upper_arm_vector)
            )
        )
        * (180 / np.pi)
        - upper_arm_error_angle
    )

    target_flat_distance = np.linalg.norm(wrist_target_position[:2])

    # calculate the vertical angle to the target for angle correction
    vert_angle_to_target = np.arctan2(
        wrist_target_position[2] - Vectors.m_base_vector.get_end_point()[2],
        target_flat_distance,
    ) * (180 / np.pi)

    vert_angle_to_target += upper_arm_error_angle

    shoulder_angle = -(90 - (shoulder_angle + vert_angle_to_target))
    elbow_angle = -(90 - elbow_angle)

    # reverse the angles to get the target position in wrist local space
    m_end_effector_vector.rotate_around_point(
        0, 0, -base_angle, Vectors.m_base_vector.get_end_point()
    )
    m_end_effector_vector.rotate_around_point(
        0, shoulder_angle, 0, Vectors.m_base_vector.get_end_point()
    )
    m_end_effector_vector.rotate_around_point(
        0, elbow_angle, 0, Vectors.m_upper_arm_vector_two.get_end_point()
    )
    m_end_effector_vector.move_absolute(np.array([0, 0, 0], dtype=float))

    wrist_flat_distance = np.linalg.norm(m_end_effector_vector.get_end_point()[:2])
    wrist_pitch_angle = 90 + np.arctan2(
        m_end_effector_vector.get_end_point()[2], wrist_flat_distance
    ) * (180 / np.pi)

    wrist_yaw_angle = (
        np.arctan2(
            m_end_effector_vector.get_end_point()[1],
            m_end_effector_vector.get_end_point()[0],
        )
        * (180 / np.pi)
        + 180
    )
    if wrist_yaw_angle > 180:
        wrist_yaw_angle -= 360

    return base_angle, shoulder_angle, elbow_angle, wrist_yaw_angle, wrist_pitch_angle


def get_trajectory(
    base_angle,
    shoulder_angle,
    elbow_angle,
    base_controller,
    shoulder_controller,
    elbow_controller,
):
    """
    Get the relative speeds for the robot arm joints
    :param base_angle: base angle in degrees
    :param shoulder_angle: shoulder angle in degrees
    :param elbow_angle: elbow angle in degrees
    :param base_controller: base controller object
    :param shoulder_controller: shoulder controller object
    :param elbow_controller: elbow controller object
    :return: relative speeds for base, shoulder, and elbow joints
    """
    base_angle, shoulder_angle, elbow_angle = (
        abs(base_angle - base_controller.position),
        abs(shoulder_angle - shoulder_controller.position),
        abs(elbow_angle - elbow_controller.position),
    )

    # Find the maximum angle
    max_angle = max(base_angle, shoulder_angle, elbow_angle)

    # Calculate relative speeds
    base_speed = 1 if base_angle == 0 else base_angle / max_angle
    shoulder_speed = 1 if shoulder_angle == 0 else shoulder_angle / max_angle
    elbow_speed = 1 if elbow_angle == 0 else elbow_angle / max_angle

    return base_speed, shoulder_speed, elbow_speed


def get_pos_from_angles(
    base_angle, shoulder_angle, elbow_angle, wrist_pitch_angle, wrist_yaw_angle
):
    """
    Get the position of the robot arm end effector from the angles
    :param base_angle: the base angle in degrees
    :param shoulder_angle: the shoulder angle in degrees
    :param elbow_angle: the elbow angle in degrees
    :param wrist_pitch_angle: the wrist pitch angle in degrees
    :param wrist_yaw_angle: the wrist yaw angle in degrees
    :return: the position of the robot arm end effector
    """

    shoulder_angle = -shoulder_angle
    elbow_angle = -elbow_angle

    # reset vectors
    m_base_vector = Vectors.m_base_vector.copy()
    m_upper_arm_vector_one = Vectors.m_upper_arm_vector_one.copy()
    m_upper_arm_vector_two = Vectors.m_upper_arm_vector_two.copy()
    m_projected_upper_arm_vector = Vectors.m_projected_upper_arm_vector.copy()
    m_fore_arm_vector = Vectors.m_fore_arm_vector.copy()
    m_end_effector_vector = Vectors.m_end_effector_vector.copy()

    m_end_effector_vector.rotate_around_point(
        0, wrist_pitch_angle, wrist_yaw_angle, m_fore_arm_vector.get_end_point()
    )

    # preform the rotations to the vectors
    m_base_vector.rotate_locally(0, 0, base_angle)
    m_upper_arm_vector_one.rotate_around_point(
        0, shoulder_angle, 0, m_base_vector.get_end_point()
    )
    m_upper_arm_vector_two.rotate_around_point(
        0, shoulder_angle, 0, m_base_vector.get_end_point()
    )
    m_fore_arm_vector.rotate_around_point(
        0, shoulder_angle, 0, m_base_vector.get_end_point()
    )
    m_projected_upper_arm_vector.rotate_around_point(
        0, shoulder_angle, 0, m_base_vector.get_end_point()
    )
    m_end_effector_vector.rotate_around_point(
        0, shoulder_angle, 0, m_base_vector.get_end_point()
    )

    m_fore_arm_vector.rotate_around_point(
        0, elbow_angle, 0, m_upper_arm_vector_two.get_end_point()
    )
    m_end_effector_vector.rotate_around_point(
        0, elbow_angle, 0, m_upper_arm_vector_two.get_end_point()
    )

    m_upper_arm_vector_one.rotate_around_point(
        0, 0, base_angle, m_base_vector.get_end_point()
    )
    m_upper_arm_vector_two.rotate_around_point(
        0, 0, base_angle, m_base_vector.get_end_point()
    )
    m_fore_arm_vector.rotate_around_point(
        0, 0, base_angle, m_base_vector.get_end_point()
    )
    m_projected_upper_arm_vector.rotate_around_point(
        0, 0, base_angle, m_base_vector.get_end_point()
    )

    m_end_effector_vector.rotate_around_point(
        0, 0, base_angle, m_base_vector.get_end_point()
    )

    return np.around(m_end_effector_vector.get_end_point(), 4)
