import logging
from ...core.device import MiedaDevice
from .message import (
    MessageQuery,
    MessageCAResponse
)
from ...backports.enum import StrEnum

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    mode = "mode"
    power_consumption = "power_consumption"
    refrigerator_actual_temp = "refrigerator_actual_temp"
    freezer_actual_temp = "freezer_actual_temp"
    flex_zone_actual_temp = "flex_zone_actual_temp"
    right_flex_zone_actual_temp = "right_flex_zone_actual_temp"
    refrigerator_setting_temp = "refrigerator_setting_temp"
    freezer_setting_temp = "freezer_setting_temp"
    flex_zone_setting_temp = "flex_zone_setting_temp"
    right_flex_zone_setting_temp = "right_flex_zone_setting_temp"
    refrigerator_door_overtime = "refrigerator_door_overtime"
    freezer_door_overtime = "freezer_door_overtime"
    bar_door_overtime = "bar_door_overtime"
    flex_zone_door_overtime = "flex_zone_door_overtime"


class MideaCADevice(MiedaDevice):
    def __init__(
            self,
            name: str,
            device_id: int,
            ip_address: str,
            port: int,
            token: str,
            key: str,
            protocol: int,
            model: str
    ):
        super().__init__(
            name=name,
            device_id=device_id,
            device_type=0xCA,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.power_consumption: None,
            DeviceAttributes.refrigerator_actual_temp: None,
            DeviceAttributes.freezer_actual_temp: None,
            DeviceAttributes.flex_zone_actual_temp: None,
            DeviceAttributes.right_flex_zone_actual_temp: None,
            DeviceAttributes.refrigerator_setting_temp: None,
            DeviceAttributes.freezer_setting_temp: None,
            DeviceAttributes.flex_zone_setting_temp: None,
            DeviceAttributes.right_flex_zone_setting_temp: None,
            DeviceAttributes.refrigerator_door_overtime: False,
            DeviceAttributes.freezer_door_overtime: False,
            DeviceAttributes.bar_door_overtime: False,
            DeviceAttributes.flex_zone_door_overtime: False
        }
        self._modes = [""]

    def build_query(self):
        return [MessageQuery(self._device_protocol_version)]

    def process_message(self, msg):
        message = MessageCAResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, status.value):
                self._attributes[status] = getattr(message, status.value)
                new_status[status.value] = getattr(message, status.value)
        return new_status

    def set_attribute(self, attr, value):
        pass

    @property
    def attributes(self):
        return super().attributes


class MideaAppliance(MideaCADevice):
    pass
