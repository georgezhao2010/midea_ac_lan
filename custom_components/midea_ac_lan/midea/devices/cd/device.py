import logging
import json
from .message import (
    MessageQuery,
    MessageSet,
    MessageCDResponse
)
try:
    from enum import StrEnum
except ImportError:
    from ...backports.enum import StrEnum
from ...core.device import MiedaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    max_temperature = "max_temperature"
    min_temperature = "min_temperature"
    target_temperature = "target_temperature"
    current_temperature = "target_temperature"
    outdoor_temperature = "outdoor_temperature"
    condenser_temperature = "condenser_temperature"
    compressor_temperature = "compressor_temperature"
    compressor_status = "condenser_status"
    aux_heating = "aux_heating"


class MideaCDDevice(MiedaDevice):
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
            device_type=0xCD,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.power: False,
            DeviceAttributes.max_temperature: 65,
            DeviceAttributes.min_temperature: 35,
            DeviceAttributes.target_temperature: 40,
            DeviceAttributes.current_temperature: None,
            DeviceAttributes.outdoor_temperature: None,
            DeviceAttributes.condenser_temperature: None,
            DeviceAttributes.compressor_temperature: None,
            DeviceAttributes.compressor_status: None,
            DeviceAttributes.aux_heating: None
        }
        self._fields = {}
        self._temperature_step = None
        self._default_temperature_step = 1
        self.set_customize(customize)

    @property
    def temperature_step(self):
        return self._temperature_step

    def build_query(self):
        return [MessageQuery(self._device_protocol_version)]

    def process_message(self, msg):
        message = MessageCDResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        if hasattr(message, "fields"):
            self._fields = getattr(message, "fields")
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                self._attributes[status] = getattr(message, str(status))
                new_status[str(status)] = self._attributes[status]
        return new_status

    def set_attribute(self, attr, value):
        if attr in [DeviceAttributes.power, DeviceAttributes.target_temperature]:
            message = MessageSet(self._device_protocol_version)
            message.fields = self._fields
            message.power = self._attributes[DeviceAttributes.power]
            message.aux_heating = self._attributes[DeviceAttributes.aux_heating]
            message.target_temperature = self._attributes[DeviceAttributes.target_temperature]
            setattr(message, str(attr), value)
            self.build_send(message)

    @property
    def attributes(self):
        return super().attributes

    def set_customize(self, customize):
        super().set_customize(customize)
        self._temperature_step = self._default_temperature_step
        if customize and len(customize) > 0:
            try:
                params = json.loads(customize)
                if params and "temperature_step" in params:
                    self._temperature_step = params.get("temperature_step")
            except Exception as e:
                _LOGGER.error(f"[{self.device_id}] Set customize error: {repr(e)}")
            self.update_all({"temperature_step": self._temperature_step})


class MideaAppliance(MideaCDDevice):
    pass
