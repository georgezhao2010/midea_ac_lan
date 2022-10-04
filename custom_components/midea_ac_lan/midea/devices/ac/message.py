from enum import IntEnum
from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
    NewProtocolMessageBody
)
from ...core.crc8 import calculate


class NewProtocolTags(IntEnum):
    indoor_humidity = 0x0015
    screen_display = 0x0017
    breezeless = 0x0018
    prompt_tone = 0x001A
    indirect_wind = 0x0042
    fresh_air_1 = 0x0233
    fresh_air_2 = 0x004b


class MessageACBase(MessageRequest):
    _message_serial = 0

    def __init__(self, device_protocol_version, message_type, body_type):
        super().__init__(
            device_protocol_version=device_protocol_version,
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
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query,
            body_type=0x41)

    @property
    def _body(self):
        return bytearray([
            0x81, 0x00, 0xFF, 0x03,
            0xFF, 0x00, 0x02,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00
        ])


class MessagePowerQuery(MessageACBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
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


class MessageSwitchDisplay(MessageACBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
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
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query,
            body_type=0xB1)

    @property
    def _body(self):
        query_params = [
            NewProtocolTags.indirect_wind,
            NewProtocolTags.breezeless,
            NewProtocolTags.indoor_humidity,
            NewProtocolTags.screen_display,
            NewProtocolTags.fresh_air_1,
            NewProtocolTags.fresh_air_2
        ]

        _body = bytearray([len(query_params)])
        for param in query_params:
            _body.extend([param & 0xFF, param >> 8])
        return _body


class MessageGeneralSet(MessageACBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
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
        self.natural_wind = False
        self.frost_protect = False
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
        # Byte 17 natural_wind
        natural_wind = 0x40 if self.natural_wind else 0
        # Byte 21 frost_protect
        frost_protect = 0x80 if self.frost_protect else 0
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
            temp_fahrenheit | sleep_mode,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00,
            natural_wind,
            0x00, 0x00, 0x00,
            frost_protect,
            comfort_mode
        ])


