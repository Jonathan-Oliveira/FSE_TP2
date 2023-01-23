import smbus2
import bme280


class BME:
    def __init__(self, address=0x76, port=1):
        self.address = address
        self.port = port
        self.bus = smbus2.SMBus(port)
        self.calibration_params = bme280.load_calibration_params(self.bus, self.address)

    def update_reading(self):
        self.calibration_params = bme280.load_calibration_params(self.bus, self.address)
        self.data = bme280.sample(self.bus, self.address, self.calibration_params)

    def get_temperature(self):
        self.update_reading()
        return self.data.temperature

    def get_humidity(self):
        self.update_reading()
        return self.data.humidity

    def get_pressure(self):
        self.update_reading()
        return self.data.pressure

    def close(self):
        self.bus.close()
