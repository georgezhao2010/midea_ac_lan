import logging
from enum import IntEnum
from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)
from ...core.crc8 import calculate

_LOGGER = logging.getLogger(__name__)


class NewProtocolParams(IntEnum):
    indoor_humidity = 0x1500
    breezeless = 0x1800
    prompt_tone = 0x1A00
    indirect_wind = 0x4200


class NewProtocolParamPack:
    @staticmethod
    def pack(param, value: bytearray, length=1, pack_len=4):
        if pack_len == 4:
            stream = bytearray([param >> 8, param & 0xFF, length]) + value
        else:
            stream = bytearray([param >> 8, param & 0xFF, 0x00, length]) + value
        return stream

    @staticmethod
    def parse(stream, pack_len=5):
        result = {}
        pos = 1
        for pack in range(0, stream[0]):
            param = (stream[pos] << 8) + stream[pos + 1]
            if pack_len == 5:
                pos += 1
            length = stream[pos + 2]
            if length > 0:
                value = stream[pos + 3: pos + 3 + length]
                result[param] = value
            pos += (3 + length)
        return result


class MessageACBase(MessageRequest):
    _message_serial = 0

    def __init__(self, message_type, body_type):
        super().__init__(
            device_type=0xAC,
            message_type=message_type,
            body_type=body_type
        )
        MessageACBase._message_serial += 1
        if MessageACBase._message_serial >= 254:
            MessageACBase._message_serial = 1
        self._message_id = MessageACBase._message_serial

    @property
    def _body(self):
        raise NotImplementedError

    @property
    def body(self):
        body = bytearray([self._body_type]) + self._body + bytearray([self._message_id])
        body.append(calculate(body))
        return body


class MessageQuery(MessageACBase):
    def __init__(self):
        super().__init__(
            message_type=MessageType.query,
            body_type=0x41)

    @property
    def _body(self):
        return bytearray([
            0x81, 0x00, 0xFF, 0x03,
            0xFF, 0x00,0x02,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00
        ])


class MessagePowerQuery(MessageACBase):
    def __init__(self):
        super().__init__(
            message_type=MessageType.query,
            body_type=0x41)

    @property
    def _body(self):
        return bytearray([
            0x21, 0x01, 0x44, 0x00, 0x01
        ])

    @property
    def body(self):
        body = bytearray([self._body_type]) + self._body
        body.append(calculate(body))
        return body


class MessageRunTimeQuery(MessagePowerQuery):
    @property
    def _body(self):
        return bytearray([
            0x21, 0x01, 0x40, 0x00, 0x01
        ])


class MessageSwitchDisplay(MessageACBase):
    def __init__(self):
        super().__init__(
            message_type=MessageType.query,
            body_type=0x41)

    @property
    def _body(self):
        return bytearray([
            0x81, 0x00, 0xFF, 0x02,
            0xFF, 0x02, 0x02,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00
        ])


class MessageNewProtocolQuery(MessageACBase):
    def __init__(self):
        super().__init__(
            message_type=MessageType.query,
            body_type=0xB1)

    @property
    def _body(self):
        query_params = [
            NewProtocolParams.indirect_wind,
            NewProtocolParams.breezeless,
            NewProtocolParams.indoor_humidity
        ]

        _body = bytearray([len(query_params)])
        for param in query_params:
            _body.extend([param >> 8, param & 0xFF])
        return _body


class MessageGeneralSet(MessageACBase):
    def __init__(self):
        super().__init__(
            message_type=MessageType.set,
            body_type=0x40)
        self.power = False
        self.prompt_tone = True
        self.mode = 0
        self.target_temperature = 20.0
        self.fan_speed = 102
        self.swing_vertical = False
        self.swing_horizontal = False
        self.boost_mode = False
        self.smart_eye = False
        self.dry = False
        self.aux_heat = False
        self.eco_mode = False
        self.temp_fahrenheit = False
        self.sleep_mode = False
        self.night_light = False
        self.natural_wind = False
        self.comfort_mode = False

    @property
    def _body(self):
        # Byte1, Power, prompt_tone
        power = 0x01 if self.power else 0
        prompt_tone = 0x40 if self.prompt_tone else 0
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
        # Byte 8, turbo
        boost_mode = 0x20 if self.boost_mode else 0
        # Byte 9 aux_heat eco_mode
        smart_eye = 0x01 if self.smart_eye else 0
        dry = 0x04 if self.dry else 0
        aux_heat = 0x08 if self.aux_heat else 0
        eco_mode = 0x80 if self.eco_mode else 0
        # Byte 10 temp_fahrenheit
        temp_fahrenheit = 0x04 if self.temp_fahrenheit else 0
        sleep_mode = 0x01 if self.sleep_mode else 0
        night_light = 0x10 if self.night_light else 0
        # Byte 17 natural_wind
        natural_wind = 0x40 if self.natural_wind else 0
        # Byte 22 comfort_mode
        comfort_mode = 0x01 if self.comfort_mode else 0

        return bytearray([
            power | prompt_tone,
            mode | target_temperature,
            fan_speed,
            0x00, 0x00, 0x00,
            swing_mode,
            boost_mode,
            smart_eye | dry | aux_heat | eco_mode,
            temp_fahrenheit | night_light | sleep_mode,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00,
            natural_wind,
            0x00, 0x00, 0x00, 0x00,
            comfort_mode
        ])


