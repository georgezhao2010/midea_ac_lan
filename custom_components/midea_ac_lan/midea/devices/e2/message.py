import logging
from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)

_LOGGER = logging.getLogger(__name__)


class MessageE2Base(MessageRequest):
    def __init__(self, message_type, body_type):
        super().__init__(
            device_type=0xE2,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageE2Base):
    def __init__(self):
        super().__init__(
            message_type=MessageType.query,
            body_type=0x01)

    @property
    def _body(self):
        return bytearray([0x01])


class MessagePower(MessageE2Base):
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


class MessageGeneralSet(MessageE2Base):
    def __init__(self):
        super().__init__(
            message_type=MessageType.set,
            body_type=0x04)

        self.target_temperature = 0
        self.mode = 0
        self.variable_heating = False
        self.whole_tank_heating = False
        self.protection = False
        self.auto_cut_out = False

    @property
    def _body(self):
        # Byte 2 mode
        mode = 0 if self.mode == 0 else 1 << (self.mode - 1)
        # Byte 4 whole_tank_heating, protection
        whole_tank_heating = 0x02 if self.whole_tank_heating else 0x01
        protection = 0x08 if self.protection else 0x00
        auto_cut_out = 0x04 if self.auto_cut_out else 0x00
        # Byte 5 target_temperature
        target_temperature = self.target_temperature & 0xFF
        # Byte 9 variable_heating
        variable_heating = 0x10 if self.variable_heating else 0x00
        return bytearray([
            0x01,
            mode,
            0x00,
            whole_tank_heating | protection | auto_cut_out,
            target_temperature,
            0x00, 0x00, 0x00,
            variable_heating,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00
        ])


class E2GeneralMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[2] & 0x01) > 0
        self.heating = (body[2] & 0x04) > 0
        self.heat_insulating = (body[2] & 0x08) > 0
        self.variable_heating = (body[2] & 0x80) > 0
        self.temperature = body[4]
        self.mode = 0
        if (body[7] & 0x01) > 0:
            # e-Plus mode
            self.mode = 1
        elif (body[7] & 0x02) > 0:
            # Rapid mode
            self.mode = 2
        elif (body[7] & 0x10) > 0:
            # Summer mode
            self.mode = 3
        elif (body[7] & 0x20) > 0:
            # Winter mode
            self.mode = 4
        elif (body[7] & 0x40) > 0:
            # Power saving
            self.mode = 5
        self.whole_tank_heating = (body[7] & 0x08) > 0
        self.target_temperature = body[11]
        self.protection = (body[22] & 0x04) > 0 if len(body) > 22 else False
        self.auto_cut_out = (body[22] & 0x02) > 0 if len(body) > 22 else False
        self.heating_power = body[27] if len(body) > 27 else 0


class MessageE2Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[10: -2]
        if (self._message_type in [MessageType.query, MessageType.notify1] and self._body_type == 0x01) or \
                (self._message_type == MessageType.set and self._body_type in [0x01, 0x02, 0x04]):
            self._body = E2GeneralMessageBody(body)
        self.set_attr()
