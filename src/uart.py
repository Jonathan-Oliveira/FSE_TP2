import serial
from modbus import Modbus


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
            self.serial.write(msg)

    def receive(self):
        self.check_connection()
        if self.is_conected:
            buffer = self.serial.read(9)
            response = self.modbus.decode_message(buffer)
            return response

    def send_and_receive(self, message, value=None):
        self.send(message, value)
        response = self.receive()
        count = 0
        while not response and count < 3:
            response = self.receive()
            count += 1
        return response

    def close(self):
        self.serial.close()
        self.is_conected = self.serial.is_open
        print("Conexão UART fechada")
