import logging
from .message import (
    MessageQuery,
    MessageSet,
    Message40Response
)
try:
    from enum import StrEnum
except ImportError:
    from ...backports.enum import StrEnum
from ...core.device import MiedaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    main_light = "light"
    ventilation_mode = "ventilation_mode"
    blowing_mode = "blowing_mode"
    current_temperature = "current_temperature"


class Midea40Device(MiedaDevice):
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
            device_type=0x40,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.light: False,
            DeviceAttributes.ventilation_mode: False,
            DeviceAttributes.blowing_mode: False,
            DeviceAttributes.current_temperature: None
        }
        self._fields = {}

    def build_query(self):
        return [MessageQuery(self._device_protocol_version)]

    def process_message(self, msg):
        message = Message40Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        self._fields = getattr(message, "fields")
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                value = getattr(message, str(status))
                self._attributes[status] = value
                new_status[str(status)] = value
        return new_status

    def set_attribute(self, attr, value):
        if attr in DeviceAttributes and attr not in [DeviceAttributes.current_temperature]:
            message = MessageSet(self._device_protocol_version)
            message.fields = self._fields
            message.light = self._attributes[DeviceAttributes.light]
            message.ventilation_mode = self._attributes[DeviceAttributes.ventilation_mode]
            message.blowing_mode = self._attributes[DeviceAttributes.blowing_mode]
            if attr in [DeviceAttributes.ventilation_mode,
                        DeviceAttributes.blowing_mode]:
                message.ventilation_mode = False
                message.blowing_mode = False
            setattr(message, str(attr), value)

    @property
    def attributes(self):
        return super().attributes


class MideaAppliance(Midea40Device):
    pass
