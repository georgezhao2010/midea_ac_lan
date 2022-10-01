from ...core.crc8 import calculate
from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)


class MessageFBBase(MessageRequest):
    def __init__(self, device_protocol_version, message_type, body_type):
        super().__init__(
            device_protocol_version=device_protocol_version,
            device_type=0xFB,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageFBBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query,
            body_type=None)

    @property
    def body(self):
        return bytearray([])

    @property
    def _body(self):
        return bytearray([])


class MessageSet(MessageFBBase):
    def __init__(self, device_protocol_version, sub_type):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.set,
            body_type=0x00)
        self.sub_type = sub_type
        self.power = None
        self.mode = None
        self.heating_level = None
        self.target_temperature = None
        self.child_lock = None

    @property
    def body(self):
        power = 0 if self.power is None else (0x01 if self.power else 0x02)
        mode = 0 if self.mode is None else self.mode
        heating_level = 0 if self.heating_level is None else \
            (int(self.heating_level if 1 <= self.heating_level <= 10 else 0) & 0xFF)
        target_temperature = 0 if self.target_temperature is None else \
            (int((self.target_temperature + 41) if -40 <= self.target_temperature <= 50 else
             (0x80 if self.target_temperature in [0x80, 87] else 0)) & 0xFF)
        child_lock = 0xFF if self.child_lock is None else (0x01 if self.child_lock else 0x00)
        _return_body = bytearray([
            power,
            0x00, 0x00, 0x00,
            mode,
            heating_level,
            target_temperature,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00,
            child_lock,
            0x00
        ])
        if self.sub_type > 5:
            _return_body += bytearray([0x00, 0x00, 0x00])
        return _return_body

    @property
    def _body(self):
        return bytearray([])


class FBGeneralMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[0] & 0x01) not in [0, 2]
        self.mode = body[4]
        self.heating_level = body[5]
        self.target_temperature = body[6] - 41
        if 1 <= body[7] <= 100:
            self.target_humidity = body[7]
            self.current_humidity = body[12]
        self.current_temperature = body[13] - 20
        if len(body) > 18:
            self.child_lock = (body[18] & 0x01) > 0
        if len(body) > 21:
            self.energy_consumption = (body[21] << 8) + body[20]


class MessageFBResponse(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[self.HEADER_LENGTH: -1]
        if self._message_type in [MessageType.query, MessageType.set, MessageType.notify1]:
            self._body = self._body = FBGeneralMessageBody(body)
        self.set_attr()
