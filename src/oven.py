from pid import PID
from bme import BME
from logger import Logger
from uart import Uart
from pwm import PWMController
from time import sleep
from utils import load_csv

# import thread
from threading import Thread


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
        self.mode = "fixed"  # fixed or curve
        self.internal_temperature = 0.0
        self.ambiente_temperature = 0.0
        self.reference_temperature = 25.0
        self.control_signal = 0
        self.curve_time = 0
        self.reflow = load_csv()
        self.max_time_reflow = max(self.reflow.keys())

    def intialize(self):
        self.pwm.start()
        initial_commands = [
            "system_state_off",
            "system_work_off",
            "control_mode_fixed",
        ]
        map(self.uart.send, initial_commands)
        sleep(0.1)
        # initialize the logger in a new thread

        print("Oven initialized")

    def heating(self):
        if self.is_on and self.is_heating:
            self.pid.update_reference(self.reference_temperature)
            self.control_signal = self.pid.control(self.internal_temperature)
            self.pwm.apply_signal(self.control_signal)
            self.uart.send("control_signal", self.control_signal)
            # print(f"Ambi Temp: {self.ambiente_temperature:.2f}")
            # print(f"Inter Temp: {self.internal_temperature:.2f}")
            # print(f"Ref Temp: {self.reference_temperature}")
            # print(f"Control Signal: {self.control_signal}\n")

    def mode_curve(self):
        while True:
            print("curve time: ", self.curve_time)
            if not self.is_on or not self.is_heating or self.mode != "curve":
                print("Curve Mode Stopped")
                break
            self.update_internal_temperature()
            self.update_reference_temperature(
                self.reflow.get(self.curve_time, self.reference_temperature)
            )
            if abs(self.reference_temperature - self.internal_temperature) <= 4:
                self.curve_time += 1
                if self.curve_time >= self.max_time_reflow:
                    self.stop_heating()
                    self.change_mode()
                    self.curve_time = 0
                    break
            self.heating()
            sleep(1)

    def empty(self):
        pass

    def change_mode(self):
        print("CHANGE MODE")
        if self.mode == "fixed" and self.is_on and self.is_heating:
            self.uart.send("control_mode_curve")
            self.mode = "curve"
            self.turn_on_mode_curve_thread = Thread(target=self.turn_on_mode_curve)
            self.turn_on_mode_curve_thread.start()
        elif self.mode == "curve" and self.is_on and self.is_heating:
            self.uart.send("control_mode_fixed")
            self.mode = "fixed"
            if hasattr(self, "curve_thread"):
                self.curve_thread.join()
            if hasattr(self, "turn_on_mode_curve_thread"):
                self.turn_on_mode_curve_thread.join()

    def turn_on_mode_curve(self):
        self.curve_time = 0
        self.uart.send("control_mode_curve")
        self.update_ambiente_temperature()
        self.update_reference_temperature(self.ambiente_temperature)
        while (
            abs(self.reference_temperature - self.internal_temperature) > 4
            and self.is_on
            and self.is_heating
            and self.mode == "curve"
        ):
            self.heating()
            self.update_internal_temperature()
            self.update_ambiente_temperature()
            sleep(1)
        self.curve_thread = Thread(target=self.mode_curve)
        self.curve_thread.start()

    def update_ambiente_temperature(self):
        self.ambiente_temperature = self.bme.get_temperature()
        self.uart.send("ambiente_temperature", self.ambiente_temperature)
        sleep(1)

    def update_internal_temperature(self):
        self.uart.send("get_internal_temperature")
        self.receive()

    def set_internal_temperature(self, internal_temperature):
        self.internal_temperature = internal_temperature

    def update_reference_temperature(self, reference_temperature=None):
        if reference_temperature:
            self.reference_temperature = reference_temperature
        if self.reference_temperature < self.ambiente_temperature:
            self.reference_temperature = round(self.ambiente_temperature, 2)
        self.uart.send("send_reference_temperature", self.reference_temperature)

    def set_reference_temperature(self, reference_temperature):
        if abs(self.ambiente_temperature - reference_temperature) <= 2:
            reference_temperature = round(self.ambiente_temperature, 2)
        self.reference_temperature = reference_temperature

    def udpate_system_mode(self, system_mode):
        self.system_mode = system_mode

    def turn_on(self):
        self.uart.send("system_state_on")
        self.is_on = True

    def turn_off(self):
        self.uart.send("system_state_off")
        self.is_on = False
        self.stop_heating()

    def log_cron(self):
        while self.is_on and self.is_heating:
            self.logger.write_log(
                self.internal_temperature,
                self.ambiente_temperature,
                self.reference_temperature,
                self.control_signal,
            )
            sleep(1)

    def control_temperature(self):
        if self.is_on and self.is_heating:
            self.update_ambiente_temperature()
            if self.mode == "fixed" and self.system_mode == "dashboard":
                self.uart.send("get_reference_temperature")
            elif self.mode == "curve" and self.system_mode == "debug":
                self.update_reference_temperature()
            self.receive()
            self.update_internal_temperature()

            if self.mode == "fixed":
                self.heating()
            sleep(0.1)

    def debug(self):
        while True:
            if self.system_mode == "debug" and self.is_on and self.is_heating:
                self.update_reference_temperature()
                self.control_temperature()
            elif not self.is_on or not self.is_heating:
                break
            sleep(1)

    def start_heating(self):
        if self.is_on and not self.is_heating:
            self.log_thread = Thread(target=self.log_cron)
            self.is_heating = True
            self.log_thread.start()
            self.uart.send("system_work_on")
            if self.mode == "curve":
                self.turn_on_mode_curve_thread = Thread(target=self.turn_on_mode_curve)
                self.turn_on_mode_curve_thread.start()
            elif self.system_mode == "debug":
                self.debug_thread = Thread(target=self.debug)
                self.debug_thread.start()

    def set_mode(self, mode):
        self.mode = mode

    def stop_heating(self):
        self.uart.send("system_work_off")
        self.is_heating = False

    def down(self):
        self.uart.send("control_mode_fixed")
        self.turn_off()
        sleep(2)
        if hasattr(self, "log_thread"):
            self.log_thread.join()
        self.pwm.stop()
        self.bme.close()
        self.uart.close()

    def receive(self):
        sleep(0.1)
        commands = {
            "turn_on_oven": self.turn_on,
            "turn_off_oven": self.turn_off,
            "turn_on_heating": self.start_heating,
            "turn_off_heating": self.stop_heating,
            "change_mode": self.change_mode,
            "internal_temperature": self.set_internal_temperature,
            "reference_temperature": self.set_reference_temperature,
        }
        command, value = self.uart.receive()
        if (
            command
            and command == "get_user_command"
            and self.system_mode == "dashboard"
        ):
            commands.get(value, self.empty)()
        if command in ["internal_temperature", "reference_temperature"]:
            commands.get(command, self.empty)(value)
        return self.uart.receive()
