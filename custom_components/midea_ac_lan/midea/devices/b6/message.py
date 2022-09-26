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
            body_type=0x22)
        self.light = None
        self.power = None
        self.fan_level = None

    @property
    def _body(self):
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
        elif self._message_type == MessageType.query:
            if self._body_type == 0x31:
                self._body = B6GeneralBody(body)
            elif self._body_type == 0x32 and body[1] == 0x01:
                self._body = B6ExceptionBody(body)
        elif self._message_type == MessageType.notify1:
            if self._body_type == 0x41:
                self._body = B6GeneralBody(body)
            elif self._body_type == 0x0A:
                if body[1] == 0xA1:
                    self._body = B6ExceptionBody(body)
                elif body[1] == 0xA2:
                    self.oilcup_full = (body[2] & 0x01) > 0
                    self.cleaning_reminder = (body[2] & 0x02) > 0
        elif self._message_type == MessageType.exception2 and self._body_type == 0xA1:
            pass

        self.set_attr()
