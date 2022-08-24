import logging
from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)

_LOGGER = logging.getLogger(__name__)


class MessageE1Base(MessageRequest):
    def __init__(self, message_type, body_type):
        super().__init__(
            device_type=0xE1,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessagePower(MessageE1Base):
    def __init__(self):
        super().__init__(
            message_type=MessageType.set,
            body_type=0x00)
        self.power = False

    @property
    def _body(self):
        power = 0x01 if self.power else 0x00
        return bytearray([
            power,
            0x00, 0x00, 0x00
        ])


class MessageQuery(MessageE1Base):
    def __init__(self):
        super().__init__(
            message_type=MessageType.query,
            body_type=0x00)

    @property
    def _body(self):
        return bytearray([])


class E1GeneralMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = body[1] > 0
        self.status = body[1]
        self.door = (body[5] & 0x01) == 0       # 0 - open, 1 - close
        self.rinse_aid = (body[5] & 0x02) > 0   # 0 - enough, 1 - shortage
        self.salt = (body[5] & 0x04) > 0        # 0 - enough, 1 - shortage
        self.time_remaining = body[6]
        self.progress = body[9]


class MessageE1Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[10: -2]
        if (self._message_type == MessageType.set and 0 <= self._body_type <= 7) or \
                (self._message_type in [MessageType.query, MessageType.notify1] and self._body_type == 0):
            self._body = E1GeneralMessageBody(body)
            self.power = self._body.power
            self.status = self._body.status
            self.door = self._body.door
            self.rinse_aid = self._body.rinse_aid
            self.salt = self._body.salt
            self.time_remaining = self._body.time_remaining
            self.progress = self._body.progress
