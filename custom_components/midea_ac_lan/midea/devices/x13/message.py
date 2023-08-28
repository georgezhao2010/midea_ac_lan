from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody
)


class Message13Base(MessageRequest):
    def __init__(self, device_protocol_version, message_type, body_type):
        super().__init__(
            device_protocol_version=device_protocol_version,
            device_type=0x13,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(Message13Base):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query,
            body_type=0x24)

    @property
    def _body(self):
        return bytearray([
            0x00, 0x00, 0x00, 0x00
        ])


class MessageSet(Message13Base):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.set,
            body_type=0x00)
        self.brightness = None
        self.color_temperature = None
        self.effect = None
        self.power = None
        self.delay_off = None

    @property
    def _body(self):
        body_byte = 0x00
        if self.power is not None:
            self._body_type = 0x01
            body_byte = 0x01 if self.power else 0x00
        elif self.effect is not None and self.effect in range(1, 6):
            self._body_type = 0x02
            body_byte = self.effect + 1
        elif self.color_temperature is not None:
            self._body_type = 0x03
            body_byte = self.color_temperature
        elif self.brightness is not None:
            self._body_type = 0x04
            body_byte = self.brightness
        elif self.delay_off is not None:
            self._body_type = 0x05
            body_byte = 0x01 if self.delay_off else 0x00
        return bytearray([body_byte, 0x00, 0x00, 0x00])


class MessageMainLightBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.brightness = self.read_byte(body, 1)
        self.color_temperature = self.read_byte(body, 2)
        self.effect = self.read_byte(body, 3)
        if self.effect < 1 or self.effect > 6:
            self.effect = 1
        self.delay_off = self.read_byte(body, 4)
        '''
        self.rgb_color = [self.read_byte(body, 5),
                          self.read_byte(body, 6),
                          self.read_byte(body, 7)]
        '''
        self.power = self.read_byte(body, 8) > 0

class MessageMainLightResponseBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.control_success = body[1] > 0

class Message13Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[self.HEADER_LENGTH: -1]
        if self._body_type == 0xa4:
            self._body = MessageMainLightBody(body)
        elif self.message_type == MessageType.set and self._body_type > 0x80:
            self._body = MessageMainLightResponseBody(body)
        self.set_attr()

