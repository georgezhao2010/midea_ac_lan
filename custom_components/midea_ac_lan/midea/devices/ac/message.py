import logging
from enum import IntEnum, Enum
from ...core.message import (
    NewProtocolParamPack,
    NewProtocolParamParser,
    MessageRequest,
    MessageResponse,
    MessageBody,
    MessageLenError,
    MessageCheckSumError
)

_LOGGER = logging.getLogger(__name__)


class FrameType(IntEnum):
    set = 0x02,
    query = 0x03,
    notify = 0x05


class MessageStatus(Enum):
    power = "power"
    mode = "mode"
    target_temperature = "target_temperature"
    fan_speed = "fan_speed"
    swing_vertical = "swing_vertical"
    swing_horizontal = "swing_horizontal"
    eco_mode = "eco_mode"
    aux_heat = "aux_heat"
    temp_fahrenheit = "temp_fahrenheit"
    indoor_temperature = "indoor_temperature"
    outdoor_temperature = "outdoor_temperature"
    indirect_wind = "indirect_wind"
    comfort_mode = "comfort_mode"


class NewProtocolParams(IntEnum):
    indirect_wind = 0x42
    prompt_tone = 0x1A


class MessageQuery(MessageRequest):
    def __init__(self):
        super().__init__(
            device_type=0xAC,
            frame_type=FrameType.query,
            msg_type=0x41)

    @property
    def _payload(self):
        return bytearray([
            0x81, 0x00, 0xFF, 0x03, 0xFF, 0x00,
            # 0x02 - Indoor Temperature; 0x03 - Outdoor Temperature
            0x02,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00
        ])


class MessageRequestFeature(MessageRequest):
    def __init__(self):
        super().__init__(
            device_type=0xAC,
            frame_type=FrameType.query,
            msg_type=0xB5)

    @property
    def _payload(self):
        return bytearray([
            0x01, 0x11
        ])


class MessageGeneralSet(MessageRequest):
    def __init__(self):
        super().__init__(
            device_type=0xAC,
            frame_type=FrameType.set,
            msg_type=0x40)
        self.power = False
        self.prompt_tone = True
        self.mode = 0
        self.target_temperature = 20.0
        self.fan_speed = 102
        self.swing_vertical = False
        self.swing_horizontal = False
        self.eco_mode = False
        self.aux_heat = False
        self.sleep_mode = False
        self.turbo_mode = False
        self.temp_fahrenheit = False
        self.lcd_display = True
        self.comfort_mode = False

    @property
    def _payload(self):
        # Byte1, Power, prompt_tone
        power = 0x01 if self.power else 0
        prompt_tone = 0x42 if self.prompt_tone else 0
        # Byte2, mode target_temperature
        mode = (self.mode << 5) & 0xe0
        target_temperature = (int(self.target_temperature) & 0xf) | \
                             (0x10 if int(round(self.target_temperature * 2)) % 2 != 0 else 0)
        # Byte 3, fan_speed
        fan_speed = self.fan_speed & 0x7f
        # Byte 7, swing_mode
        swing_mode = 0x30 | \
                     (0x0c if self.swing_vertical else 0) | \
                     (0x03 if self.swing_horizontal else 0)
        # Byte 9 eco_mode aux_heat
        eco_mode = 0x80 if self.eco_mode else 0
        aux_heat = 0x08 if self.aux_heat else 0
        # Byte 10 temp_fahrenheit
        sleep_mode = 0x01 if self.sleep_mode else 0
        turbo_mode = 0x02 if self.turbo_mode else 0
        temp_fahrenheit = 0x04 if self.temp_fahrenheit else 0
        lcd_display = 0x10 if self.lcd_display else 0
        # Byte 22 comfort_mode
        comfort_mode = 0x01 if self.comfort_mode else 0

        return bytearray([
            power | prompt_tone,
            mode | target_temperature,
            fan_speed,
            0x00, 0x00, 0x00,
            swing_mode,
            0x00,
            eco_mode | aux_heat,
            sleep_mode | turbo_mode | temp_fahrenheit | lcd_display,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00,
            comfort_mode
        ])


class MessageNewProtocolSet(MessageRequest):
    def __init__(self):
        super().__init__(
            device_type=0xAC,
            frame_type=FrameType.set,
            msg_type=0xB0)
        self.indirect_wind = None
        self.prompt_tone = None

    @property
    def _payload(self):
        payload = bytearray([0x02])
        if self.indirect_wind is not None:
            indirect_wind = NewProtocolParamPack(
                param=NewProtocolParams.indirect_wind,
                value=bytearray([0x02 if self.indirect_wind else 0x01]))
            payload.extend(indirect_wind.serialize())
        if self.prompt_tone is not None:
            prompt_tone = NewProtocolParamPack(
                param=NewProtocolParams.prompt_tone,
                value=bytearray([0x01 if self.prompt_tone else 0x00]))
            payload.extend(prompt_tone.serialize())
        return payload


