import smbus2
import bme280


class BME:
    def __init__(self, address=0x76, port=1):
        self.address = address
        self.port = port
        self.bus = smbus2.SMBus(port)

    def get_reading(self):
        self.calibration_params = bme280.load_calibration_params(
            self.bus, self.address
        )

        data = bme280.sample(self.bus, self.address, self.calibration_params)
        return data.temperature, data.humidity, data.pressure

    def get_temperature(self):
        data = bme280.sample(self.bus, self.address, self.calibration_params)
        return data.temperature

    def get_humidity(self):
        data = bme280.sample(self.bus, self.address, self.calibration_params)
        return data.humidity

    def get_pressure(self):
        data = bme280.sample(self.bus, self.address, self.calibration_params)
        return data.pressure

    def close(self):
        self.bus.close()
