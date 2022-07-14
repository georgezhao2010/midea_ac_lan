import logging
from .crc8 import calculate

_LOGGER = logging.getLogger(__name__)


class MessageLenError(Exception):
    pass


class MessageCheckSumError(Exception):
    pass


class NewProtocolParamPack:
    def __init__(self, param, value: bytearray, length=1, pack_len=4):
        self._param = param
        self._length = length
        self._value = value
        self._pack_len = pack_len

    def serialize(self):
        if self._pack_len == 4:
            stream = bytearray([self._param >> 8, self._param & 0xFF, self._length]) + self._value
        else:
            stream = bytearray([self._param >> 8, self._param & 0xFF, 00, self._length]) + self._value
        return stream

    @property
    def value(self):
        return self._value

    @staticmethod
    def parse(stream, pack_len=5):
        result = {}
        pos = 1
        for pack in range(0, stream[0]):
            param = stream[pos] << 8 + stream[pos + 1]
            if pack_len == 5:
                pos += 1
            length = stream[pos + 2]
            value = stream[pos + 3: pos + 3 + length]
            result[param] = value
            pos += (3 + length)
        return result


class MessageBase:
    def __init__(self):
        self._device_type = 0x00
        self._frame_type = 0x00
        self._msg_type = 0x00

    @staticmethod
    def checksum(data):
        return (~ sum(data) + 1) & 0xff

    @property
    def header(self):
        return bytearray([])

    @property
    def payload(self):
        return bytearray([])

    def __str__(self) -> str:
        output = {
            "header": self.header.hex(),
            "payload": self.payload.hex(),
            "frame type": "%#x" % self._frame_type,
            "message type": "%#x" % self._msg_type
        }
        return str(output)


class MessageRequest(MessageBase):
    _message_serial = 0

    def __init__(self, device_type, frame_type, msg_type):
        super().__init__()
        self._device_type = device_type
        self._frame_type = frame_type
        self._msg_type = msg_type
        MessageRequest._message_serial += 1
        if MessageRequest._message_serial >= 254:
            MessageRequest._message_serial = 1


    @property
    def header(self):
        length = 10 + len(self.payload) + 1
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
            self._frame_type
        ])

    @property
    def _payload(self):
        return bytearray([])

    @property
    def payload(self):
        return bytearray([self._msg_type]) + self._payload + bytearray([MessageRequest._message_serial])

    def serialize(self):
        stream = self.header + self.payload
        stream.append(calculate(self.payload))
        stream.append(MessageBase.checksum(stream[1:]))
        return stream


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
        self._header = message[:10]
        self._frame_type = self._header[-1]
        body = message[10: -2]
        self._msg_type = body[0]
        self._body = MessageBody(body)

    @property
    def header(self):
        return self._header

    @property
    def payload(self):
        return self._body.data
