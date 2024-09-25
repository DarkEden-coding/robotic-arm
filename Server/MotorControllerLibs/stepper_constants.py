class StepperConstants:
    degrees_per_step = 1.8  # direct degrees per step
    trapezoidal_step = (
        0.01  # time between speed updates in trapezoidal profile (seconds)
    )
    microstepping = 16  # microstepping of the stepper motor (8, 16, 32, 64)

    # -----------
    # Speed Curve
    # -----------

    max_speed = 360
    acceleration = 240
    starting_speed = 0
