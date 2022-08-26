import logging
from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)

_LOGGER = logging.getLogger(__name__)


class MessageE3Base(MessageRequest):
    def __init__(self, message_type, body_type):
        super().__init__(
            device_type=0xE3,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageE3Base):
    def __init__(self):
        super().__init__(
            message_type=MessageType.query,
            body_type=0x01)

    @property
    def _body(self):
        return bytearray([0x01])


class MessagePower(MessageE3Base):
    def __init__(self):
        super().__init__(
            message_type=MessageType.set,
            body_type=0x02)
        self.power = False

    @property
    def _body(self):
        if self.power:
            self._body_type = 0x01
        else:
            self._body_type = 0x02
        return bytearray([0x01])


class MessageGeneralSet(MessageE3Base):
    def __init__(self):
        super().__init__(
            message_type=MessageType.set,
            body_type=0x04)

        self.target_temperature = 0
        self.zero_cold_water = False
        self.mode = 0
        self.bathtub_volume = 0
        self.protection = False
        self.zero_cold_pulse = False
        self.smart_volume = False

    @property
    def _body(self):
        # Byte 2 zero_cold_water mode
        zero_cold_water = 0x01 if self.zero_cold_water else 0x00
        mode = (1 << (self.mode + 1)) if self.mode < 5 else 0
        # Byte 3
        protection = 0x08 if self.protection else 0x00
        zero_cold_pulse = 0x10 if self.zero_cold_pulse else 0x00
        smart_volume = 0x20 if self.smart_volume else 0x00
        # Byte 5 target_temperature
        target_temperature = self.target_temperature & 0xFF
        energy_saving = 0x02 if self.mode == 5 else 0x00

        return bytearray([
            0x01,
            zero_cold_water | mode,
            protection | zero_cold_pulse | smart_volume,
            0x00,
            target_temperature,
            0x00, 0x00,
            energy_saving,
            0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00
        ])


class E3GeneralMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[2] & 0x01) > 0
        self.burning_state = (body[2] & 0x02) > 0
        self.zero_cold_water = (body[2] & 0x04) > 0
        self.mode = 0
        if (body[2] & 0x08) > 0:
            # shower mode
            self.mode = 0
        elif (body[2] & 0x10) > 0:
            # kitchen mode
            self.mode = 1
        elif (body[2] & 0x40) > 0:
            # bathtub mode
            self.mode = 2
        elif (body[2] & 0x20) > 0:
            # temperature mode
            self.mode = 3
        elif (body[2] & 0x80) > 0:
            # cloud mode
            self.mode = 4
        if (body[16] & 0x01) > 0:
            self.mode = 5
        elif(body[16] & 0x80) > 0:
            self.mode = 6
        self.temperature = body[5]
        self.target_temperature = body[6]
        self.protection = (body[8] & 0x08) > 0
        self.zero_cold_pulse = (body[20] & 0x01) > 0 if len(body) > 20 else False
        self.smart_volume = (body[20] & 0x02) > 0 if len(body) > 20 else False


class MessageE3Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[10: -2]
        if (self._message_type == MessageType.query and self._body_type == 0x01) or \
                (self._message_type == MessageType.set and self._body_type in [0x01, 0x02, 0x04, 0x14]) or \
                (self._message_type == MessageType.notify1 and self._body_type in [0x00, 0x01]):
            self._body = E3GeneralMessageBody(body)
        self.set_attr()