class MessageNewProtocolSet(MessageACBase):
    def __init__(self):
        super().__init__(
            message_type=MessageType.set,
            body_type=0xB0)
        self.indirect_wind = None
        self.prompt_tone = None
        self.breezeless = None

    @property
    def _body(self):
        pack_count = 0
        payload = bytearray([0x00])
        if self.breezeless is not None:
            pack_count += 1
            payload.extend(
                NewProtocolParamPack.pack(
                    param=NewProtocolParams.breezeless,
                    value=bytearray([0x01 if self.breezeless else 0x00])
                ))
        if self.indirect_wind is not None:
            pack_count += 1
            payload.extend(
                NewProtocolParamPack.pack(
                    param=NewProtocolParams.indirect_wind,
                    value=bytearray([0x02 if self.indirect_wind else 0x01])
                ))
        if self.prompt_tone is not None:
            pack_count += 1
            payload.extend(
                NewProtocolParamPack.pack(
                    param=NewProtocolParams.prompt_tone,
                    value=bytearray([0x01 if self.prompt_tone else 0x00])
            ))
        payload[0] = pack_count
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
        self.boost_mode = (body[8] & 0x20) > 0
        self.smart_eye = (body[9] & 0x01) > 0
        self.dry = (body[9] & 0x04) > 0
        self.aux_heat = (body[9] & 0x08) > 0
        self.eco_mode = (body[9] & 0x10) > 0
        self.sleep_mode = (body[10] & 0x01) > 0
        self.night_light = (body[10] & 0x10) > 0
        self.natural_wind = (body[10] & 0x40) > 0
        self.screen_display = ((body[11] & 0x7) != 0x7) and self.power
        self.comfort_mode = (body[14] & 0x1) > 0 if len(body) > 16 else False


class XA1MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        if body[13] != 0xFF:
            temperature_integer = int((body[13] - 50) / 2)
            temperature_dot = (body[18] & 0xF) * 0.1 if len(body) > 18 else 0
            if body[13] > 49:
                self.indoor_temperature = temperature_integer + temperature_dot
            else:
                self.indoor_temperature = temperature_integer - temperature_dot
        if body[14] == 0xFF:
            self.outdoor_temperature = None
        else:
            temperature_integer = int((body[14] - 50) / 2)
            temperature_dot = ((body[18] & 0xF0) >> 4) * 0.1 if len(body) > 18 else 0
            if body[14] > 49:
                self.outdoor_temperature = temperature_integer + temperature_dot
            else:
                self.outdoor_temperature = temperature_integer - temperature_dot
        self.indoor_humidity = body[17]


class XBXMessageBody(MessageBody):
    def __init__(self, body, bt):
        super().__init__(body)
        if bt == 0xb5:
            pack_len = 4
        else:
            pack_len = 5
        params = NewProtocolParamPack.parse(body[1:-1], pack_len=pack_len)
        if NewProtocolParams.indirect_wind in params:
            self.indirect_wind = (params[NewProtocolParams.indirect_wind][0] == 0x02)
        if NewProtocolParams.indoor_humidity in params:
            self.indoor_humidity = params[NewProtocolParams.indoor_humidity][0]
        if NewProtocolParams.breezeless in params:
            self.breezeless = (params[NewProtocolParams.breezeless][0] == 1)


class XC0MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[1] & 0x1) > 0
        self.mode = (body[2] & 0xe0) >> 5
        self.target_temperature = (body[2] & 0xf) + 16.0 + (0.5 if body[0x02] & 0x10 > 0 else 0.0)
        self.fan_speed = body[3] & 0x7f
        self.swing_vertical = (body[7] & 0xC) > 0
        self.swing_horizontal = (body[7] & 0x3) > 0
        self.boost_mode = (body[8] & 0x20) > 0
        self.smart_eye = (body[8] & 0x40) > 0
        self.natural_wind = (body[9] & 0x2) > 0
        self.dry = (body[9] & 0x4) > 0
        self.eco_mode = (body[9] & 0x10) > 0
        self.aux_heat = (body[9] & 0x08) > 0
        self.temp_fahrenheit = (body[10] & 0x04) > 0
        self.sleep_mode = (body[10] & 0x01) > 0
        self.night_light = (body[10] & 0x10) > 0
        if body[11] != 0xFF:
            TempInteger = int((body[11] - 50) / 2)
            TemperatureDot = (body[15] & 0xF) * 0.1
            if body[11] > 49:
                self.indoor_temperature = TempInteger + TemperatureDot
            else:
                self.indoor_temperature = TempInteger - TemperatureDot
        if body[12] == 0xFF:
            self.outdoor_temperature = None
        else:
            TempInteger = int((body[12] - 50) / 2)
            TemperatureDot = ((body[15] & 0xF0) >> 4) * 0.1
            if body[12] > 49:
                self.outdoor_temperature = TempInteger + TemperatureDot
            else:
                self.outdoor_temperature = TempInteger - TemperatureDot
        self.screen_display = ((body[14] >> 4 & 0x7) != 0x7) and self.power
        self.comfort_mode = (body[22] & 0x1) > 0 if len(body) > 24 else False


