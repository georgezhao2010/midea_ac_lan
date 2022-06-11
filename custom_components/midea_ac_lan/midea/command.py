import logging
import datetime
from .crc8 import calculate

_LOGGER = logging.getLogger(__name__)


class CommandRequest:
    def __init__(self):
        self._header = bytearray([
            0xaa,
            # request is 0x20; setting is 0x23
            0x00,
            # device type
            0xac,
            0x00, 0x00, 0x00, 0x00, 0x00,
            0x00,
            # request is 0x03; setting is 0x02
            0x03
        ])
        self._body = bytearray([
            # Byte0 - Data request/response type: 0x41 - check status; 0x40 - Set up
            0x41,
            # Byte1
            0x81,
            # Byte2 - operational_mode
            0x00,
            # Byte3
            0xff,
            # Byte4
            0x03,
            # Byte5
            0xff,
            # Byte6
            0x00,
            # Byte7 - Room Temperature Request: 0x02 - indoor_temperature, 0x03 - outdoor_temperature
            # when set, this is swing_mode
            0x02,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ])
        serial = int(datetime.datetime.now().microsecond % 1000 / 4)
        if serial == 0 or serial == 254:
            serial = 1
        self._body[-1] = serial

    @staticmethod
    def checksum(data):
        return (~ sum(data) + 1) & 0xff

    def finalize(self):
        self._header[1] = len(self._body) + 11
        output = {
            "header": self._header.hex(),
            "body": self._body.hex(),
            "type": int(self._header[9] << 8) + int(self._body[0])
        }
        _LOGGER.debug(f"Send message: {str(output)}")
        data = self._header
        data.extend(self._body)
        data.append(calculate(self._body))
        data.append(self.checksum(data[1:]))
        return data


class CommandRequestIndirectWind(CommandRequest):
    def __init__(self):
        self._header = bytearray([
            0xaa,
            # request is 0x20; setting is 0x23
            0x23,
            # device type
            0xac,
            0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x02
        ])
        self._body = bytearray([
            0xB0,
            0x02,
            0x42,
            0x00, 0x01,
            0x02,  #0x01关闭防直吹
            0x1A, 0x00, 0x01,
            0x01,  #0x00关闭提示音
            0x00
        ])

    def finalize(self):
        self._header[1] = len(self._body) + 11
        output = {
            "header": self._header.hex(),
            "body": self._body.hex(),
            "type": int(self._header[9] << 8) + int(self._body[0])
        }
        _LOGGER.debug(f"Send message: {str(output)}")
        data = self._header
        data.extend(self._body)
        data.append(calculate(self._body))
        data.append(self.checksum(data[1:]))
        return data

    def set_prompt_tone(self, prompt_tone):
        self._body[9] = 0x01 if prompt_tone else 0x00

    def set_indirect_wind(self, indirect_wind):
        self._body[5] = 0x02 if indirect_wind else 0x01


class CommandSet(CommandRequest):
    def __init__(self):
        super().__init__()
        self._header[1] = 0x23
        self._header[9] = 0x02
        self._body[0] = 0x40
        self._body[4] = 0x02
        self._body[6] = 0x02

    def set_prompt_tone(self, prompt_tone: bool):
        self._body[1] &= (~0x40)  # Clear the audible bits
        self._body[1] |= 0x40 if prompt_tone else 0

    def set_power(self, power: bool):
        self._body[1] &= (~0x01)  # Clear the power bit
        self._body[1] |= 0x01 if power else 0

    def set_mode(self, mode: int):
        self._body[2] &= (~0xe0)  # Clear the mode bit
        self._body[2] |= (mode << 5) & 0xe0

    def set_fan_speed(self, fan_speed):
        self._body[3] = fan_speed & 0x7f

    def set_swing(self, swing_vertical, swing_horizontal):
        mode = 0
        if swing_vertical:
            mode |= 0x0c
        if swing_horizontal:
            mode |= 0x03
        self._body[7] = 0x30  # Clear the mode bit
        self._body[7] |= mode & 0x3f

    def set_target_temperature(self, temperature: float):
        self._body[2] &= ~ 0x0f
        self._body[2] |= (int(temperature) & 0xf)
        if int(round(temperature * 2)) % 2 != 0:
            self._body[2] |= 0x10
        else:
            self._body[2] &= (~0x10)

    def set_comfort_mode(self, comfort_mode):
        self._body[22] &= (~0x01)
        self._body[22] |= 0x01 if comfort_mode else 0

    def set_eco_mode(self, eco_mode):
        self._body[9] = 0xff if eco_mode else 0

    def set_indirect_wind(self, indirect_wind):
        self._body[22] &= (~0x10)
        self._body[22] |= 0x10 if indirect_wind else 0

    def set_fahrenheit(self, fahrenheit: bool):
        self._body[10] &= (~0x04)
        self._body[10] |= 0x04 if fahrenheit else 0



