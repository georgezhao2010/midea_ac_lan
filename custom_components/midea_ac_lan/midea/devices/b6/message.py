from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)


class MessageB6Base(MessageRequest):
    def __init__(self, device_protocol_version, message_type, body_type):
        super().__init__(
            device_protocol_version=device_protocol_version,
            device_type=0xB6,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageB6Base):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query,
            body_type=0x31)
        if device_protocol_version == 2:
            self._body_type = 0x11

    @property
    def _body(self):
        return bytearray([])


class MessageQueryTips(MessageB6Base):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query,
            body_type=0x02)

    @property
    def _body(self):
        return bytearray([0x01])


class MessageSet(MessageB6Base):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.set,
            body_type=0x00)
        self.light = None
        self.power = None
        self.fan_level = None
        if self._device_protocol_version in [0x00, 0x01]:
            self._body_type = 0x22
        else:
            self._body_type = 0x11

    @property
    def _body(self):
        if self._device_protocol_version in [0x00, 0x01]:
            light = 0xFF
            value2 = 0xFF
            value3 = 0xFF
            if self.light is not None:
                if self.light:
                    light = 0x1A
                else:
                    light = 0
            elif self.power is not None:
                if self.power:
                    value2 = 0x02
                    if self.fan_level is not None:
                        value3 = self.fan_level
                    else:
                        value3 = 0x01
                else:
                    value2 = 0x03
            elif self.fan_level is not None:
                if self.fan_level == 0:
                    value2 = 0x03
                else:
                    value2 = 0x02
                    value3 = self.fan_level
            return bytearray([
                0x01, light, value2, value3,
                0xFF, 0xFF, 0xFF, 0xFF, 0xFF
            ])
        else:
            value13 = 0xFF
            value14 = 0xFF
            value15 = 0xFF
            value16 = 0xFF
            if self.power is not None:
                value13 = 0x01
                if self.power:
                    value15 = 0x02
                    if self.fan_level is not None:
                        value16 = self.fan_level
                    else:
                        value16 = 0x01
                else:
                    value15 = 0x01
            elif self.fan_level is not None:
                value13 = 0x01
                if self.fan_level == 0:
                    value15 = 0x01
                else:
                    value15 = 0x02
                    value16 = self.fan_level
            elif self.light is not None:
                value13 = 0x02
                value14 = 0x02
                value15 = 0x01 if self.light else 0x00
            return bytearray([
                0x01, value13, value14, value15, value16,
                0xFF, 0xFF
            ])


class B6FeedbackBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)


class B6GeneralBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        if body[1] != 0xFF:
            self.light = body[1] > 0x00
        self.power = False
        fan_level = None
        if body[2] != 0xFF:
            self.power = body[2] in [0x02, 0x06, 0x07, 0x14, 0x15, 0x16]
            if body[2] in [0x14, 0x16]:
                fan_level = 0x16
        if fan_level is None and body[3] != 0xFF:
            fan_level = body[3]
        if fan_level > 100:
            if fan_level < 130:
                fan_level = 1
            elif fan_level < 140:
                fan_level = 2
            elif fan_level < 170:
                fan_level = 3
            else:
                fan_level = 4
        else:
            self.fan_level = fan_level
        self.fan_level = 0 if fan_level is None else fan_level
        self.oilcup_full = (body[5] & 0x01) > 0
        self.cleaning_reminder = (body[5] & 0x02) > 0


class B6NewProtocolBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        if body[1] == 0x01:
            pack_bytes = body[3: 3 + body[2]]
            if pack_bytes[1] != 0xFF:
                self.power = True
                self.power = pack_bytes[1] not in [0x00, 0x01, 0x05, 0x07]
            if pack_bytes[2] != 0xFF:
                self.fan_level = pack_bytes[2]
            if pack_bytes[6] != 0xFF:
                self.light = pack_bytes[6] > 0
            self.oilcup_full = (pack_bytes[18] & 0x02) > 0
            self.cleaning_reminder = (pack_bytes[18] & 0x04) > 0


class B6SpecialBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        if body[2] != 0xFF:
            self.light = body[2] > 0x00
        self.power = False
        if body[3] != 0xFF:
            self.power = body[3] in [0x00, 0x02, 0x04]
        if body[4] != 0xFF:
            self.fan_level = body[4]


class B6ExceptionBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)


class MessageB6Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[self.HEADER_LENGTH: -1]
        if self._message_type == MessageType.set and self._body_type == 0x22 and body[1] == 0x01:
            self._body = B6SpecialBody(body)
        elif self._message_type == MessageType.set and self._body_type == 0x11 and body[1] == 0x01:
            #############################
            pass
        elif self._message_type == MessageType.query:
            if self._body_type in [0x11, 0x31]:
                if self._device_protocol_version in [0, 1]:
                    self._body = B6GeneralBody(body)
                else:
                    self._body = B6NewProtocolBody(body)
            elif self._body_type == 0x32 and body[1] == 0x01:
                self._body = B6ExceptionBody(body)
        elif self._message_type == MessageType.notify1:
            if self._body_type in [0x11, 0x41]:
                if self._device_protocol_version in [0, 1]:
                    self._body = B6GeneralBody(body)
                else:
                    self._body = B6NewProtocolBody(body)
            elif self._body_type == 0x0A:
                if body[1] == 0xA1:
                    self._body = B6ExceptionBody(body)
                elif body[1] == 0xA2:
                    self.oilcup_full = (body[2] & 0x01) > 0
                    self.cleaning_reminder = (body[2] & 0x02) > 0
        elif self._message_type == MessageType.exception2 and self._body_type == 0xA1:
            pass

        self.set_attr()