class XC1MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        if body[3] == 0x44:
            self.total_energy_consumption = XC1MessageBody.parse_consumption(
                body[4], body[5], body[6], body[7]
            )
            self.current_energy_consumption = XC1MessageBody.parse_consumption(
                body[12], body[13], body[14], body[15]
            )
            self.realtime_power = XC1MessageBody.parse_power(
                body[16], body[17], body[18]
            )
        elif body[3] == 0x40:
            pass

    @staticmethod
    def parse_value(byte):
        return (byte >> 4) * 10 + (byte & 0x0F)

    @staticmethod
    def parse_power(byte1, byte2, byte3):
        return float(XC1MessageBody.parse_value(byte1) * 10000 +
                     XC1MessageBody.parse_value(byte2) * 100 +
                     XC1MessageBody.parse_value(byte3)) / 10

    @staticmethod
    def parse_consumption(byte1, byte2, byte3, byte4):
        return float(XC1MessageBody.parse_value(byte1) * 1000000 +
                     XC1MessageBody.parse_value(byte2) * 10000 +
                     XC1MessageBody.parse_value(byte3) * 100 +
                     XC1MessageBody.parse_value(byte4)) / 100


class MessageACResponse(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[self.HEADER_LENGTH: -1]
        if self._body_type == 0xA0:
            self._body = XA0MessageBody(body)
            self.power = self._body.power
            self.target_temperature = self._body.target_temperature
            self.mode = self._body.mode
            self.fan_speed = self._body.fan_speed
            self.swing_vertical = self._body.swing_vertical
            self.swing_horizontal = self._body.swing_horizontal
            self.boost_mode = self._body.boost_mode
            self.smart_eye = self._body.smart_eye
            self.dry = self._body.dry
            self.aux_heat = self._body.aux_heat
            self.eco_mode = self._body.eco_mode
            self.sleep_mode = self._body.sleep_mode
            self.night_light = self._body.night_light
            self.natural_wind = self._body.natural_wind
            self.screen_display = self._body.screen_display
            self.comfort_mode = self._body.comfort_mode
        elif self._body_type == 0xA1:
            self._body = XA1MessageBody(body)
            if hasattr(self._body, "indoor_temperature"):
                self.indoor_temperature = self._body.indoor_temperature
            self.outdoor_temperature = self._body.outdoor_temperature
            self.indoor_humidity = self._body.indoor_humidity
        elif self._body_type in [0xB0, 0xB1, 0xB5]:
            self._body = XBXMessageBody(body, self._body_type)
            if hasattr(self._body, "indirect_wind"):
                self.indirect_wind = self._body.indirect_wind
            if hasattr(self._body, "indoor_humidity"):
                self.indoor_humidity = self._body.indoor_humidity
            if hasattr(self._body, "breezeless"):
                self.breezeless = self._body.breezeless
        elif self._body_type == 0xC0:
            self._body = XC0MessageBody(body)
            self.power = self._body.power
            self.mode = self._body.mode
            self.target_temperature = self._body.target_temperature
            self.fan_speed = self._body.fan_speed
            self.swing_vertical = self._body.swing_vertical
            self.swing_horizontal = self._body.swing_horizontal
            self.boost_mode = self._body.boost_mode
            self.smart_eye = self._body.smart_eye
            self.natural_wind = self._body.natural_wind
            self.dry = self._body.dry
            self.aux_heat = self._body.aux_heat
            self.eco_mode = self._body.eco_mode
            self.temp_fahrenheit = self._body.temp_fahrenheit
            self.sleep_mode = self._body.sleep_mode
            self.night_light = self._body.night_light
            if hasattr(self._body, "indoor_temperature"):
                self.indoor_temperature = self._body.indoor_temperature
            self.outdoor_temperature = self._body.outdoor_temperature
            self.screen_display = self._body.screen_display
            self.comfort_mode = self._body.comfort_mode
        elif self._body_type == 0xC1:
            self._body = XC1MessageBody(body)
            if hasattr(self._body, "total_energy_consumption"):
                self.total_energy_consumption = self._body.total_energy_consumption
            if hasattr(self._body, "current_energy_consumption"):
                self.current_energy_consumption = self._body.current_energy_consumption
            if hasattr(self._body, "realtime_power"):
                self.realtime_power = self._body.realtime_power
