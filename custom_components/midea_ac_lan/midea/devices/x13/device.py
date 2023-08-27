import logging
from .message import (
    MessageQuery,
    MessageSet,
    Message13Response
)
try:
    from enum import StrEnum
except ImportError:
    from ...backports.enum import StrEnum
from ...core.device import MiedaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    brightness = "brightness"
    color_temperature = "color_temperature"
    rgb_color = "rgb_color"
    effect = "effect"
    power = "power"
    delay_off = "delay_off"


class Midea13Device(MiedaDevice):
    _effects = ["Manual", "Living", "Reading", "Mildly", "Film", "Bright"]

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
            device_type=0x13,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.brightness: None,
            DeviceAttributes.color_temperature: None,
            DeviceAttributes.rgb_color: None,
            DeviceAttributes.effect: None,
            DeviceAttributes.power: False,
            DeviceAttributes.delay_off: False
        }
        self._fields = {}

    @property
    def effects(self):
        return Midea13Device._effects

    def build_query(self):
        return [MessageQuery(self._device_protocol_version)]

    def process_message(self, msg):
        message = Message13Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                value = getattr(message, str(status))
                self._attributes[status] = value
                new_status[str(status)] = value
        return new_status

    def set_attribute(self, attr, value):
        if attr in [DeviceAttributes.brightness,
                    DeviceAttributes.color_temperature,
                    DeviceAttributes.effect,
                    DeviceAttributes.power,
                    DeviceAttributes.delay_off]:
            message = MessageSet(self._device_protocol_version)
            if attr == DeviceAttributes.effect and value in self._effects:
                setattr(message, str(attr), self._effects.index(value))
            else:
                setattr(message, str(attr), value)
            self.build_send(message)

    @property
    def attributes(self):
        return super().attributes


class MideaAppliance(Midea13Device):
    pass
