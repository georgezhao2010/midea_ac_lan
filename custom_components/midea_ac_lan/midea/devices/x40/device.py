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
    light = "light"
    mode = "mode"
    power = "power"
    oscillate = "oscillate"
    ventilation = "ventilation"
    current_temperature = "current_temperature"
    fan_speed = "fan_speed"


class Midea40Device(MiedaDevice):
    _modes = {255: "Off", 30: "Low", 100: "High"}

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
            DeviceAttributes.mode: None,
            DeviceAttributes.power: False,
            DeviceAttributes.oscillate: False,
            DeviceAttributes.ventilation: False,
            DeviceAttributes.current_temperature: None,
            DeviceAttributes.fan_speed: None
        }
        self._fields = {}

    @property
    def preset_modes(self):
        return Midea40Device._modes

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
                if status == DeviceAttributes.mode:
                    self._attributes[status] = Midea40Device._modes[value]
                else:
                    self._attributes[status] = value
                new_status[str(status)] = self._attributes[status]
        return new_status

    def set_attribute(self, attr, value):
        if attr in [DeviceAttributes.light,
                    DeviceAttributes.mode,
                    DeviceAttributes.fan_speed,
                    DeviceAttributes.ventilation,
                    DeviceAttributes.oscillate]:
            message = MessageSet(self._device_protocol_version)
            message.fields = self._fields
            message.light = self._attributes[DeviceAttributes.light]
            message.ventilation = self._attributes[DeviceAttributes.ventilation]
            message.oscillate = self._attributes[DeviceAttributes.oscillate]
            message.fan_speed = self._attributes[DeviceAttributes.fan_speed]
            message.power = self._attributes[DeviceAttributes.power]
            if attr == DeviceAttributes.mode:
                message.fan_speed = list(Midea40Device._modes.keys())[
                    list(Midea40Device._modes.values()).index(self._attributes[value])
                ]
                message.power = (message.fan_speed > 0)
            elif attr == DeviceAttributes.fan_speed:
                message.fan_speed = value
                message.power = (message.fan_speed > 0)
            elif attr == DeviceAttributes.power:
                message.power = value
                if message.power:
                    if message.fan_speed == 0:
                        message.fan_speed = 50
                else:
                    message.fan_speed = 0
            else:
                setattr(message, str(attr), value)

    @property
    def attributes(self):
        return super().attributes


class MideaAppliance(Midea40Device):
    pass
