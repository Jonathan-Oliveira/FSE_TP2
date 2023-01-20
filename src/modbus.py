from crc16 import calculate_crc16, check_crc16
import struct

# self.commands = {
#     # to get a message
#     "internal_temperature": [0x01, 0x23, 0xC1, registration_number],
#     "reference_temperature": [0x01, 0x23, 0xC2, registration_number],
#     "ambiente_temperature": [0x01, 0x23, 0xD6, registration_number],
#     "user_commands": [0x01, 0x23, 0xC3, registration_number, 0],
#     # to send message
#     "system_state_on": [0x01, 0x16, 0xD3, registration_number, 1],
#     "system_state_off": [0x01, 0x16, 0xD3, registration_number, 0],
#     "control_mode_fixed": [0x01, 0x16, 0xD4,registration_number, 0],
#     "control_mode_curve": [0x01, 0x16, 0xD4,registration_number, 1],
#     "system_work_on": [0x01, 0x16, 0xD5,registration_number, 1],
#     "system_work_off": [0x01, 0x16, 0xD5,registration_number, 0],
#     "control_signal": [0x01, 0x16, 0xD1, registration_number],
#     "reference_signal": [0x01, 0x16, 0xD2, registration_number],
# }


class Modbus:
    def __init__(self):
        registration_number = [3, 5, 8, 0]
        self.commands = {
            # to get a message
            "internal_temperature": [0x01, 0x23, 0xC1, *registration_number],
            "get_reference_temperature": [
                0x01,
                0x23,
                0xC2,
                *registration_number,
            ],
            "get_user_command": [0x01, 0x23, 0xC3, *registration_number],
            # to send message
            "send_reference_temperature": [
                0x01,
                0x23,
                0xD2,
                *registration_number,
            ],
            "ambiente_temperature": [0x01, 0x23, 0xD6, *registration_number],
            "system_state_on": [0x01, 0x16, 0xD3, *registration_number, 1],
            "system_state_off": [0x01, 0x16, 0xD3, *registration_number, 0],
            "control_mode_fixed": [0x01, 0x16, 0xD4, *registration_number, 0],
            "control_mode_curve": [0x01, 0x16, 0xD4, *registration_number, 1],
            "system_work_on": [0x01, 0x16, 0xD5, *registration_number, 1],
            "system_work_off": [0x01, 0x16, 0xD5, *registration_number, 0],
            "control_signal": [0x01, 0x16, 0xD1, *registration_number],
            "reference_signal": [0x01, 0x16, 0xD2, *registration_number],
        }
        self.user_messages = {
            0xA1: "turn_on_oven",
            0xA2: "turn_off_oven",
            0xA3: "turn_on_heating",
            0xA4: "turn_off_heating",
            0xA5: "change_mode",
        }

    def code_message(self, command, value=None):
        message_bytes = bytes(self.commands[command])
        if value:
            # value = value.to_bytes(4, "little", signed=True)
            if type(value) == int:
                value = struct.pack("<i", value)
            elif type(value) == float:
                value = struct.pack("<f", value)
            message_bytes = message_bytes + value
        crc_code = calculate_crc16(message_bytes).to_bytes(2, "little")
        return message_bytes + crc_code

    def decode_message(self, message):
        if len(message) == 9:
            data = message[3:7]
            code = message[3]
            print("data: ", data)
            print("code: ", code)
            if check_crc16(message):
                if code in [0xC1, 0xC2]:
                    return round(struct.unpack("<f", data)[0], 2)
                return self.user_messages.get(
                    code, struct.unpack("<i", data)[0]
                )
            else:
                print("CRC inválido")
                return None
        else:
            print("Mensagem inválida")
            return None

    # def crc_is_valid(self, buffer):
    #     received_crc = buffer[7:9]
    #     crc = calculate_crc16(buffer[0:7], 7).to_bytes(2, "little")

    #     return received_crc == crc
