from crc16 import calculate_crc16, check_crc16, InvalidCRC
import struct


class Modbus:
    def __init__(self):
        registration_number = [3, 5, 8, 0]
        self.commands = {
            # to get a message
            "get_internal_temperature": [0x01, 0x23, 0xC1, *registration_number],
            "get_reference_temperature": [0x01, 0x23, 0xC2, *registration_number],
            "get_user_command": [0x01, 0x23, 0xC3, *registration_number],
            # to send message
            "send_reference_temperature": [0x01, 0x16, 0xD2, *registration_number],
            "ambiente_temperature": [0x01, 0x16, 0xD6, *registration_number],
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
        self.response_messages = {
            0xC1: "internal_temperature",
            0xC2: "reference_temperature",
            0xC3: "get_user_command",
        }
        self.update_mesages = {}

    def code_message(self, command, value=None):
        try:
            message_bytes = bytes(self.commands.get(command, None))
        except TypeError:
            return None
        if value:
            if type(value) == int:
                value = struct.pack("<i", value)
            elif type(value) == float:
                value = struct.pack("<f", round(value, 2))
            message_bytes = message_bytes + value
        crc_code = calculate_crc16(message_bytes).to_bytes(2, "little")
        return message_bytes + crc_code

    def decode_message(self, message):
        length = len(message)
        if length == 9:
            try:
                check_crc16(message)
            except InvalidCRC:
                return None, None
            start_byte, code, sub_code, data = (
                message[0],
                message[1],
                message[2],
                message[3:7],
            )
            if start_byte == 0x00:
                if code == 0x23:
                    if sub_code in [0xC1, 0xC2]:
                        return self.response_messages.get(sub_code), round(
                            struct.unpack("<f", data)[0], 2
                        )
                    if sub_code in [0xC3]:
                        return self.response_messages.get(
                            sub_code
                        ), self.user_messages.get(struct.unpack("<i", data)[0])
                        # if user comand apply the function
                elif code == 0x16:
                    return None, None
        return None, None
