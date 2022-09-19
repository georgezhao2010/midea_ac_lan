from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)


class MessageCFBase(MessageRequest):
    def __init__(self, device_protocol_version, message_type, body_type):
        super().__init__(
            device_protocol_version=device_protocol_version,
            device_type=0xCF,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageCFBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query,
            body_type=0x01)

    @property
    def _body(self):
        return bytearray([])


class MessageSet(MessageCFBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.set,
            body_type=0x01)
        self.power = False
        self.mode = 0  # 1 自动 2 制冷 3 制热
        self.target_temperature = None
        self.aux_heat = None

    @property
    def _body(self):
        power = 0x01 if self.power else 0x00
        mode = self.mode
        target_temperature = 0xFF if self.target_temperature is None else (int(self.target_temperature) & 0xFF)
        aux_heat = 0xFF if self.aux_heat is None else (0x01 if self.aux_heat else 0x00)
        return bytearray([
            power, mode, target_temperature, aux_heat
        ])


class CFMessageBody(MessageBody):
    def __init__(self, body, data_offset=0):
        super().__init__(body)
        self.power = (body[data_offset + 0] & 0x01) > 0
        self.aux_heat = (body[data_offset + 0] & 0x02) > 0
        self.silent = (body[data_offset + 0] & 0x04) > 0
        self.mode = body[data_offset + 3]
        self.target_temperature = body[data_offset + 4]
        self.current_temperature = body[data_offset + 5]
        if self.mode == 2:
            self.max_temperature = body[data_offset + 8]
            self.min_temperature = body[data_offset + 9]
        elif self.mode == 3:
            self.max_temperature = body[data_offset + 6]
            self.min_temperature = body[data_offset + 7]
        else:
            self.max_temperature = body[data_offset + 6]
            self.min_temperature = body[data_offset + 9]


class MessageCFResponse(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[self.HEADER_LENGTH: -1]
        if self._message_type in [MessageType.query, MessageType.set] and self._body_type == 0x01:
            self._body = CFMessageBody(body, data_offset=1)
        elif self._message_type in [MessageType.notify1, MessageType.notify2]:
            self._body = CFMessageBody(body, data_offset=0)
        self.set_attr()

