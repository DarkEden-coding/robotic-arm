from math import sqrt
from threading import Thread
from time import sleep, time

from stepper_constants import StepperConstants, import_gpio

GPIO = import_gpio()
GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering


class StepperMotor:
    def __init__(self, motor_pins):
        """
        Stepper Motor class to control a stepper motor using the RPi.GPIO library.
        :param motor_pins: the pins to control the stepper motor in the following order:
        [step_pin, direction_pin, enable_pin, [micro_stepping_pins]]
        """
        self.step_pin = motor_pins[0]
        self.direction_pin = motor_pins[1]
        self.enable_pin = motor_pins[2]
        self.micro_stepping_pins = motor_pins[3]

        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.direction_pin, GPIO.OUT)
        GPIO.setup(self.enable_pin, GPIO.OUT)
        GPIO.setup(self.micro_stepping_pins, GPIO.OUT)

        GPIO.output(self.enable_pin, GPIO.HIGH)

        self.micro_stepping = StepperConstants.microstepping
        self.set_micro_stepping(StepperConstants.microstepping)

        self.current_position = 0
        self.current_velocity = 0
        self.moving = False

        self.max_speed = StepperConstants.max_speed
        self.acceleration = StepperConstants.acceleration

        self.running_thread = Thread(target=self.running_thread)
        self.running_thread.start()

    def set_micro_stepping(self, micro_stepping):
        GPIO.output(
            self.micro_stepping_pins[0],
            StepperConstants.microstep_map[micro_stepping][0],
        )
        GPIO.output(
            self.micro_stepping_pins[1],
            StepperConstants.microstep_map[micro_stepping][1],
        )
        self.micro_stepping = micro_stepping

    def running_thread(self):
        while True:
            start_time = time()
            if self.current_velocity > 0:
                GPIO.output(self.direction_pin, GPIO.HIGH)
            elif self.current_velocity < 0:
                GPIO.output(self.direction_pin, GPIO.LOW)

            step_velocity = abs(self.current_velocity) / (
                StepperConstants.degrees_per_step / self.micro_stepping
            )
            if step_velocity != 0:
                GPIO.output(self.step_pin, GPIO.HIGH)
                sleep(1 / (2 * step_velocity))
                GPIO.output(self.step_pin, GPIO.LOW)
                sleep(1 / (2 * step_velocity))
            else:
                sleep(0.01)
            self.current_position += self.current_velocity * (time() - start_time)

    def set_position(self, position, blocking=False):
        if blocking:
            self._set_position(position)
        else:
            Thread(target=self._set_position, args=(position,)).start()
            sleep(0.05)

    def _set_position(self, position):
        print(f"Moving to position: {position}")
        self.moving = True
        change_in_position = position - self.current_position
        start_position = self.current_position
        print(f"Change in position: {change_in_position}")

        if self._get_acceleration_distance() * 2 > abs(change_in_position):
            print("Move too short to get to max speed...")
            accelerate_position = position - change_in_position / 2
            decelerate_position = position - change_in_position / 2
        else:
            accelerate_position = (
                self.current_position
                + self._get_acceleration_distance()
                * (1 if change_in_position > 0 else -1)
            )
            decelerate_position = position - self._get_acceleration_distance() * (
                1 if change_in_position > 0 else -1
            )

        self.current_position = (
            0.01 if self.current_position == 0 else self.current_position
        )

        print(f"Accelerate Position: {accelerate_position}")
        print(f"Decelerate Position: {decelerate_position}")

        def get_acceleration_velocity():
            return sqrt(
                2
                * self.acceleration
                * abs(self.current_position - (start_position - 0.1))
            )

        def get_deceleration_velocity():
            return sqrt(
                2
                * self.acceleration
                * abs(
                    (self.current_position - start_position)
                    - (position - start_position)
                )
            )

        if change_in_position > 0:
            while self.current_position < accelerate_position:
                self.current_velocity = get_acceleration_velocity()
                sleep(0.0001)

            while self.current_position < decelerate_position:
                self.current_velocity = self.max_speed
                sleep(0.0001)

            while self.current_position < position:
                self.current_velocity = get_deceleration_velocity()
                sleep(0.0001)
        else:
            while self.current_position > accelerate_position:
                self.current_velocity = -get_acceleration_velocity()
                sleep(0.0001)

            while self.current_position > decelerate_position:
                self.current_velocity = -self.max_speed
                sleep(0.0001)

            while self.current_position > position:
                self.current_velocity = -get_deceleration_velocity()
                sleep(0.0001)

        self.current_velocity = 0
        self.moving = False
        print(f"Stopped at: {self.current_position}\n")

    def _get_acceleration_time(self):
        return self.max_speed / self.acceleration

    def _get_acceleration_distance(self):
        return 0.5 * self.acceleration * self._get_acceleration_time() ** 2


if __name__ == "__main__":
    graph_enabled = False  # Toggle graphing here

    if graph_enabled:
        import matplotlib.pyplot as plt  # Only import if graphing is enabled

    motor = StepperMotor([1, 12, 0, [5, 6]])

    moves = [180, -180]

    positions = []
    velocities = []
    time_steps = []
    start_time = time()

    if graph_enabled:
        plt.figure(figsize=(10, 5))
        plt.subplot(2, 1, 1)
        (pos_plot,) = plt.plot([], [], label="Position")
        plt.title("Stepper Motor Position Over Time")
        plt.ylabel("Position")
        plt.legend()

        plt.subplot(2, 1, 2)
        (vel_plot,) = plt.plot([], [], label="Velocity", color="orange")
        plt.title("Stepper Motor Velocity Over Time")
        plt.ylabel("Velocity")
        plt.xlabel("Time (s)")
        plt.legend()

    for move in moves:
        motor.set_position(move, blocking=False)

        while motor.moving:
            positions.append(motor.current_position)
            velocities.append(motor.current_velocity)
            time_steps.append(time() - start_time)

            if graph_enabled:
                pos_plot.set_data(time_steps, positions)
                vel_plot.set_data(time_steps, velocities)

                plt.subplot(2, 1, 1)
                plt.xlim(0, max(time_steps))
                plt.ylim(min(positions), max(positions))

                plt.subplot(2, 1, 2)
                plt.xlim(0, max(time_steps))
                plt.ylim(min(velocities), max(velocities))

                plt.pause(0.01)  # Pause to update the plot
            sleep(0.01)

    if graph_enabled:
        plt.show()
