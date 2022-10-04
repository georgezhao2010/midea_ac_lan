from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody
)


class MessageCFBase(MessageRequest):
    def __init__(self, device_protocol_version, message_type, body_type):
        super().__init__(
            device_protocol_version=device_protocol_version,
            device_type=0xB0,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery00(MessageCFBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query,
            body_type=0x00)

    @property
    def _body(self):
        return bytearray([])


class MessageQuery01(MessageCFBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query,
            body_type=0x01)

    @property
    def _body(self):
        return bytearray([])


class B0MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        if len(body) > 15:
            self.door = (body[0] & 0x80) > 0
            self.status = body[0] & 0x7F
            self.time_remaining = body[2] * 60 + body[3]
            self.error_code = body[5]


class B0Message01Body(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        if len(body) > 15:
            self.door = (body[32] & 0x02) > 0
            self.status = body[31]
            self.time_remaining = (0 if body[22] == 0xFF else body[22]) * 3600 + \
                                  (0 if body[23] == 0xFF else body[23]) * 60 + \
                                  (0 if body[24] == 0xFF else body[24])
            self.current_temperature = (body[25] << 8) + (body[26])
            if self.current_temperature == 0:
                self.current_temperature = (body[27] << 8) + body[28]
            self.tank_ejected = (body[32] & 0x04) > 0
            self.water_shortage = (body[32] & 0x08) > 0
            self.water_change_reminder = (body[32] & 0x10) > 0


class MessageB0Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[self.HEADER_LENGTH: -1]
        if self._message_type in [MessageType.notify1, MessageType.query]:
            if self._body_type == 0x01:
                self._body = B0Message01Body(body)
            elif self._body_type == 0x04:
                pass
            else:
                self._body = B0MessageBody(body)
        self.set_attr()
