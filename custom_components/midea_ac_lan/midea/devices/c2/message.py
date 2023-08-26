from enum import IntEnum
from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)


class C2MessageEnum(IntEnum):
    child_lock = 0x10
    light = 0x0d


C2_MESSAGE_KEYS = {
    C2MessageEnum.child_lock: {True: 0x10, False: 0x00},
    C2MessageEnum.light: {True: 0x01, False: 0x00}
}


class MessageC2Base(MessageRequest):
    def __init__(self, device_protocol_version, message_type, body_type):
        super().__init__(
            device_protocol_version=device_protocol_version,
            device_type=0xC2,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageC2Base):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query,
            body_type=0x01)

    @property
    def _body(self):
        return bytearray([0x01])


class MessagePowerOn(MessageC2Base):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.set,
            body_type=0x01)

    @property
    def _body(self):
        return bytearray([0x01])


class MessagePowerOff(MessageC2Base):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.set,
            body_type=0x02)

    @property
    def _body(self):
        return bytearray([0x01])


class MessageSet(MessageC2Base):
    def __init__(self, device_protocol_version, key: C2MessageEnum, value: bool):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.set,
            body_type=0x14)

        self.key = key
        self.value = C2_MESSAGE_KEYS.get(self.key).get(value)

    @property
    def _body(self):
        return bytearray([self.key, self.value])


class C2MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[2] & 0x01) > 0
        self.seat_status = (body[3] & 0x01) > 0
        self.flip_status = (body[12] & 0x08) > 0
        self.light = (body[14] & 0x02) > 0
        self.child_lock = (body[14] & 0x04) > 0


class C2Notify1MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)


class MessageC2Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[self.HEADER_LENGTH: -1]
        if self._message_type in [MessageType.notify1, MessageType.query, MessageType.set]:
            self._body = C2MessageBody(body)
        self.set_attr()