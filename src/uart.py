import serial
from modbus import Modbus
from time import sleep


class Uart:
    def __init__(self):
        self.serial = serial.Serial("/dev/serial0", 9600, timeout=0.1)
        self.modbus = Modbus()
        self.is_conected = False
        self.check_connection()

    def check_connection(self):
        if not self.is_conected and self.serial.is_open:
            print("Conexão UART estabelecida :)")
        self.is_conected = self.serial.is_open
        if not self.is_conected:
            print("Erro na conexão UART :(")

    def send(self, message, value=None):
        self.check_connection()
        if self.is_conected:
            msg = self.modbus.code_message(message, value)
            if msg:
                self.serial.write(msg)

    def receive(self):
        self.check_connection()
        if self.is_conected:
            sleep(0.1)
            buffer = self.serial.read(9)
            message, value = self.modbus.decode_message(buffer)
            return message, value
        return None, None

    def close(self):
        self.serial.close()
        self.is_conected = self.serial.is_open
        print("Conexão UART fechada")
