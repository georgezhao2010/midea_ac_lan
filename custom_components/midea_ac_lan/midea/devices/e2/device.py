import logging
from .message import (
    MessageQuery,
    MessageSet,
    MessageE2Response,
    MessagePower,
    MessageNewProtocolSet
)
from ...core.device import MiedaDevice
from ...backports.enum import StrEnum

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    heating = "heating"
    keep_warm = "keep_warm"
    protection = "protection"
    current_temperature = "current_temperature"
    target_temperature = "target_temperature"
    whole_tank_heating = "whole_tank_heating"
    variable_heating = "variable_heating"
    heating_time_remaining = "heating_time_remaining"
    water_consumption = "water_consumption"
    heating_power = "heating_power"


class MideaE2Device(MiedaDevice):
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
            device_type=0xE2,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.power: False,
            DeviceAttributes.heating: False,
            DeviceAttributes.keep_warm: False,
            DeviceAttributes.protection: False,
            DeviceAttributes.current_temperature: None,
            DeviceAttributes.target_temperature: 40,
            DeviceAttributes.whole_tank_heating: False,
            DeviceAttributes.variable_heating: False,
            DeviceAttributes.heating_time_remaining: 0,
            DeviceAttributes.water_consumption: None,
            DeviceAttributes.heating_power: None
        }

    def old_protocol(self):
        return self._sub_type <= 82 or self._sub_type == 85 or self._sub_type == 36353

    def build_query(self):
        return [MessageQuery(self._device_protocol_version)]

    def process_message(self, msg):
        message = MessageE2Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, status.value):
                self._attributes[status] = getattr(message, status.value)
                new_status[status.value] = getattr(message, status.value)
        return new_status

    def make_message_set(self):
        message = MessageSet(self._device_protocol_version)
        message.protection = self._attributes[DeviceAttributes.protection]
        message.whole_tank_heating = self._attributes[DeviceAttributes.whole_tank_heating]
        message.target_temperature = self._attributes[DeviceAttributes.target_temperature]
        message.variable_heating = self._attributes[DeviceAttributes.variable_heating]
        return message

    def set_attribute(self, attr, value):
        if attr not in [DeviceAttributes.heating,
                        DeviceAttributes.keep_warm,
                        DeviceAttributes.current_temperature]:
            if attr == DeviceAttributes.power:
                message = MessagePower(self._device_protocol_version)
                message.power = value
            elif self.old_protocol():
                message = self.make_message_set()
                setattr(message, str(attr), value)
            else:
                message = MessageNewProtocolSet(self._device_protocol_version)
                setattr(message, str(attr), value)
            self.build_send(message)


class MideaAppliance(MideaE2Device):
    pass
