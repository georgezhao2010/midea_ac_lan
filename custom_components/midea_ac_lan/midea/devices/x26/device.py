import logging
from .message import (
    MessageQuery,
    MessageSet,
    Message26Response
)
try:
    from enum import StrEnum
except ImportError:
    from ...backports.enum import StrEnum
from ...core.device import MiedaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    main_light = "main_light"
    night_light = "night_light"
    heating_mode = "heating_mode"
    bath_mode = "bath_mode"
    ventilation_mode = "ventilation_mode"
    drying_mode = "drying_mode"
    blowing_mode = "blowing_mode"
    gentle_wind_mode = "gentle_wind_mode"
    current_temperature = "current_temperature"


class Midea26Device(MiedaDevice):
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
            device_type=0x26,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.main_light: False,
            DeviceAttributes.night_light: False,
            DeviceAttributes.heating_mode: False,
            DeviceAttributes.bath_mode: False,
            DeviceAttributes.ventilation_mode: False,
            DeviceAttributes.drying_mode: False,
            DeviceAttributes.blowing_mode: False,
            DeviceAttributes.gentle_wind_mode: False,
            DeviceAttributes.current_temperature: None
        }
        self._fields = {}

    def build_query(self):
        return [MessageQuery(self._device_protocol_version)]

    def process_message(self, msg):
        message = Message26Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        self._fields = getattr(message, "fields")
        for status in self._attributes.keys():
            if hasattr(message, status.value):
                value = getattr(message, status.value)
                self._attributes[status] = value
                new_status[status.value] = value
        return new_status

    def set_attribute(self, attr, value):
        if attr in DeviceAttributes and attr not in [DeviceAttributes.current_temperature]:
            message = MessageSet(self._device_protocol_version)
            message.fields = self._fields
            message.main_light = self._attributes[DeviceAttributes.main_light]
            message.night_light = self._attributes[DeviceAttributes.night_light]
            message.heating_mode = self._attributes[DeviceAttributes.heating_mode]
            message.bath_mode = self._attributes[DeviceAttributes.bath_mode]
            message.ventilation_mode = self._attributes[DeviceAttributes.ventilation_mode]
            message.drying_mode = self._attributes[DeviceAttributes.drying_mode]
            message.blowing_mode = self._attributes[DeviceAttributes.blowing_mode]
            message.gentle_wind_mode = self._attributes[DeviceAttributes.gentle_wind_mode]
            if attr in [DeviceAttributes.heating_mode,
                        DeviceAttributes.bath_mode,
                        DeviceAttributes.ventilation_mode,
                        DeviceAttributes.drying_mode,
                        DeviceAttributes.blowing_mode,
                        DeviceAttributes.gentle_wind_mode]:
                message.heating_mode = False
                message.bath_mode = False
                message.ventilation_mode = False
                message.drying_mode = False
                message.blowing_mode = False
                message.gentle_wind_mode = False
            setattr(message, str(attr), value)
            self.build_send(message)

    @property
    def attributes(self):
        return super().attributes


class MideaAppliance(Midea26Device):
    pass
