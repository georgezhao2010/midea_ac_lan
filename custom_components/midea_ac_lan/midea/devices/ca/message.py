from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)


class MessageCABase(MessageRequest):
    def __init__(self, device_protocol_version, message_type, body_type):
        super().__init__(
            device_protocol_version=device_protocol_version,
            device_type=0xCA,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageCABase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query,
            body_type=0x00)

    @property
    def _body(self):
        return bytearray([])


class CAGeneralMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.refrigerator_setting_temp = (body[2] & 0x0f)
        self.freezer_setting_temp = -12 - ((body[2] & 0xf0) >> 4)
        flex_zone_setting_temp = body[3]
        right_flex_zone_setting_temp = body[4]

        if 1 <= flex_zone_setting_temp <= 29:
            self.flex_zone_setting_temp = flex_zone_setting_temp - 19
        elif 49 <= flex_zone_setting_temp <= 54:
            self.flex_zone_setting_temp = 30 - flex_zone_setting_temp
        else:
            self.flex_zone_setting_temp = 0
        if 1 <= right_flex_zone_setting_temp <= 29:
            self.right_flex_zone_setting_temp = right_flex_zone_setting_temp - 19
        elif 49 <= right_flex_zone_setting_temp <= 54:
            self.right_flex_zone_setting_temp = 30 - right_flex_zone_setting_temp
        else:
            self.right_flex_zone_setting_temp = 0

        self.energy_consumption = (body[13] << 8) + body[12]
        self.refrigerator_actual_temp = (body[17] - 100) / 2
        self.freezer_actual_temp = (body[18] - 100) / 2
        self.flex_zone_actual_temp = (body[19] - 100) / 2
        self.right_flex_zone_actual_temp = (body[20] - 100) / 2


class CAExceptionMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.refrigerator_door_overtime = (body[1] & 0x01) > 0
        self.freezer_door_overtime = (body[1] & 0x02) > 0
        self.bar_door_overtime = (body[1] & 0x04) > 0
        self.flex_zone_door_overtime = (body[1] & 0x08) > 0


class CANotify00MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.refrigerator_door = (body[1] & 0x01) > 0
        self.freezer_door = (body[1] & 0x02) > 0
        self.bar_door = (body[1] & 0x04) > 0
        self.flex_zone_door = (body[1] & 0x010) > 0


class CANotify01MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.refrigerator_setting_temp = body[37]
        self.freezer_setting_temp = -12 - body[38]
        flex_zone_setting_temp = body[39]
        right_flex_zone_setting_temp = body[40]

        if 1 <= flex_zone_setting_temp <= 29:
            self.flex_zone_setting_temp = flex_zone_setting_temp - 19
        elif 49 <= flex_zone_setting_temp <= 54:
            self.flex_zone_setting_temp = 30 - flex_zone_setting_temp
        else:
            self.flex_zone_setting_temp = 0
        if 1 <= right_flex_zone_setting_temp <= 29:
            self.right_flex_zone_setting_temp = right_flex_zone_setting_temp - 19
        elif 49 <= right_flex_zone_setting_temp <= 54:
            self.right_flex_zone_setting_temp = 30 - right_flex_zone_setting_temp
        else:
            self.right_flex_zone_setting_temp = 0


class MessageCAResponse(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[self.HEADER_LENGTH: -1]
        if (self._message_type in [MessageType.query, MessageType.set] and self._body_type == 0x00) or \
                (self._message_type == MessageType.notify1 and self._body_type == 0x02):
            self._body = CAGeneralMessageBody(body)
        elif (self._message_type == MessageType.exception and self._body_type == 0x01) or \
                (self._message_type == 0x03 and self._body_type == 0x02):
            self._body = CAExceptionMessageBody(body)
        elif self._message_type == MessageType.notify1 and self._body_type == 0x00:
            self._body = CANotify00MessageBody(body)
        elif self._message_type in [MessageType.query, MessageType.notify1] and self._body_type == 0x01:
            self._body = CANotify01MessageBody(body)
        self.set_attr()