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
        self.ventilation_mode = False
        self.blowing_mode = False

    def read_field(self, field):
        value = self.fields.get(field, 0)
        return value if value else 0

    @property
    def _body(self):
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
            self.read_field("HEATING_TEMPERATURE"),
            self.read_field("HEATING_SPEED"),
            self.read_field("HEATING_DIRECTION"),
            self.read_field("BATH_ENABLE"),
            self.read_field("BATH_HEATING_TIME"),
            self.read_field("BATH_TEMPERATURE"),
            self.read_field("BATH_SPEED"),
            self.read_field("BATH_DIRECTION"),
            1 if self.ventilation_mode else 0,
            self.read_field("VENTILATION_SPEED"),
            self.read_field("VENTILATION_DIRECTION"),
            self.read_field("DRYING_ENABLE"),
            self.read_field("DRYING_TIME"),
            self.read_field("DRYING_TEMPERATURE"),
            self.read_field("DRYING_SPEED"),
            self.read_field("DRYING_DIRECTION"),
            1 if self.blowing_mode else 0,
            self.read_field("BLOWING_SPEED"),
            self.read_field("BLOWING_DIRECTION"),
            self.read_field("DELAY_ENABLE"),
            self.read_field("DELAY_TIME"),
            self.read_field("SOFT_WIND_ENABLE"),
            self.read_field("SOFT_WIND_HEATING_TIME"),
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
        self.light = self.read_byte(body, 1) > 0
        self.fields["MAIN_LIGHT_BRIGHTNESS"] = self.read_byte(body, 2)
        self.night_light = self.read_byte(body, 3) > 0
        self.fields["NIGHT_LIGHT_BRIGHTNESS"] = self.read_byte(body, 4)
        self.fields["RADAR_INDUCTION_ENABLE"] = self.read_byte(body, 5)
        self.fields["RADAR_INDUCTION_CLOSING_TIME"] = self.read_byte(body, 6)
        self.fields["LIGHT_INTENSITY_THRESHOLD"] = self.read_byte(body, 7)
        self.fields["RADAR_SENSITIVITY"] = self.read_byte(body, 8)
        self.heating_mode = self.read_byte(body, 9) > 0
        self.fields["HEATING_TEMPERATURE"] = self.read_byte(body, 10)
        self.fields["HEATING_SPEED"] = self.read_byte(body, 11)
        self.fields["HEATING_DIRECTION"] = self.read_byte(body, 12)
        self.bath_mode = self.read_byte(body, 13) > 0
        self.fields["BATH_HEATING_TIME"] = self.read_byte(body, 14)
        self.fields["BATH_TEMPERATURE"] = self.read_byte(body, 15)
        self.fields["BATH_SPEED"] = self.read_byte(body, 16)
        self.fields["BATH_DIRECTION"] = self.read_byte(body, 17)
        self.ventilation_mode = self.read_byte(body, 18) > 0
        self.fields["VENTILATION_SPEED"] = self.read_byte(body, 19)
        self.fields["VENTILATION_DIRECTION"] = self.read_byte(body, 20)
        self.fields["DRYING_ENABLE"] = self.read_byte(body, 21)
        self.fields["DRYING_TIME"] = self.read_byte(body, 22)
        self.drying_mode = self.read_byte(body, 23) > 0
        self.fields["DRYING_SPEED"] = self.read_byte(body, 24)
        self.fields["DRYING_DIRECTION"] = self.read_byte(body, 25)
        self.blowing_mode = self.read_byte(body, 26) > 0
        self.fields["BLOWING_SPEED"] = self.read_byte(body, 27)
        self.fields["BLOWING_DIRECTION"] = self.read_byte(body, 28)
        self.fields["DELAY_ENABLE"] = self.read_byte(body, 29)
        self.fields["DELAY_TIME"] = self.read_byte(body, 30)
        self.current_temperature = self.read_byte(body, 33)
        self.fields["SOFT_WIND_ENABLE"] = self.read_byte(body, 38)
        self.gentle_wind_mode = self.read_byte(body, 39) > 0
        self.fields["SOFT_WIND_TEMPERATURE"] = self.read_byte(body, 40)
        self.fields["SOFT_WIND_SPEED"] = self.read_byte(body, 41)
        self.fields["SOFT_WIND_DIRECTION"] = self.read_byte(body, 42)
        self.fields["WINDLESS_ENABLE"] = self.read_byte(body, 43)
        self.fields["ANION_ENABLE"] = self.read_byte(body, 44)
        self.fields["SMELLY_ENABLE"] = self.read_byte(body, 45)
        self.fields["SMELLY_THRESHOLD"] = self.read_byte(body, 46)


class Message40Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[self.HEADER_LENGTH: -1]
        if self._message_type in [MessageType.set, MessageType.notify1, MessageType.query] and self._body_type == 0x01:
            self._body = Message40Body(body)
        self.set_attr()

