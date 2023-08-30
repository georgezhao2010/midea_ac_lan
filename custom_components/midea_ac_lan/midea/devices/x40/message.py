from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody
)


class Message40Base(MessageRequest):
    def __init__(self, device_protocol_version, message_type, body_type):
        super().__init__(
            device_protocol_version=device_protocol_version,
            device_type=0x40,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(Message40Base):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query,
            body_type=0x01)

    @property
    def _body(self):
        return bytearray([
        ])


class MessageSet(Message40Base):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.set,
            body_type=0x01)
        self.fields = {}
        self.light = False
        self.power = False
        self.fan_speed = 30
        self.oscillate = False
        self.ventilation = False

    def read_field(self, field):
        value = self.fields.get(field, 0)
        return value if value else 0

    @property
    def _body(self):
        fan_speed = 0xFF if self.fan_speed == 0 else 30 if self.fan_speed <= 50 else 100
        return bytearray([
            1 if self.light else 0,
            self.read_field("MAIN_LIGHT_BRIGHTNESS"),
            self.read_field("NIGHT_LIGHT_ENABLE"),
            self.read_field("NIGHT_LIGHT_BRIGHTNESS"),
            self.read_field("RADAR_INDUCTION_ENABLE"),
            self.read_field("RADAR_INDUCTION_CLOSING_TIME"),
            self.read_field("LIGHT_INTENSITY_THRESHOLD"),
            self.read_field("RADAR_SENSITIVITY"),
            self.read_field("HEATING_ENABLE"),
            self.read_field("HEATING_SPEED"),
            self.read_field("HEATING_DIRECTION"),
            self.read_field("BATH_ENABLE"),
            self.read_field("BATH_HEATING_TIME"),
            self.read_field("BATH_TEMPERATURE"),
            self.read_field("BATH_SPEED"),
            self.read_field("BATH_DIRECTION"),
            1 if self.ventilation else 0,
            self.read_field("VENTILATION_SPEED"),
            self.read_field("VENTILATION_DIRECTION"),
            self.read_field("DRYING_ENABLE"),
            self.read_field("DRYING_TIME"),
            self.read_field("DRYING_TEMPERATURE"),
            self.read_field("DRYING_SPEED"),
            self.read_field("DRYING_DIRECTION"),
            1 if self.power else 0,
            fan_speed,
            0xFD if self.oscillate else 0x66,
            self.read_field("DELAY_ENABLE"),
            self.read_field("DELAY_TIME"),
            self.read_field("SOFT_WIND_ENABLE"),
            self.read_field("SOFT_WIND_TIME"),
            self.read_field("SOFT_WIND_TEMPERATURE"),
            self.read_field("SOFT_WIND_SPEED"),
            self.read_field("SOFT_WIND_DIRECTION"),
            self.read_field("WINDLESS_ENABLE"),
            self.read_field("ANION_ENABLE"),
            self.read_field("SMELLY_ENABLE"),
            self.read_field("SMELLY_THRESHOLD")
        ])


class Message40Body(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.fields = {}
        self.light = body[1] > 0
        self.fields["MAIN_LIGHT_BRIGHTNESS"] = body[2]
        self.fields["NIGHT_LIGHT_ENABLE"] = body[3]
        self.fields["NIGHT_LIGHT_BRIGHTNESS"] = body[4]
        self.fields["RADAR_INDUCTION_ENABLE"] = body[5]
        self.fields["RADAR_INDUCTION_CLOSING_TIME"] = body[6]
        self.fields["LIGHT_INTENSITY_THRESHOLD"] = body[7]
        self.fields["RADAR_SENSITIVITY"] = body[8]
        self.fields["HEATING_ENABLE"] = body[9]
        self.fields["HEATING_TEMPERATURE"]= body[10]
        self.fields["HEATING_SPEED"] = body[11]
        self.fields["HEATING_DIRECTION"] = body[12]
        self.fields["BATH_ENABLE"] = body[13] > 0
        self.fields["BATH_HEATING_TIME"] = body[14]
        self.fields["BATH_TEMPERATURE"] = body[15]
        self.fields["BATH_SPEED"] = body[16]
        self.fields["BATH_DIRECTION"] = body[17]
        self.ventilation = body[18] > 0
        self.fields["VENTILATION_SPEED"] = body[19]
        self.fields["VENTILATION_DIRECTION"] = body[20]
        self.fields["DRYING_ENABLE"] = body[21] > 0
        self.fields["DRYING_TIME"] = body[22]
        self.fields["DRYING_TEMPERATURE"] = body[23]
        self.fields["DRYING_SPEED"] = body[24]
        self.fields["DRYING_DIRECTION"] = body[25]
        self.power = body[26] > 0
        self.fan_speed = 0 if body[27] == 0xFF else 50 if body[27] <= 30 else 100
        self.oscillate = (body[28] == 0xFD)
        self.fields["DELAY_ENABLE"] = body[29]
        self.fields["DELAY_TIME"] = body[30]
        self.current_temperature = body[33]
        self.fields["SOFT_WIND_ENABLE"] = body[38]
        self.fields["SOFT_WIND_TIME"] = body[39]
        self.fields["SOFT_WIND_TEMPERATURE"] = body[40]
        self.fields["SOFT_WIND_SPEED"] = body[41]
        self.fields["SOFT_WIND_DIRECTION"] = body[42]
        self.fields["WINDLESS_ENABLE"] = body[43]
        self.fields["ANION_ENABLE"] = body[44]
        self.fields["SMELLY_ENABLE"] = body[45]
        self.fields["SMELLY_THRESHOLD"] = body[46]


class Message40Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[self.HEADER_LENGTH: -1]
        if self._message_type in [MessageType.set, MessageType.notify1, MessageType.query] and self._body_type == 0x01:
            self.set_body(Message40Body(body))
        self.set_attr()

