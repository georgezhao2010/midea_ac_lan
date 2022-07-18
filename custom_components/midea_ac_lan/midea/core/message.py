import logging
from abc import ABC

from .crc8 import calculate

_LOGGER = logging.getLogger(__name__)


class MessageLenError(Exception):
    pass


class MessageCheckSumError(Exception):
    pass


class NewProtocolParamPack:
    @staticmethod
    def pack(param, value: bytearray, length=1, pack_len=4):
        if pack_len == 4:
            stream = bytearray([param & 0xFF, param >> 8, length]) + value
        else:
            stream = bytearray([param & 0xFF, param >> 8, 0x00, length]) + value
        return stream

    @staticmethod
    def parse(stream, pack_len=5):
        result = {}
        pos = 1
        for pack in range(0, stream[0]):
            param = stream[pos] + (stream[pos + 1] << 8)
            if pack_len == 5:
                pos += 1
            length = stream[pos + 2]
            if length > 0:
                value = stream[pos + 3: pos + 3 + length]
                result[param] = value
            pos += (3 + length)
        return result


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

    def serialize(self):
        stream = self.header + self.body
        stream.append(calculate(self.body))
        stream.append(MessageBase.checksum(stream[1:]))
        return stream

    def __str__(self) -> str:
        output = {
            "header": self.header.hex(),
            "payload": self.body.hex(),
            "message type": "%#x" % self._message_type,
            "body type": "%#x" % self._body_type
        }
        return str(output)


class MessageRequest(MessageBase):
    _message_serial = 0

    def __init__(self, device_type, message_type, body_type):
        super().__init__()
        self._device_type = device_type
        self._message_type = message_type
        self._body_type = body_type
        MessageRequest._message_serial += 1
        if MessageRequest._message_serial >= 254:
            MessageRequest._message_serial = 1

    @property
    def header(self):
        length = self.HEADER_LENGTH + len(self.body) + 1
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
        return bytearray([self._body_type]) + self._body + bytearray([MessageRequest._message_serial])


class MessageBody:
    def __init__(self, body):
        self.data = body


class MessageResponse(MessageBase):
    def __init__(self, message):
        super().__init__()
        if message is None:
            raise MessageLenError
        length = len(message)
        if length < 10 + 3:
            raise MessageLenError
        self._header = message[:self.HEADER_LENGTH]
        self._message_type = self._header[-1]
        self._device_type = self._header[2]
        body = message[10: -2]
        self._body_type = body[0]
        self._body = MessageBody(body)

    @property
    def header(self):
        return self._header

    @property
    def body(self):
        return self._body.data
