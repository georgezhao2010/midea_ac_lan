import logging
from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)

_LOGGER = logging.getLogger(__name__)


class MessageEDBase(MessageRequest):
    def __init__(self, device_protocol_version, message_type, body_type):
        super().__init__(
            device_protocol_version=device_protocol_version,
            device_type=0xED,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageEDBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query,
            body_type=0x00)

    @property
    def _body(self):
        return bytearray([])


class MessageSet(MessageEDBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.set,
            body_type=0x00)

    @property
    def _body(self):
        return bytearray([])


class EDQueryMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[2] & 0x01) > 0


class EDNotifyMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)


class MessageEDResponse(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[self.HEADER_LENGTH: -1]
        if self._message_type in [MessageType.query, MessageType.notify1]:
            if self._body_type == 0x01:
                self._body = EDQueryMessageBody(body)
            elif self._body_type in [0x03, 0x04]:
                self._body = EDNotifyMessageBody(body)
        self.set_attr()
