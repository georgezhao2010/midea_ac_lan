from enum import IntEnum
from ...core.crc8 import calculate
from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody
)


class MessageF1Base(MessageRequest):

    def __init__(self, device_protocol_version, message_type, body_type):
        super().__init__(
            device_protocol_version=device_protocol_version,
            device_type=0xF1,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageF1Base):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query,
            body_type=0xAA)

    @property
    def _body(self):
        return bytearray([
            0x55, 0x00, 0x31,0x00,
            0x00, 0x00
        ])


class MessageSet(MessageF1Base):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.set,
            body_type=0xAA)

    @property
    def _body(self):
        # # byte1, power, prompt_tone
        # power = 0x01 if self.power else 0x00
        # prompt_tone = 0x40 if self.prompt_tone else 0x00
        # # byte2 mode
        # mode = self.mode
        # # byte3 fan_speed
        # fan_speed = self.fan_speed
        # # byte7 target_humidity
        # target_humidity = self.target_humidity
        # # byte8 child_lock
        # child_lock = 0x80 if self.child_lock else 0x00
        # # byte9 anion
        # anion = 0x40 if self.anion else 0x00
        # # byte10 swing
        # swing = 0x08 if self.swing else 0x00
        # # byte 13 water_level_set
        # water_level_set = self.water_level_set
        # return bytearray([0x00] * 23)
        return bytearray([
            0x55,0x00, 0x20,0x00,
            0x00,0x00,0x00,0x00,
            0x00
        ])


class F1GeneralMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        print(f"body:{body}")
        self.mode=body[4]+(body[5] << 8)+(body[6] << 16)+(body[7] << 24)
        self.error_code=body[8]
        self.response_type=body[9]
        self.work_status=body[10]
        self.step_status=body[11]
        self.work_step=body[12]
        self.cup_capstatus=body[13]
        self.cup_bodystatus=body[14]
        self.curworktime= body[15] + (body[16] << 8)
        self.curtemperature= body[17]
        self.curwork_speed=body[18]
        self.temperature_reservehot=body[19]
        self.temperature_reservewarm=body[20]
        self.time_reservefinish=body[21] + (body[22] << 8)
        self.time_reservework= body[23] + (body[24] << 8)
        self.time_reservewarm= body[25]
        self.code_id=body[26]




class MessageF1Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[self.HEADER_LENGTH: -1]
        # self._body = F1GeneralMessageBody(body)

        if (self._message_type in [MessageType.query, MessageType.notify1] and self._body_type == 0xAA) or \
                (self._message_type == MessageType.set and self._body_type in [0xAA]):
            self._body = F1GeneralMessageBody(body)
        self.set_attr()
