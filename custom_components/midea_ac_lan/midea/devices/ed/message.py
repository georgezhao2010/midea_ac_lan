# coding=utf8

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
    heat_start = 0x0400 # 这里实际使用的是 "heat" 控制


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

class MessageQueryff(MessageQuery):  # 厨下净热一体机
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version, device_class=0xff)


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
        if self.heat_start is not None:
            pack_count += 1
            payload.extend(
                EDNewSetParamPack.pack(
                    param=NewSetTags.heat_start,  # heat_start
                    value=0x01 if self.heat_start else 0x00
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


# 参考 T_0000_ED_63200856_2022070501.lua
class EDMessageBodyff(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.device_class = 0xff

        status = {}
        self.parseStatus(body[1:], status)

        if "power" in status:
            self.power = status.get("power") == "on"

        self.in_tds = status.get("in_tds")
        self.out_tds = status.get("out_tds")
        self.life1 = status.get("life_1")
        self.heat_start = bool(status.get("heat_start"))
        self.hot_pot_temperature = status.get("hot_pot_temperature")

    def parseStatus(self, body, status):
        if len(body) < 2:
            return
        leng = (body[2]>>4) + 2
        attr = ((body[2] % 16) <<  8) + body[1]
        if attr == 0x00:
            status["filter"] = "on" if body[3]&0x01 else "off"
            status['wash_enable'] = "on" if body[3]&0x02  else "off"
            status['wash'] = "on" if body[3]&0x04 else "off"
            status['standby_status'] = 1 if body[3]&0x08 else 0
            status['bubble'] = "on" if body[3]&0x10 else "off"
            status['bubble_status'] = "on" if body[3]&0x20 else "off"
            status['save_mode'] = "on" if body[3]&0x40 else "off"
            status['cloud_wash'] = "on" if body[3]&0x80 else "off"

            status['cool'] = "on" if body[4]&0x01 else "off"
            status['heat'] = "on" if body[4]&0x02 else "off"
            status['uv_led'] = "on" if body[4]&0x04 else "off"
            status['germicidal'] = "on" if body[4]&0x08 else "off"
            status['set_germicidal_countdown'] = "on" if body[4]&0x10 else "off"
            status['heat_status'] = "on" if body[4]&0x20 else "off"
            status['set_result'] = "on" if body[4]&0x40 else "off"
            status['gesture'] = "on" if body[4]&0x80 else "off"

            status['lock'] = "on" if body[5]&0x01 else "off"
            status['out_water'] = "on" if body[5]&0x02 else "off"
            status['lack_water'] = "on" if body[5]&0x04 else "off"
            status['full'] = "on" if body[5]&0x08 else "off"
            status['waste_water'] = "on" if body[5]&0x10 else "off"
            status['drainage'] = "on" if body[5]&0x20 else "off"
            status['out_hot_water'] = "on" if body[5]&0x40 else "off"
            status['infrared_outlet'] = "on" if body[5]&0x80 else "off"

            status['power'] = "on" if body[6]&0x01 else "off"
            status['sleep'] = "on" if body[6]&0x02 else "off"
            status['vacation'] = "on" if body[6]&0x04 else "off"
            status['season'] = 1 if body[6]&0x08 else 0
            status['domestic_outlet'] = "on" if body[6]&0x10 else "off"
            status['backflow'] = "on" if body[6]&0x20 else "off"
            status['mixed_water'] = "on" if body[6]&0x40 else "off"
            status['filter_self_cleaning'] = "on" if body[6]&0x80 else "off"
        elif attr == 0x01:
            status["error"] = body[3]
        elif attr == 0x02:
            status['v_version'] = body[3]
            status['e_version'] = body[4]
            status['k_version'] = body[5]
            status['w_version'] = body[6]
        elif attr == 0x03:
            status['current_temperature'] = body[3]
        elif attr == 0x04:
            status['coffee_temperature'] = body[3]
        elif attr == 0x05:
            status['honey_temperature'] = body[3]
        elif attr == 0x06:
            status['milk_temperature'] = body[3]
        elif attr == 0x07:
            status['red_tea_temperature'] = body[3]
        elif attr == 0x08:
            status['black_tea_temperature'] = body[3]
        elif attr == 0x09:
            status['green_tea_temperature'] = body[3]
        elif attr == 0x0A:
            status['yellow_tea_temperature'] = body[3]
        elif attr == 0x0B:
            status['tea_temperature'] = body[3]
        elif attr == 0x0C:
            status['medlar_temperature'] = body[3]
        elif attr == 0x0D:
            status['cool_target_temperature'] = body[3]
        elif attr == 0x0E:
            status['heat_time'] = body[3]
        elif attr == 0x0F:
            status['heat_tea'] = body[3]
        elif attr == 0x10:
            status['life_1'] = body[3]
            status['life_2'] = body[4]
            status['life_3'] = body[5]
            status['life_4'] = body[6]
            status['life_5'] = body[7]
        elif attr == 0x11:
            status['water_consumption'] = (body[6]<<24) + (body[5]<<16) + (body[4]<<8) + body[3]
            status['water_consumption_ml'] = body[5]
        elif attr == 0x12:
            status['hot_water_consumption'] = (body[6]<<24) + (body[5]<<16) + (body[4]<<8) + body[3]
            status['hot_water_consumption_ml'] = body[5]
        elif attr == 0x13:
            status['in_tds'] = (body[4]<<8) + body[3]
            status['out_tds'] = (body[6]<<8) + body[5]
        elif attr == 0x14:
            status['countdown_filter_1'] = body[3]
            status['countdown_filter_2'] = body[4]
            status['countdown_filter_3'] = body[5]
            status['countdown_filter_4'] = body[6]
            status['countdown_filter_5'] = body[7]
        elif attr == 0x15:
            status['air_filter'] = body[3]
        elif attr == 0x16:
            status['maxlife_1'] = body[3]
            status['maxlife_2'] = body[4]
            status['maxlife_3'] = body[5]
            status['maxlife_4'] = body[6]
            status['maxlife_5'] = body[7]
        elif attr == 0x20:
            status['water_kind'] = body[3]
            status['heat_start'] = body[4]
            status['ice_gall_status'] = body[5]
        elif attr == 0x21:
            status['custom_temperature_1'] = body[3]
            status['custom_temperature_2'] = body[4]
            status['custom_temperature_3'] = body[5]
            status['custom_temperature_4'] = body[6]
            status['custom_temperature_5'] = body[7]
        elif attr == 0x22:
            status['custom_temperature_6'] = body[3]
            status['custom_temperature_7'] = body[4]
            status['custom_temperature_8'] = body[5]
            status['custom_temperature_9'] = body[6]
            status['custom_temperature_10'] = body[7]
        elif attr == 0x23:
            status['quantify_1'] = body[3]
            status['quantify_2'] = body[4]
            status['quantify_3'] = body[5]
            status['quantify_4'] = body[6]
            status['quantify_5'] = body[7]
            status['cur_quantify'] = body[8]
        elif attr == 0x24:
            status['quantify_sec'] = (body[4]<<8) + body[3]
            status['cur_quantify_sec'] = (body[6]<<8) + body[5]
        elif attr == 0x25:
            status['keep_warm'] = "on" if body[3]&0x01  else "off"
            status['keep_warm_2'] = "on" if body[3]&0x02  else "off"
            status['keep_warm_time'] = body[4]
            status['warm_left_time'] = (body[6]<<8) + body[5]
        elif attr == 0x26:
            status['special_status'] = body[3]
            status['germicidal_countdown'] = body[4]
            status['set_germicidal_countdown_days'] = body[5]
            status['germicidal_left_time'] = body[6]
        elif attr == 0x27:
            status['rfid_quantify'] = (body[4]<<8) + body[3]
        elif attr == 0x28:
            status['rfid_temp'] = body[3]
        elif attr == 0x29:
            status['rfid_kind'] = body[3]
        elif attr == 0x30:
            status['rfid_id6'] = body[3]
            status['rfid_id5'] = body[4]
            status['rfid_id4'] = body[5]
            status['rfid_id3'] = body[6]
            status['rfid_id2'] = body[7]
            status['rfid_id1'] = body[8]
            status['rfid_id0'] = body[9]
        elif attr == 0x31:
            status['rfid_role'] = body[3]
        elif attr == 0x32:
            status['set_tea_washing'] = body[3]
        elif attr == 0x33:
            status['brew_status'] = body[3]
        elif attr == 0x34:
            status['tea_washing_time'] = body[3]
        elif attr == 0x35:
            status['tea_washing_quantify'] = body[3]
        elif attr == 0x36:
            status['screenout_time'] = (body[4]<<8) + body[3]
        elif attr == 0x37:
            status['effluent_ml'] = (body[4]<<8) + body[3]
            status['outlet_stop'] = body[5]
        elif attr == 0x38:
            status['quantify_21'] = (body[4]<<8) + body[3]
            status['quantify_22'] = (body[6]<<8) + body[5]
            status['quantify_23'] = (body[8]<<8) + body[7]
            status['quantify_24'] = (body[10]<<8) + body[9]
            status['quantify_25'] = (body[12]<<8) + body[11]
        elif attr == 0x39:
            status['quantify_tds_1'] = body[3]
            status['quantify_tds_2'] = body[4]
            status['quantify_tds_3'] = body[5]
            status['quantify_tds_4'] = body[6]
            status['quantify_tds_5'] = body[7]
        elif attr == 0x3A:
            status["plateau_power"] = "on" if body[3]&0x01 else "off"
            status['plateau_boiling_point'] = body[4]
            status['plateau_pressure'] = (body[6]<<8) + body[5]
        elif attr == 0x3B:
            status['hot_pot_temperature'] = body[3]
        elif attr == 0x3C:
            status['antifreeze'] = "on" if body[3]&0x01 else "off"
            status['no_obsolete_water'] = "on" if body[3]&0x40 else "off"

            status['leak_water_protect'] = "on" if body[4]&0x01 else "off"
            status['smart_no_obsolete_water'] = "on" if body[4]&0x08 else "off"
            status['leaking_protect_status'] = "on" if body[4]&0x20 else "off"
            status['gesture_disable_high_temperature'] = "on" if body[4]&0x40 else "off"
        elif attr == 0x3E:
            status['leaking_protect_time'] = body[3]
        elif attr == 0x200:
            status['input_pressure_Sensing'] = (body[4]<<8) + body[3]
        elif attr == 0x202 and len(body) > 4:
            status['water_flow'] = (body[4]<<8) + body[3]
        elif attr == 0x207:
            status['input_temperature_Sensing'] = body[3]

        if len(body)  >= leng:
            self.parseStatus(body[leng:], status)


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
            elif self._body_type == 0xff:
                self._body = EDMessageBodyff(body)
        self.set_attr()