class XA0MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[1] & 0x1) > 0
        self.target_temperature = ((body[1] & 0x3E) >> 1) - 4 + 16.0 + (0.5 if body[1] & 0x40 > 0 else 0.0)
        self.mode = (body[2] & 0xe0) >> 5
        self.fan_speed = body[3] & 0x7f
        self.swing_vertical = (body[7] & 0xC) > 0
        self.swing_horizontal = (body[7] & 0x3) > 0
        self.eco_mode = (body[9] & 0x10) > 0
        self.aux_heat = (body[9] & 0x08) > 0
        self.comfort_mode = (body[14] & 0x1) == 0x1


class XA1MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        TempInteger = int((body[13] - 50) / 2)
        TemperatureDot = (body[18] & 0xF) * 0.1 if len(body) > 18 else 0
        if body[13] > 49:
            self.indoor_temperature = TempInteger + TemperatureDot
        else:
            self.indoor_temperature = TempInteger - TemperatureDot
        TempInteger = int((body[14] - 50) / 2)
        TemperatureDot = ((body[18] & 0xF0) >> 4) * 0.1 if len(body) > 18 else 0
        if body[14] > 49:
            self.outdoor_temperature = TempInteger + TemperatureDot
        else:
            self.outdoor_temperature = TempInteger - TemperatureDot


class XB0MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.indirect_wind = (body[6] & 0x2) == 0x2


class XB5MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.indirect_wind = (body[5] & 0x2) == 0x2


class XC0MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[1] & 0x1) > 0
        self.mode = (body[2] & 0xe0) >> 5
        self.target_temperature = (body[2] & 0xf) + 16.0 + (0.5 if body[0x02] & 0x10 > 0 else 0.0)
        self.fan_speed = body[3] & 0x7f
        self.swing_vertical = (body[7] & 0xC) > 0
        self.swing_horizontal = (body[7] & 0x3) > 0
        self.eco_mode = (body[9] & 0x10) > 0
        self.aux_heat = (body[9] & 0x08) > 0
        self.temp_fahrenheit = (body[10] & 0x04) > 0
        self.indoor_temperature = int((body[11] - 50) / 2) + (body[15] & 0xF) * 0.1
        self.outdoor_temperature = \
            0.0 if body[12] == 0xFF else int((body[12] - 50) / 2) + ((body[15] & 0xF0) >> 4) * 0.1
        self.comfort_mode = (body[22] & 0x1) > 0 if len(body) > 22 else False


class MessageACResponse(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[10: -2]
        if self._msg_type == 0xA0:
            self._body = XA0MessageBody(body)
            self.power = self._body.power
            self.target_temperature = self._body.target_temperature
            self.mode = self._body.mode
            self.fan_speed = self._body.fan_speed
            self.swing_vertical = self._body.swing_vertical
            self.swing_horizontal = self._body.swing_horizontal
            self.eco_mode = self._body.eco_mode
            self.aux_heat = self._body.aux_heat
            self.comfort_mode = self._body.comfort_mode
        elif self._msg_type == 0xA1:
            self._body = XA1MessageBody(body)
            self.indoor_temperature = self._body.indoor_temperature
            self.outdoor_temperature = self._body.outdoor_temperature
        elif self._msg_type == 0xB0:
            self._body = XB0MessageBody(body)
            self.indirect_wind = self._body.indirect_wind
        elif self._msg_type == 0xB5:
            self._body = XB5MessageBody(body)
            self.indirect_wind = self._body.indirect_wind
        elif self._msg_type == 0xC0:
            self._body = XC0MessageBody(body)
            self.power = self._body.power
            self.mode = self._body.mode
            self.target_temperature = self._body.target_temperature
            self.fan_speed = self._body.fan_speed
            self.swing_vertical = self._body.swing_vertical
            self.swing_horizontal = self._body.swing_horizontal
            self.eco_mode = self._body.eco_mode
            self.aux_heat = self._body.aux_heat
            self.temp_fahrenheit = self._body.temp_fahrenheit
            self.indoor_temperature = self._body.indoor_temperature
            self.outdoor_temperature = self._body.outdoor_temperature
            self.comfort_mode = self._body.comfort_mode
        else:
            self._body = MessageBody(body)