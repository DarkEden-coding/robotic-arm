from constants import NetworkTablesConstants, CanIds, restricted_areas
from networktables import NetworkTables

NetworkTables.initialize(server=NetworkTablesConstants.ip)

table = NetworkTables.getTable("RoboticArmData")


def setup():
    table.putNumber("base_nodeid", CanIds.base_nodeid)
    table.putNumber("shoulder_nodeid", CanIds.shoulder_nodeid)
    table.putNumber("elbow_nodeid", CanIds.elbow_nodeid)
    table.putValue("restricted_areas", restricted_areas)


def enable_motors():
    table.putBoolean("enable_motors", True)


def disable_motors():
    table.putBoolean("enable_motors", False)


def shutdown():
    table.putBoolean("shutdown", True)


def set_percentage_speed(percentage_speed):
    table.putNumber("percentage_speed", percentage_speed)


def move(pos, wait_for_finish=False):
    table.putNumber("target_position", pos)


def emergency_stop():
    table.putBoolean("emergency_stop", True)


def get_position():
    return table.getValue("current_position", (0, 0, 0))
