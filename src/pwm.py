import RPi.GPIO as GPIO


class PWMController:
    def __init__(self, resistor_pin=23, fan_pin=24, frequency=999):
        self.resistor_pin = resistor_pin
        self.fan_pin = fan_pin
        self.frequency = frequency
        GPIO.setwarnings(False)
        # setup the GPIO
        GPIO.setmode(GPIO.BCM)
        # set the resistor and fan pin as PWM output
        GPIO.setup(self.resistor_pin, GPIO.OUT)
        GPIO.setup(self.fan_pin, GPIO.OUT)
        # create PWM objects
        self.resistor_pwm = GPIO.PWM(self.resistor_pin, self.frequency)
        self.fan_pwm = GPIO.PWM(self.fan_pin, self.frequency)

    def start(self, resistor_duty_cycle=50, fan_duty_cycle=50):
        self.resistor_pwm.start(resistor_duty_cycle)
        self.fan_pwm.start(fan_duty_cycle)

    def stop(self):
        self.resistor_pwm.stop()
        self.fan_pwm.stop()
        self.cleanup()

    def change_resistor_duty_cycle(self, duty_cycle):
        self.resistor_pwm.ChangeDutyCycle(duty_cycle)

    def change_fan_duty_cycle(self, duty_cycle):
        duty_cycle = abs(duty_cycle)
        if duty_cycle < 40:
            duty_cycle = 40
        self.fan_pwm.ChangeDutyCycle(duty_cycle)

    def apply_signal(self, signal):
        if signal > 0:
            self.change_resistor_duty_cycle(signal)
            self.change_fan_duty_cycle(0)
        else:
            self.change_resistor_duty_cycle(0)
            self.change_fan_duty_cycle(signal)

    def change_frequency(self, frequency):
        self.frequency = frequency
        self.resistor_pwm.ChangeFrequency(self.frequency)
        self.fan_pwm.ChangeFrequency(self.frequency)

    def cleanup(self):
        GPIO.cleanup()
