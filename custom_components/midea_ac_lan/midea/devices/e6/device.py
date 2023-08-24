import logging
from .message import (
    MessageQuery,
    MessageSet,
    MessageE6Response
)
try:
    from enum import StrEnum
except ImportError:
    from ...backports.enum import StrEnum
from ...core.device import MiedaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    burning_state = "burning_state"
    heating_power = "heating_power"
    bathing_power = "bathing_power"
    heating_working = "heating_working"
    bathing_working = "bathing_working"
    min_temperature = "temperature_min"
    max_temperature = "temperature_max"
    heating_temperature = "heating_temperature"
    bathing_temperature = "bathing_temperature"
    heating_leaving_temperature = "heating_leaving_temperature"
    bathing_leaving_temperature = "bathing_leaving_temperature"
    heating_returning_temperature = "heating_returning_temperature"
    bathing_returning_temperature = "bathing_returning_temperature"


class MideaE6Device(MiedaDevice):
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
            device_type=0xE6,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.power: False,
            DeviceAttributes.burning_state: None,
            DeviceAttributes.heating_power: True,
            DeviceAttributes.bathing_power: True,
            DeviceAttributes.heating_working: None,
            DeviceAttributes.bathing_working: None,
            DeviceAttributes.min_temperature: [30, 35],
            DeviceAttributes.max_temperature: [80, 60],
            DeviceAttributes.heating_temperature: 50,
            DeviceAttributes.bathing_temperature: 40,
            DeviceAttributes.heating_leaving_temperature: None,
            DeviceAttributes.bathing_leaving_temperature: None,
            DeviceAttributes.heating_returning_temperature: None,
            DeviceAttributes.bathing_returning_temperature: None
        }

    def build_query(self):
        return [MessageQuery(self._device_protocol_version)]

    def process_message(self, msg):
        message = MessageE6Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, status.value):
                self._attributes[status] = getattr(message, status.value)
                new_status[status.value] = self._attributes[status]
        return new_status

    def set_attribute(self, attr, value):
        if attr in [DeviceAttributes.power,
                    DeviceAttributes.heating_temperature,
                    DeviceAttributes.bathing_temperature]:
            message = MessageSet(self._device_protocol_version)
            setattr(message, str(attr), value)
            self.build_send(message)

    @property
    def attributes(self):
        return super().attributes


class MideaAppliance(MideaE6Device):
    pass
