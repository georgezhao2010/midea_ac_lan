from enum import IntEnum
from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)


class NewSetTags(IntEnum):
    power = 0x0100
    lock = 0x0201


class EDNewSetParamPack:
    @staticmethod
    def pack(param, value, addition=0):
        return bytearray([param & 0xFF, param >> 8, value, addition & 0xFF, addition >> 8])


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
    def __init__(self, device_protocol_version, device_class):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query,
            body_type=device_class)

    @property
    def _body(self):
        return bytearray([0x01])


class MessageQuery01(MessageQuery):  # 净水器
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version, device_class=0x01)


class MessageQuery07(MessageQuery):  # 管线机
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version, device_class=0x07)


class MessageNewSet(MessageEDBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.set,
            body_type=0x15)
        self.power = None
        self.lock = None

    @property
    def _body(self):
        pack_count = 0
        payload = bytearray([0x01, 0x00])
        if self.power is not None:
            pack_count += 1
            payload.extend(
                EDNewSetParamPack.pack(
                    param=NewSetTags.power,  # power
                    value=0x01 if self.power else 0x00
                )
            )
        if self.lock is not None:
            pack_count += 1
            payload.extend(
                EDNewSetParamPack.pack(
                    param=NewSetTags.lock,  # lock
                    value=0x01 if self.lock else 0x00
                )
            )
        payload[1] = pack_count
        return payload


class MessageOldSet(MessageEDBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.set,
            body_type=None)

    @property
    def body(self):
        return bytearray([])

    @property
    def _body(self):
        return bytearray([])


class EDMessageBody01(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.device_class = 0x01
        self.power = (body[2] & 0x01) > 0
        self.water_yield = body[7] + (body[8] << 8)
        self.in_tds = body[36] + (body[37] << 8)
        self.out_tds = body[38] + (body[39] << 8)
        self.child_lock = body[15]
        self.filter1 = round((body[25] + (body[26] << 8)) / 24)
        self.filter2 = round((body[27] + (body[28] << 8)) / 24)
        self.filter3 = round((body[29] + (body[30] << 8)) / 24)
        self.life1 = body[16]
        self.life2 = body[17]
        self.life3 = body[18]


class EDMessageBody03(MessageBody):
    def __init__(self, body):
        super().__init__(body)


class EDMessageBody05(MessageBody):
    def __init__(self, body):
        super().__init__(body)


class EDMessageBody06(MessageBody):
    def __init__(self, body):
        super().__init__(body)


class EDMessageBody07(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.water_yield = (body[21] << 8) + body[20]
        self.power = (body[51] & 0x01) > 0
        self.child_lock = (body[51] & 0x08) > 0


class MessageEDResponse(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[self.HEADER_LENGTH: -1]
        if self._message_type in [MessageType.query, MessageType.notify1]:
            if self._body_type == 0x01:
                self._body = EDMessageBody01(body)
            elif self._body_type in [0x03, 0x04]:
                self._body = EDMessageBody03(body)
            elif self._body_type == 0x05:
                self._body = EDMessageBody05(body)
            elif self._body_type == 0x06:
                self._body = EDMessageBody06(body)
            elif self._body_type == 0x07:
                self._body = EDMessageBody07(body)
        self.set_attr()
