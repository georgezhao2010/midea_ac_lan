import logging
from abc import ABC
from enum import IntEnum


_LOGGER = logging.getLogger(__name__)


class MessageLenError(Exception):
    pass


class MessageBodyError(Exception):
    pass


class MessageCheckSumError(Exception):
    pass


class MessageType(IntEnum):
    set = 0x02,
    query = 0x03,
    notify1 = 0x04,
    notify2 = 0x05


class MessageBase(ABC):
    HEADER_LENGTH = 10

    def __init__(self):
        self._device_type = 0x00
        self._message_type = 0x00
        self._body_type = 0x00

    @staticmethod
    def checksum(data):
        return (~ sum(data) + 1) & 0xff

    @property
    def header(self):
        raise NotImplementedError

    @property
    def body(self):
        raise NotImplementedError

    def __str__(self) -> str:
        output = {
            "header": self.header.hex(),
            "body": self.body.hex(),
            "message type": "%02x" % self._message_type,
            "body type": "%02x" % self._body_type
        }
        return str(output)


class MessageRequest(MessageBase):
    def __init__(self, device_type, message_type, body_type):
        super().__init__()
        self._device_type = device_type
        self._message_type = message_type
        self._body_type = body_type

    @property
    def header(self):
        length = self.HEADER_LENGTH + len(self.body)
        return bytearray([
            # flag
            0xAA,
            # length
            length,
            # device type
            self._device_type,
            # frame checksum
            self._device_type ^ length,
            # unused
            0x00, 0x00,
            # frame ID
            0x00,
            # frame protocol version
            0x00,
            # device protocol version
            0x00,
            # frame type
            self._message_type
        ])

    @property
    def _body(self):
        raise NotImplementedError

    @property
    def body(self):
        return bytearray([self._body_type]) + self._body

    def serialize(self):
        stream = self.header + self.body
        stream.append(MessageBase.checksum(stream[1:]))
        return stream


class MessageBody:
    def __init__(self, body):
        self.data = body

    @property
    def body_type(self):
        return self.data[0]


class MessageResponse(MessageBase):
    def __init__(self, message):
        super().__init__()
        if message is None or len(message) < self.HEADER_LENGTH + 1:
            raise MessageLenError
        self._header = message[:self.HEADER_LENGTH]
        self._message_type = self._header[-1]
        self._device_type = self._header[2]
        body = message[self.HEADER_LENGTH: -1]
        self._body = MessageBody(body)
        self._body_type = self._body.body_type

    @property
    def header(self):
        return self._header

    @property
    def body(self):
        return self._body.data
