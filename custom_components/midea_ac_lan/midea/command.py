import logging
import datetime
import copy
from .crc8 import calculate

_LOGGER = logging.getLogger(__name__)


class CommandRequest:
    _message_serial = 0

    def __init__(self, device_type=0xac):
        self._header = bytearray([
            0xaa,
            # length
            0x20,
            # device type
            device_type,
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
            0x00, 0x00, 0x00, 0x00, 0x00
        ])

    @staticmethod
    def checksum(data):
        return (~ sum(data) + 1) & 0xff

    def finalize(self):
        self._header[1] = len(self._body) + 10 + 1
        CommandRequest._message_serial += 1
        if CommandRequest._message_serial > 254:
            CommandRequest._message_serial = 1
        self._body[-1] = CommandRequest._message_serial
        data = copy.deepcopy(self._header)
        data.extend(self._body)
        data.append(calculate(self._body))
        data.append(self.checksum(data[1:]))
        _LOGGER.debug(f"Finalized command: {data.hex()}")
        return data

    def __str__(self) -> str:
        output = {
            "header": self._header.hex(),
            "body": self._body.hex(),
            "type": "%#x" % (int(self._header[9] << 8) + int(self._body[0]))
        }
        return str(output)


class CommandFeatureRequest(CommandRequest):
    def __init__(self, device_type=0xac):
        super().__init__(device_type=device_type)
        self._body = bytearray([
            0xB5,
            0x01,
            0x11,
            0x00
        ])


class CommandSet(CommandRequest):
    def __init__(self, device_type=0xac):
        super().__init__(device_type=device_type)
        self._header[9] = 0x02


class CommandNewProtocolSet(CommandSet):
    def __init__(self, prompt_tone=True, device_type=0xac):
        super().__init__(device_type=device_type)
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
        self._body[9] = 0x01 if prompt_tone else 0

    def set_indirect_wind(self, indirect_wind):
        self._body[5] = 0x02 if indirect_wind else 0x01


class CommandGeneralSet(CommandSet):
    def __init__(self, prompt_tone=True, device_type=0xac):
        super().__init__(device_type=device_type)
        self._body[0] = 0x40
        self._body[1] = 0xC2 if prompt_tone else 0x80
        self._body.extend(bytearray([0x00, 0x00, 0x00]))

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
        self._body[9] &= (~0xFF)
        self._body[9] |= 0xFF if eco_mode else 0

    def set_aux_heat(self, aux_heat):
        self._body[9] &= (~0x08)
        self._body[9] |= 0x08 if aux_heat else 0



