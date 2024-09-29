import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

pins = [1, 12, 0, [5, 6]]
step_pin = pins[0]
direction_pin = pins[1]
enable_pin = pins[2]
micro_stepping_pins = pins[3]

GPIO.setup(step_pin, GPIO.OUT)
GPIO.setup(direction_pin, GPIO.OUT)
GPIO.setup(enable_pin, GPIO.OUT)
GPIO.setup(micro_stepping_pins, GPIO.OUT)

GPIO.output(enable_pin, GPIO.LOW)
GPIO.output(direction_pin, GPIO.LOW)
GPIO.output(step_pin, GPIO.LOW)
GPIO.output(micro_stepping_pins, GPIO.LOW)
