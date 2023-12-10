import smbus2
import time

# Replace with the correct I2C address
DEVICE_ADDRESS = 0x36  # AS5600 I2C address

# Registers for the 12-bit angle value
ANGLE_HIGH_REGISTER = 0x0E  # High 8 bits of the angle
ANGLE_LOW_REGISTER = 0x0F  # Low 4 bits of the angle

bus = smbus2.SMBus(1)  # 1 indicates /dev/i2c-1


def read_angle(bus, address):
    # Read high and low bytes of the angle
    angle_high = bus.read_byte_data(address, ANGLE_HIGH_REGISTER)
    angle_low = bus.read_byte_data(address, ANGLE_LOW_REGISTER)
    # Combine the high and low bytes
    angle = (angle_high << 8) | angle_low
    return angle & 0x0FFF  # The angle is a 12-bit value


try:
    while True:
        # Read the angle value
        angle_value = read_angle(bus, DEVICE_ADDRESS)
        print(f"Angle Value: {angle_value}")

        # Sleep for a bit before reading again
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nScript interrupted by user.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    bus.close()
