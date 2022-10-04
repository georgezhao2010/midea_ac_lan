import logging
from .message import (
    MessageQuery01,
    MessageB0Response
)
from ...core.device import MiedaDevice
from ...backports.enum import StrEnum

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    door = "door"
    status = "status"
    time_remaining = "time_remaining"
    current_temperature = "current_temperature"
    tank_ejected = "tank_ejected"
    water_change_reminder = "water_change_reminder"
    water_shortage = "water_shortage"


class MideaB0Device(MiedaDevice):
    _status = {
        0x01: "Standby", 0x02: "Idle", 0x03: "Working",
        0x04: "Finished", 0x05: "Delay", 0x06: "Paused"
    }

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
            device_type=0xB0,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.door: False,
            DeviceAttributes.status: "Unknown",
            DeviceAttributes.time_remaining: None,
            DeviceAttributes.current_temperature: None,
            DeviceAttributes.tank_ejected: False,
            DeviceAttributes.water_change_reminder: False,
            DeviceAttributes.water_shortage: False,
        }

    def build_query(self):
        return [MessageQuery01(self._device_protocol_version)]

    def process_message(self, msg):
        message = MessageB0Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, status.value):
                value = getattr(message, status.value)
                if status == DeviceAttributes.status:
                    if value in MideaB0Device._status.keys():
                        self._attributes[DeviceAttributes.status] = MideaB0Device._status.get(value)
                    else:
                        self._attributes[DeviceAttributes.status] = "Unknown"
                else:
                    self._attributes[status] = value
                new_status[status.value] = self._attributes[status]
        return new_status

    def set_attribute(self, attr, value):
        pass

    @property
    def attributes(self):
        return super().attributes


class MideaAppliance(MideaB0Device):
    pass
