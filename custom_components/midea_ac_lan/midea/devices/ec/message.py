from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)


class MessageECBase(MessageRequest):
    def __init__(self, device_protocol_version, message_type, body_type):
        super().__init__(
            device_protocol_version=device_protocol_version,
            device_type=0xEC,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageECBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query,
            body_type=None)

    @property
    def body(self):
        return bytearray([
            0xAA, 0x55,
            self._device_protocol_version, 0x03,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00
        ])

    @property
    def _body(self):
        return bytearray([])


class ECGeneralMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.mode = body[4] + (body[5] << 8)
        self.progress = body[8]
        self.cooking = self.progress == 1
        self.time_remaining = body[12] * 60 + body[13]
        self.keep_warm_time = body[16] * 60 + body[17]
        self.top_temperature = body[21]
        self.bottom_temperature = body[22]
        self.with_pressure = (body[23] & 0x04) > 0


class MessageECResponse(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[self.HEADER_LENGTH: -1]
        if(self._message_type == MessageType.set and body[3] == 0x02) or \
                (self._message_type == MessageType.query and body[3] == 0x03) or \
                (self._message_type == MessageType.notify1 and body[3] == 0x04) or \
                (self._message_type == MessageType.notify1 and body[3] == 0x3d):
            self._body = ECGeneralMessageBody(body)
        elif self._message_type == MessageType.notify1 and body[3] == 0x06:
            self.mode = body[4] + (body[5] << 8)
        self.set_attr()
