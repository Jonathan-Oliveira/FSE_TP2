from pid import PID
from bme import BME
from logger import Logger
from uart import Uart
from pwm import PWMController
from time import sleep
from utils import load_csv


class Oven:
    def __init__(self):
        self.logger = Logger()
        self.pid = PID()
        self.bme = BME()
        self.uart = Uart()
        self.pwm = PWMController()
        self.is_on = False
        self.is_heating = False
        self.system_mode = "dashboard"  # debug or dashboard
        self.curve_mode = "fixed"  # fixed or curve
        self.internal_temperature = 0.0
        self.ambiente_temperature = 35.0
        self.reference_temperature = 0.0
        self.control_signal = 0
        self.curve_time = 0
        self.initializing_curve_mode = False
        self.reflow = load_csv()

    def intialize(self):
        self.pwm.start()
        initial_commands = [
            "system_state_off",
            "system_work_off",
            "control_mode_fixed",
        ]
        map(self.uart.send, initial_commands)
        print("Oven initialized")

    def heating(self):
        if self.is_on and not self.is_heating:
            self.pid.update_reference(reference=self.reference_temperature)
            self.control_signal = self.pid.control(
                actual_measure=self.internal_temperature
            )
            self.pwm.apply_signal(signal=self.control_signal)
            self.uart.send("internal_temperature", self.internal_temperature)
            self.uart.send("reference_temperature", self.reference_temperature)
            self.uart.send("control_signal", self.control_signal)
            self.pwm.apply_signal(signal=self.control_signal)
            print(f"Ambi Temp: {self.ambiente_temperature}")
            print(f"Inter Temp: {self.internal_temperature}")
            print(f"Ref Temp: {self.reference_temperature}")
            print(f"Control Signal: {self.control_signal}\n")

            self.logger.write_log(
                self.internal_temperature,
                self.ambiente_temperature,
                self.reference_temperature,
                self.control_signal,
            )

    def mode_curve(self):
        if self.initializing_curve_mode:
            self.curve_time = 0
            if abs(self.ambiente_temperature - self.internal_temperature) <= 2:
                self.initializing_curve_mode = False
        else:
            self.set_reference_temperature(
                self.reflow.get(self.curve_time, self.reference_temperature)
            )
            if abs(self.reference_temperature - self.internal_temperature) <= 2:
                self.curve_time += 1
        self.heating()

    def mode_fixed(self):
        self.heating()

    def empty(self):
        pass

    def refresh_system(self):
        self.reference_temperature = self.ambiente_temperature
        if abs(self.reference_temperature - self.internal_temperature) >= 2:
            self.heating()
            self.update_internal_temperature()

    def change_mode(self):
        if self.curve_mode == "fixed":
            self.uart.send("control_mode_curve")
            self.curve_mode = "curve"
            self.initializing_curve_mode = True
        elif self.curve_mode == "curve":
            self.curve_mode = "fixed"
            self.uart.send("control_mode_fixed")

    def read_user_command(self):
        return self.uart.send_and_receive(message="get_user_command")

    def turn_on_mode_curve(self):
        self.curve_mode = "curve"
        self.uart.send("control_mode_curve")
        self.uart.receive()
        self.update_ambiente_temperature()
        self.update_reference_temperature(self.ambiente_temperature)
        while abs(self.reference_temperature - self.internal_temperature) > 1:
            self.heating()
            self.update_internal_temperature()
            sleep(1)

    def control_temperature(self):
        if self.is_on and self.is_heating:
            self.update_internal_temperature()
            self.update_ambiente_temperature()
            if self.curve_mode == "fixed":
                self.update_reference_temperature()
                self.curve_mode_fixed()
            elif self.curve_mode == "curve":
                self.curve_mode_curve()

    def update_ambiente_temperature(self):
        self.ambiente_temperature = self.bme.get_temperature()
        self.uart.send("ambiente_temperature", self.ambiente_temperature)

    def update_reference_temperature(self, reference_temperature=None):
        if reference_temperature:
            self.reference_temperature = reference_temperature
            self.uart.send("reference_temperature", self.reference_temperature)
        else:
            if self.system_mode == "dashboard":
                reference_temperature = self.uart.send_and_receive(
                    message="get_reference_temperature"
                )
            elif self.system_mode == "debug":

                if reference_temperature:
                    self.reference_temperature = reference_temperature

    def update_internal_temperature(self):
        self.internal_temperature = self.uart.send_and_receive(
            message="get_internal_temperature"
        )

    def set_reference_temperature(self, reference_temperature):
        if reference_temperature <= self.ambiente_temperature:
            self.reference_temperature = self.ambiente_temperature
        else:
            self.reference_temperature = reference_temperature

    def turn_on(self):
        self.uart.send("system_state_on")
        self.is_on = True

    def turn_off(self):
        self.uart.send("system_state_off")
        self.is_on = False
        self.stop_heating()

    def start_heating(self):
        if self.is_on:
            self.uart.send("system_work_on")
            self.is_heating = True

    def stop_heating(self):
        self.uart.send("system_work_off")
        self.is_heating = False

        # read file curva_reflow.csv and send to

    def down(self):
        self.turn_off()
        self.pwm.stop()
        self.bme280.close()
        self.uart.close()
