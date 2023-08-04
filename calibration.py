import RPi.GPIO as GPIO

direction_pin = 14  # Direction (DIR) GPIO Pin
step_pin = 15  # Step GPIO Pin
ms_pins = (17, 22, 27)
enable_pin = 2  # Enable GPIO Pin


GPIO.setmode(GPIO.BCM)

GPIO.setup(direction_pin, GPIO.OUT)
GPIO.setup(step_pin, GPIO.OUT)
GPIO.setup(ms_pins[0], GPIO.OUT)
GPIO.setup(ms_pins[1], GPIO.OUT)
GPIO.setup(ms_pins[2], GPIO.OUT)
GPIO.setup(enable_pin, GPIO.OUT)

GPIO.output(enable_pin, GPIO.LOW)
GPIO.output(step_pin, GPIO.HIGH)

GPIO.output(ms_pins[0], GPIO.LOW)
GPIO.output(ms_pins[1], GPIO.LOW)
GPIO.output(ms_pins[2], GPIO.LOW)
