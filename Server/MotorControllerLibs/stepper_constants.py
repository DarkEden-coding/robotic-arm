def import_gpio():
    # Try to import RPi.GPIO; if it fails, define a mock GPIO class for simulation
    try:
        import RPi.GPIO as GPIO

        return GPIO
    except ImportError:
        print("RPi.GPIO not found; using mock GPIO class for simulation")

        class GPIO:
            BCM = "BCM"
            OUT = "OUT"
            HIGH = True
            LOW = False

            @staticmethod
            def setmode(mode):
                # empty for simulation
                pass

            @staticmethod
            def setup(pin, mode):
                # empty for simulation
                pass

            @staticmethod
            def output(pin, state):
                # empty for simulation
                pass

        return GPIO


GPIO = import_gpio()


class StepperConstants:
    degrees_per_step = 1.8  # direct degrees per step
    microstepping = 16  # micro stepping of the stepper motor (8, 16, 32, 64)

    microstep_map = {
        8: (GPIO.LOW, GPIO.LOW),
        16: (GPIO.HIGH, GPIO.HIGH),
        32: (GPIO.HIGH, GPIO.LOW),
        64: (GPIO.LOW, GPIO.HIGH),
    }

    # -----------
    # Speed Curve
    # -----------

    max_speed = 10
    acceleration = 2
