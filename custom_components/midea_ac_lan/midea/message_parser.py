import logging

_LOGGER = logging.getLogger(__name__)


class XAAMessage:
    def __init__(self, body):
        self._body = body

    @property
    def body(self):
        return self._body

    @property
    def power(self):
        return False

    @property
    def mode(self):
        return 0

    @property
    def fan_speed(self):
        return 0

    @property
    def swing_vertical(self):
        return False

    @property
    def swing_horizontal(self):
        return False

    @property
    def target_temperature(self):
        return 0.0

    @property
    def indoor_temperature(self):
        return 0.0

    @property
    def outdoor_temperature(self):
        return 0.0

    @property
    def comfort_mode(self):
        return False

    @property
    def eco_mode(self):
        return False

    @property
    def indirect_wind(self):
        return False

    @property
    def aux_heat(self):
        return False

    @property
    def temp_fahrenheit(self):
        return False

    def __str__(self) -> str:
        return self._body.hex()


class X03XC0Message(XAAMessage):
    def __init__(self, body):
        super().__init__(body)

    @property
    def power(self):
        return (self._body[1] & 0x1) > 0

    @property
    def mode(self):
        return (self._body[2] & 0xe0) >> 5

    @property
    def fan_speed(self):
        return self._body[3] & 0x7f

    @property
    def swing_vertical(self):
        return (self._body[7] & 0xC) > 0

    @property
    def swing_horizontal(self):
        return (self._body[7] & 0x3) > 0

    @property
    def target_temperature(self):
        return (self._body[2] & 0xf) + 16.0 + (0.5 if self._body[0x02] & 0x10 > 0 else 0.0)

    @property
    def indoor_temperature(self):
        return int((self._body[11] - 50) / 2) + (self._body[15] & 0xF) * 0.1

    @property
    def outdoor_temperature(self):
        return int((self._body[12] - 50) / 2) + ((self._body[15] & 0xF0) >> 4) * 0.1

    @property
    def comfort_mode(self):
        return  (self._body[22] & 0x1) > 0 if len(self._body) > 22 else False

    @property
    def eco_mode(self):
        return (self._body[9] & 0x10) > 0

    @property
    def aux_heat(self):
        return (self._body[9] & 0x08) > 0

    @property
    def temp_fahrenheit(self):
        return (self._body[10] & 0x04) > 0

    @property
    def indirect_wind(self):
        return (self._body[14] & 0x10) > 0 if len(self._body) > 14 else False


class X04XA1Message(XAAMessage):
    def __init__(self, body):
        super().__init__(body)

    @property
    def indoor_temperature(self):
        indoorTempInteger = int((self._body[13] - 50) / 2)
        indoorTemperatureDot = (self._body[18] & 0xF) * 0.1 if len(self._body) > 18 else 0
        if self._body[13] > 49:
            return indoorTempInteger + indoorTemperatureDot
        else:
            return indoorTempInteger - indoorTemperatureDot

    @property
    def outdoor_temperature(self):
        outdoorTempInteger = int((self._body[14] - 50) / 2)
        outdoorTemperatureDot = ((self._body[18] & 0xF0) >> 4) * 0.1 if len(self._body) > 18 else 0
        if self._body[14] > 49:
            return outdoorTempInteger + outdoorTemperatureDot
        else:
            return outdoorTempInteger - outdoorTemperatureDot


class X05XA0Message(XAAMessage):
    def __init__(self, body):
        super().__init__(body)

    @property
    def prompt_tone(self):
        return self._body[2] & 0x42 > 0

    @property
    def power(self):
        return (self._body[1] & 0x1) > 0

    @property
    def mode(self):
        return (self._body[2] & 0xe0) >> 5

    @property
    def fan_speed(self):
        return self._body[3] & 0x7f

    @property
    def swing_vertical(self):
        return (self._body[7] & 0xC) > 0

    @property
    def swing_horizontal(self):
        return (self._body[7] & 0x3) > 0

    @property
    def target_temperature(self):
        return ((self._body[1] & 0x3E) >> 1) - 4 + 16.0 + (0.5 if self._body[1] & 0x40 > 0 else 0.0)

    @property
    def comfort_mode(self):
        return (self._body[14] & 0x1) == 0x1

    @property
    def eco_mode(self):
        return (self._body[9] & 0x10) > 0

    @property
    def aux_heat(self):
        return (self._body[9] & 0x08) > 0

    @property
    def temp_fahrenheit(self):
        return (self._body[10] & 0x04) > 0

    @property
    def indirect_wind(self):
        return (self._body[14] & 0x10) > 0


class X05XB5Message(XAAMessage):
    def __init__(self, body):
        super().__init__(body)

    @property
    def indirect_wind(self):
        return (self._body[5] & 0x2) == 0x2


class X02XB0Message(XAAMessage):
    @property
    def indirect_wind(self):
        return (self._body[6] & 0x2) == 0x2


class UnknownMessage(XAAMessage):
    pass


class MessageParser:
    def __init__(self, message):
        _LOGGER.debug(f"Parsing command: {message.hex()}")
        self._header = message[:10]
        body = message[10: -2]
        msg_type = self._header[9]
        if (msg_type == 0x02 or msg_type == 0x03) and body[0] == 0xc0:
            self._body = X03XC0Message(body)
        elif msg_type == 0x04 and body[0] == 0xA1:
            self._body = X04XA1Message(body)
        elif msg_type == 0x05 and body[0] == 0xA0:
            self._body = X05XA0Message(body)
        elif msg_type == 0x05 and body[0] == 0xB5:
            self._body = X05XB5Message(body)
        elif msg_type == 0x02 and body[0] == 0xb0:
            self._body = X02XB0Message(body)
        else:
            self._body = UnknownMessage(body)

    @property
    def msg_type(self):
        return int(self._header[9] << 8) + int(self._body.body[0])

    @property
    def power(self):
        return self._body.power

    @property
    def mode(self):
        return self._body.mode

    @property
    def fan_speed(self):
        return self._body.fan_speed

    @property
    def swing_vertical(self):
        return self._body.swing_vertical

    @property
    def swing_horizontal(self):
        return self._body.swing_horizontal

    @property
    def target_temperature(self):
        return self._body.target_temperature

    @property
    def indoor_temperature(self):
        return self._body.indoor_temperature

    @property
    def outdoor_temperature(self):
        return self._body.outdoor_temperature

    @property
    def comfort_mode(self):
        return self._body.comfort_mode

    @property
    def eco_mode(self):
        return self._body.eco_mode

    @property
    def aux_heat(self):
        return self._body.aux_heat

    @property
    def temp_fahrenheit(self):
        return self._body.temp_fahrenheit

    @property
    def indirect_wind(self):
        return self._body.indirect_wind

    def __str__(self) -> str:
        output = {
            "header": self._header.hex(),
            "body": str(self._body),
            "type": "%#x" % self.msg_type
        }
        return str(output)
