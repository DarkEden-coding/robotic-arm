from constants import NetworkTablesConstants, restricted_areas_encoded
from networktables import NetworkTables
from time import sleep

NetworkTables.initialize(server=NetworkTablesConstants.ip)

data_table = NetworkTables.getTable("RoboticArmData")


def setup():
    data_table.putStringArray("restricted_areas", restricted_areas_encoded)

    data_table.putBoolean("enable_motors", False)
    data_table.putBoolean("shutdown", False)
    data_table.putBoolean("emergency_stop", False)
    data_table.putNumber("percentage_speed", 1)
    data_table.putValue("target_position", (0, 0, 0))
    data_table.putBoolean("moving", False)
    data_table.putValue("current_position", (0, 0, 0))

    data_table.putBoolean("setup", True)


def enable_motors():
    data_table.putBoolean("enable_motors", True)


def disable_motors():
    data_table.putBoolean("enable_motors", False)


def shutdown():
    data_table.putBoolean("shutdown", True)


def set_percentage_speed(percentage_speed):
    data_table.putNumber("percentage_speed", percentage_speed)


def move(pos, rotations, wait_for_finish=False):
    if not data_table.getBoolean("moving", False):
        data_table.putValue("target_position", pos)
        data_table.putValue("target_rotations", rotations)
        data_table.putBoolean("request_move", True)

        if wait_for_finish:
            while data_table.getBoolean("moving", True):
                sleep(0.1)


def emergency_stop():
    data_table.putBoolean("emergency_stop", True)


def get_position():
    return data_table.getValue("current_position", (0, 0, 0))
