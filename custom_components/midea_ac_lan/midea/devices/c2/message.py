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
    water_temp_level = 0x09
    seat_temp_level = 0x0a
    dry_level = 0x0c


C2_MESSAGE_KEYS = {
    C2MessageEnum.child_lock: {True: 0x10, False: 0x00},
    C2MessageEnum.light: {True: 0x01, False: 0x00},
    C2MessageEnum.dry_level: {0: 0, 1: 1, 2: 2, 3: 3},
    C2MessageEnum.seat_temp_level: {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5},
    C2MessageEnum.water_temp_level: {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
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
        self.dry_level = ((body[6] & 0x7E) >> 1)
        self.water_temp_level = (body[9] & 0x07)
        self.seat_temp_level = ((body[9] & 0x38) >> 3)
        self.lid_status = (body[12] & 0x08) > 0
        self.light = (body[14] & 0x02) > 0
        self.child_lock = (body[14] & 0x04) > 0
        self.water_temperature = body[11]
        self.seat_temperature = body[11]
        self.filter_life = 100 - body[19]


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