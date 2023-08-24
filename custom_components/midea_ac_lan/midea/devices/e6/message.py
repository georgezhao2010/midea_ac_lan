from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)


class MessageE6Base(MessageRequest):
    def __init__(self, device_protocol_version, message_type):
        super().__init__(
            device_protocol_version=device_protocol_version,
            device_type=0xE6,
            message_type=message_type,
            body_type=None
        )

    @property
    def body(self):
        return self._body

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageE6Base):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query)

    @property
    def _body(self):
        return bytearray([0x01, 0x01] + [0] * 28)


class MessageSet(MessageE6Base):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.set)
        self.power = None
        self.heating_temperature = None
        self.bathing_temperature = None

    @property
    def _body(self):
        body = []
        if self.power is not None:
            power = 0x01 if self.power else 0x02
            body = [power, 0x01]
        elif self.heating_temperature is not None:
            body = [0x04, 0x13, self.heating_temperature]
        elif self.bathing_temperature is not None:
            body = [0x04, 0x12, self.bathing_temperature]
        body_len = len(body)
        return bytearray(body + [0] * (30 - body_len))


class E6GeneralMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[4] & 0x04) > 0
        self.burning_state = (body[4] & 0x08) > 0
        self.heating_working = (body[4] & 0x10) > 0
        self.bathing_working = (body[4] & 0x20) > 0
        self.min_temperature = [
            body[18],
            body[13]
        ]
        self.max_temperature = [
            body[17],
            body[12]
        ]
        self.heating_temperature = body[19]
        self.bathing_temperature = body[14]
        self.heating_leaving_temperature = body[16]
        self.bathing_leaving_temperature = body[10]
        self.heating_returning_temperature = body[37]
        self.bathing_returning_temperature = body[38]


class MessageE6Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[self.HEADER_LENGTH: -1]
        self._body = E6GeneralMessageBody(body)
        self.set_attr()
