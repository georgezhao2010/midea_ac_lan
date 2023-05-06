import logging
from .message import (
    MessageQuery,
    MessageF1Response,
    MessageSet
)
from ...core.device import MiedaDevice
from ...backports.enum import StrEnum

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    mode="mode"
    error_code="error_code"
    response_type="response_type"
    work_status="work_status"
    step_status="step_status"
    work_step="work_step"
    cup_capstatus="cup_capstatus"
    cup_bodystatus="cup_bodystatus"
    curworktime="curworktime"
    curtemperature="curtemperature"
    curwork_speed="curwork_speed"
    temperature_reservehot="temperature_reservehot"
    temperature_reservewarm="temperature_reservewarm"
    time_reservefinish="time_reservefinish"
    time_reservework="time_reservework"
    time_reservewarm="time_reservewarm"
    code_id="code_id"


class MideaF1Device(MiedaDevice):

    def __init__(
            self,
            name: str,
            device_id: int,
            ip_address: str,
            port: int,
            token: str,
            key: str,
            protocol: int,
            model: str,
            customize: str
    ):
        super().__init__(
            name=name,
            device_id=device_id,
            device_type=0xF1,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.mode: None,
            DeviceAttributes.error_code: None,
            DeviceAttributes.response_type: None,
            DeviceAttributes.work_status: None,
            DeviceAttributes.step_status: None,
            DeviceAttributes.work_step: None,
            DeviceAttributes.cup_capstatus: None,
            DeviceAttributes.cup_bodystatus: None,
            DeviceAttributes.curworktime: None,
            DeviceAttributes.curtemperature: None,
            DeviceAttributes.curwork_speed: None,
            DeviceAttributes.temperature_reservehot: None,
            DeviceAttributes.temperature_reservewarm: None,
            DeviceAttributes.time_reservefinish: None,
            DeviceAttributes.time_reservework: None,
            DeviceAttributes.time_reservewarm: None,
            DeviceAttributes.code_id: None
        }

    # @property
    # def modes(self):
    #     return MideaF1Device._modes

    # @property
    # def fan_speeds(self):
    #     return list(MideaF1Device._speeds.values())

    # @property
    # def water_level_sets(self):
    #     return MideaF1Device._water_level_sets

    def build_query(self):
        return [
            MessageQuery(self._device_protocol_version)
        ]

    def process_message(self, msg):
        message = MessageF1Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, status.value):
                self._attributes[status] = getattr(message, status.value)
                new_status[status.value] = getattr(message, status.value)
        return new_status

    def make_message_set(self):
        message = MessageSet(self._device_protocol_version)
        message.mode = self._attributes[DeviceAttributes.mode]
        message.error_code = self._attributes[DeviceAttributes.error_code]
        message.response_type = self._attributes[DeviceAttributes.response_type]
        message.work_status = self._attributes[DeviceAttributes.work_status]
        message.step_status = self._attributes[DeviceAttributes.step_status]
        message.work_step = self._attributes[DeviceAttributes.work_step]
        message.cup_capstatus = self._attributes[DeviceAttributes.cup_capstatus]
        message.cup_bodystatus = self._attributes[DeviceAttributes.cup_bodystatus]
        message.curworktime = self._attributes[DeviceAttributes.curworktime]
        message.curtemperature = self._attributes[DeviceAttributes.curtemperature]
        message.curwork_speed = self._attributes[DeviceAttributes.curwork_speed]
        message.temperature_reservehot = self._attributes[DeviceAttributes.temperature_reservehot]
        message.temperature_reservewarm = self._attributes[DeviceAttributes.temperature_reservewarm]
        message.time_reservefinish = self._attributes[DeviceAttributes.time_reservefinish]
        message.time_reservework = self._attributes[DeviceAttributes.time_reservework]
        message.time_reservewarm = self._attributes[DeviceAttributes.time_reservewarm]
        message.code_id = self._attributes[DeviceAttributes.code_id]

        return message


    def set_attribute(self, attr, value):
        # if attr == DeviceAttributes.prompt_tone:
        #     self._attributes[DeviceAttributes.prompt_tone] = value
        #     self.update_all({DeviceAttributes.prompt_tone.value: value})
        # else:
        #     message = self.make_message_set()
        #     if attr == DeviceAttributes.mode:
        #         if value in MideaF1Device._modes:
        #             message.mode = MideaF1Device._modes.index(value) + 1
        #     elif attr == DeviceAttributes.fan_speed:
        #         if value in MideaF1Device._speeds.values():
        #             message.fan_speed = list(MideaF1Device._speeds.keys())[
        #                 list(MideaF1Device._speeds.values()).index(value)
        #             ]
        #     elif attr == DeviceAttributes.water_level_set:
        #         if value in MideaF1Device._water_level_sets:
        #             message.water_level_set = int(value)
        #     else:
        message = self.make_message_set()

        setattr(message, str(attr), value)
        self.build_send(message)

    @property
    def attributes(self):
        return super().attributes


class MideaAppliance(MideaF1Device):
    pass