class MessageNewProtocolSet(MessageACBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.set,
            body_type=0xB0)
        self.indirect_wind = None
        self.prompt_tone = None
        self.breezeless = None
        self.screen_display = None
        self.fresh_air_1 = None
        self.fresh_air_2 = None

    @property
    def _body(self):
        pack_count = 0
        payload = bytearray([0x00])
        if self.breezeless is not None:
            pack_count += 1
            payload.extend(
                NewProtocolMessageBody.pack(
                    param=NewProtocolTags.breezeless,
                    value=bytearray([0x01 if self.breezeless else 0x00])
                ))
        if self.indirect_wind is not None:
            pack_count += 1
            payload.extend(
                NewProtocolMessageBody.pack(
                    param=NewProtocolTags.indirect_wind,
                    value=bytearray([0x02 if self.indirect_wind else 0x01])
                ))
        if self.prompt_tone is not None:
            pack_count += 1
            payload.extend(
                NewProtocolMessageBody.pack(
                    param=NewProtocolTags.prompt_tone,
                    value=bytearray([0x01 if self.prompt_tone else 0x00])
                ))
        if self.screen_display is not None:
            pack_count += 1
            payload.extend(
                NewProtocolMessageBody.pack(
                    param=NewProtocolTags.screen_display,
                    value=bytearray([0x64 if self.screen_display else 0x00])
                ))
        if self.fresh_air_1 is not None and len(self.fresh_air_1) == 2:
            pack_count += 1
            fresh_air_power = 2 if self.fresh_air_1[0] > 0 else 1
            fresh_air_fan_speed = self.fresh_air_1[1]
            payload.extend(
                NewProtocolMessageBody.pack(
                    param=NewProtocolTags.fresh_air_1,
                    value=bytearray([
                        fresh_air_power,
                        fresh_air_fan_speed,
                        0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00
                    ])
                ))
        if self.fresh_air_2 is not None and len(self.fresh_air_2) == 2:
            pack_count += 1
            fresh_air_power = 1 if self.fresh_air_2[0] > 0 else 0
            fresh_air_fan_speed = self.fresh_air_2[1]
            payload.extend(
                NewProtocolMessageBody.pack(
                    param=NewProtocolTags.fresh_air_2,
                    value=bytearray([
                        fresh_air_power,
                        fresh_air_fan_speed,
                        0xFF
                    ])
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
        self.natural_wind = (body[10] & 0x40) > 0
        self.full_dust = (body[13] & 0x20) > 0
        self.comfort_mode = (body[14] & 0x1) > 0 if len(body) > 16 else False


class XA1MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        if body[13] != 0xFF:
            temp_integer = int((body[13] - 50) / 2)
            temp_decimal = ((body[18] & 0xF) * 0.1) if len(body) > 20 else 0
            if body[13] > 49:
                self.indoor_temperature = temp_integer + temp_decimal
            else:
                self.indoor_temperature = temp_integer - temp_decimal
        if body[14] == 0xFF:
            self.outdoor_temperature = None
        else:
            temp_integer = int((body[14] - 50) / 2)
            temp_decimal = (((body[18] & 0xF0) >> 4) * 0.1) if len(body) > 20 else 0
            if body[14] > 49:
                self.outdoor_temperature = temp_integer + temp_decimal
            else:
                self.outdoor_temperature = temp_integer - temp_decimal
        self.indoor_humidity = body[17]


class XBXMessageBody(NewProtocolMessageBody):
    def __init__(self, body, bt):
        super().__init__(body, bt)
        params = self.parse()
        if NewProtocolTags.indirect_wind in params:
            self.indirect_wind = (params[NewProtocolTags.indirect_wind][0] == 0x02)
        if NewProtocolTags.indoor_humidity in params:
            self.indoor_humidity = params[NewProtocolTags.indoor_humidity][0]
        if NewProtocolTags.breezeless in params:
            self.breezeless = (params[NewProtocolTags.breezeless][0] == 1)
        if NewProtocolTags.screen_display in params:
            self.screen_display = (params[NewProtocolTags.screen_display][0] > 0)
            self.screen_display_new = True
        if NewProtocolTags.fresh_air_1 in params:
            self.fresh_air_1 = True
            data = params[NewProtocolTags.fresh_air_1]
            self.fresh_air_power = data[0] == 0x02
            self.fresh_air_fan_speed = data[1]
        if NewProtocolTags.fresh_air_2 in params:
            self.fresh_air_2 = True
            data = params[NewProtocolTags.fresh_air_2]
            self.fresh_air_power = data[0] > 0
            self.fresh_air_fan_speed = data[1]


class XC0MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[1] & 0x1) > 0
        self.mode = (body[2] & 0xe0) >> 5
        self.target_temperature = (body[2] & 0x0F) + 16.0 + (0.5 if body[0x02] & 0x10 > 0 else 0.0)
        self.fan_speed = body[3] & 0x7F
        self.swing_vertical = (body[7] & 0x0C) > 0
        self.swing_horizontal = (body[7] & 0x03) > 0
        self.boost_mode = (body[8] & 0x20) > 0
        self.smart_eye = (body[8] & 0x40) > 0
        self.natural_wind = (body[9] & 0x2) > 0
        self.dry = (body[9] & 0x4) > 0
        self.eco_mode = (body[9] & 0x10) > 0
        self.aux_heat = (body[9] & 0x08) > 0
        self.temp_fahrenheit = (body[10] & 0x04) > 0
        self.sleep_mode = (body[10] & 0x01) > 0
        if body[11] != 0xFF:
            temp_integer = int((body[11] - 50) / 2)
            temp_decimal = (body[15] & 0x0F) * 0.1
            if body[11] > 49:
                self.indoor_temperature = temp_integer + temp_decimal
            else:
                self.indoor_temperature = temp_integer - temp_decimal
        if body[12] == 0xFF:
            self.outdoor_temperature = None
        else:
            temp_integer = int((body[12] - 50) / 2)
            temp_decimal = ((body[15] & 0xF0) >> 4) * 0.1
            if body[12] > 49:
                self.outdoor_temperature = temp_integer + temp_decimal
            else:
                self.outdoor_temperature = temp_integer - temp_decimal
        self.full_dust = (body[13] & 0x20) > 0
        self.screen_display = ((body[14] >> 4 & 0x7) != 0x07) and self.power
        self.frost_protect = (body[21] & 0x80) > 0 if len(body) > 23 else False
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
        if self._message_type == MessageType.notify2 and self._body_type == 0xA0:
            self._body = XA0MessageBody(body)
        elif self._message_type == MessageType.notify1 and self._body_type == 0xA1:
            self._body = XA1MessageBody(body)
        elif self._message_type in [MessageType.query, MessageType.set, MessageType.notify2] and \
                self._body_type in [0xB0, 0xB1, 0xB5]:
            self._body = XBXMessageBody(body, self._body_type)
        elif self._message_type in [MessageType.query, MessageType.set] and self._body_type == 0xC0:
            self._body = XC0MessageBody(body)
        elif self._message_type == MessageType.query and self._body_type == 0xC1:
            self._body = XC1MessageBody(body)
        self.set_attr()
