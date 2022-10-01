import logging
import json
from .message import (
    MessageQuery,
    MessageB6Response,
    MessageSet
)
from ...core.device import MiedaDevice
from ...backports.enum import StrEnum

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    light = "light"
    mode = "mode"
    fan_level = "fan_level"
    fan_speed = "fan_speed"
    oilcup_full = "oilcup_full"
    cleaning_reminder = "cleaning_reminder"


class MideaB6Device(MiedaDevice):
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
            device_type=0xB6,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.power: False,
            DeviceAttributes.light: None,
            DeviceAttributes.mode: None,
            DeviceAttributes.fan_level: 0,
            DeviceAttributes.fan_speed: 0,
            DeviceAttributes.oilcup_full: False,
            DeviceAttributes.cleaning_reminder: False
        }
        self._default_speeds = {
            0: "Off", 1: "Level 1", 2: "Level 2"
        }
        self._default_power_speed = 2
        self._power_speed = self._default_power_speed
        self._speeds = self._default_speeds
        self.set_customize(customize)

    @property
    def speed_count(self):
        return len(self._speeds) - 1

    @property
    def preset_modes(self):
        return list(self._speeds.values())

    def build_query(self):
        return [MessageQuery(self._device_protocol_version)]

    def process_message(self, msg):
        message = MessageB6Response(msg)
        self._device_protocol_version = message.device_protocol_version
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, status.value):
                value = getattr(message, status.value)
                if status == DeviceAttributes.fan_level:
                    if value in self._speeds.keys():
                        self._attributes[DeviceAttributes.mode] = self._speeds.get(value)
                        self._attributes[DeviceAttributes.fan_speed] = list(self._speeds.keys()).index(value)
                    else:
                        self._attributes[DeviceAttributes.mode] = None
                        self._attributes[DeviceAttributes.fan_speed] = 0
                    new_status[DeviceAttributes.mode.value] = self._attributes[DeviceAttributes.mode]
                    new_status[DeviceAttributes.fan_speed.value] = self._attributes[DeviceAttributes.fan_speed]
                self._attributes[status] = getattr(message, status.value)
                new_status[status.value] = self._attributes[status]
        return new_status

    def set_attribute(self, attr, value):
        message = None
        if attr == DeviceAttributes.fan_speed:
            if value < len(self._speeds):
                message = MessageSet(self._device_protocol_version)
                message.fan_level = list(self._speeds.keys())[value]
        elif attr == DeviceAttributes.mode:
            if value in self._speeds.values():
                message = MessageSet(self._device_protocol_version)
                message.fan_level = \
                    list(self._speeds.keys())[list(self._speeds.values()).index(value)]
            elif not value:
                message = MessageSet(self._device_protocol_version)
                message.power = False
        elif attr == DeviceAttributes.power:
            message = MessageSet(self._device_protocol_version)
            message.power = value
            message.fan_level = self._power_speed
        elif attr == DeviceAttributes.light:
            message = MessageSet(self._device_protocol_version)
            message.light = value
        if message is not None:
            self.build_send(message)

    @property
    def attributes(self):
        return super().attributes

    def turn_on(self, fan_speed=None, mode=None):
        message = MessageSet(self._device_protocol_version)
        message.power = True
        if fan_speed is not None and fan_speed < len(self._speeds):
            message.fan_level = list(self._speeds.keys())[fan_speed]
        else:
            message.fan_level = self._power_speed
        if mode is not None in self._speeds.values():
            message.fan_level = \
                list(self._speeds.keys())[list(self._speeds.values()).index(mode)]
        self.build_send(message)

    def set_customize(self, customize):
        _LOGGER.debug(f"[{self.device_id}] Customize: {customize}")
        self._speeds = self._default_speeds
        self._power_speed = self._default_power_speed
        if customize:
            try:
                params = json.loads(customize)
                if params:
                    if "default_speed" in params:
                        self._power_speed = int(params.get("default_speed"))
                    if "speeds" in params:
                        self._speeds = {}
                        speeds = {}
                        for k, v in params.get("speeds").items():
                            speeds[int(k)] = v
                        keys = sorted(speeds.keys())
                        for k in keys:
                            self._speeds[k] = speeds[k]
                    self.update_all({"speeds": self._speeds, "default_speed": self._power_speed})
            except Exception as e:
                _LOGGER.error(f"[{self.device_id}] Set customize error: {repr(e)}")


class MideaAppliance(MideaB6Device):
    pass
