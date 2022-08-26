import logging
from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)

_LOGGER = logging.getLogger(__name__)


class MessageFABase(MessageRequest):
    def __init__(self, message_type, body_type):
        super().__init__(
            device_type=0xFA,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageFABase):
    def __init__(self):
        super().__init__(
            message_type=MessageType.query,
            body_type=0x00)

    @property
    def body(self):
        return bytearray([])

    @property
    def _body(self):
        return bytearray([])

