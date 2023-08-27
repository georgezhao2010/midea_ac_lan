import logging
import json
from .message import (
    MessageQuery,
    MessageC2Response,
    MessageSet,
    MessagePowerOn,
    MessagePowerOff,
    C2MessageEnum
)
try:
    from enum import StrEnum
except ImportError:
    from ...backports.enum import StrEnum
from ...core.device import MiedaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    child_lock = "child_lock"
    seat_status = "seat_status"
    lid_status = "lid_status"
    light = "light"
    dry_level = "dry_level"
    water_temp_level = "water_temp_level"
    seat_temp_level = "seat_temp_level"
    water_temperature = "water_temperature"
    seat_temperature = "seat_temperature"
    filter_life = "filter_life"


class MideaC2Device(MiedaDevice):
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
            device_type=0xC2,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.power: False,
            DeviceAttributes.child_lock: False,
            DeviceAttributes.light: False,
            DeviceAttributes.seat_status: None,
            DeviceAttributes.lid_status: None,
            DeviceAttributes.dry_level: 0,
            DeviceAttributes.water_temp_level: 0,
            DeviceAttributes.seat_temp_level: 0,
            DeviceAttributes.water_temperature: None,
            DeviceAttributes.seat_temperature: None,
            DeviceAttributes.filter_life: None
        }
        self._max_dry_level = None
        self._max_water_temp_level = None
        self._max_seat_temp_level = None
        self._default_max_dry_level = 3
        self._default_max_water_temp_level = 5
        self._default_max_seat_temp_level = 5
        self.set_customize(customize)
    @property
    def max_dry_level(self):
        return self._max_dry_level

    @property
    def max_water_temp_level(self):
        return self._max_water_temp_level

    @property
    def max_seat_temp_level(self):
        return self._max_seat_temp_level

    def build_query(self):
        return [MessageQuery(self._device_protocol_version)]

    def process_message(self, msg):
        message = MessageC2Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                self._attributes[status] = getattr(message, str(status))
                new_status[str(status)] = getattr(message, str(status))
        return new_status

    def set_attribute(self, attr, value):
        message = None
        if attr == DeviceAttributes.power:
            if value:
                message = MessagePowerOn(self._device_protocol_version)
            else:
                message = MessagePowerOff(self._device_protocol_version)
        elif attr == DeviceAttributes.child_lock:
            message = MessageSet(self._device_protocol_version, C2MessageEnum.child_lock, value)
        elif attr == DeviceAttributes.light:
            message = MessageSet(self._device_protocol_version, C2MessageEnum.light, value)
        elif attr == DeviceAttributes.water_temp_level:
            message = MessageSet(self._device_protocol_version, C2MessageEnum.water_temp_level, value)
        elif attr == DeviceAttributes.seat_temp_level:
            message = MessageSet(self._device_protocol_version, C2MessageEnum.seat_temp_level, value)
        elif attr == DeviceAttributes.dry_level:
            message = MessageSet(self._device_protocol_version, C2MessageEnum.dry_level, value)
        if message:
            self.build_send(message)

    @property
    def attributes(self):
        return super().attributes

    def set_customize(self, customize):
        _LOGGER.debug(f"[{self.device_id}] Customize: {customize}")
        self._max_dry_level = self._default_max_dry_level
        self._max_water_temp_level = self._default_max_water_temp_level
        self._max_seat_temp_level = self._default_max_seat_temp_level
        if customize and len(customize) > 0:
            try:
                params = json.loads(customize)
                if params and "max_dry_level" in params:
                    self._max_dry_level = params.get("max_dry_level")
                if params and "max_water_temp_level" in params:
                    self._max_water_temp_level = params.get("max_water_temp_level")
                if params and "max_seat_temp_level" in params:
                    self._max_seat_temp_level = params.get("max_seat_temp_level")
            except Exception as e:
                _LOGGER.error(f"[{self.device_id}] Set customize error: {repr(e)}")
            self.update_all({"dry_level": {"max_dry_level": self._max_dry_level},
                             "water_temp_level": {"max_water_temp_level": self._max_water_temp_level},
                             "seat_temp_level": {"max_seat_temp_level": self._max_seat_temp_level}
                             })


class MideaAppliance(MideaC2Device):
    pass
