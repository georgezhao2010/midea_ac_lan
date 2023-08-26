import logging
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
    flip_status = "flip_status"
    light = "light"


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
            DeviceAttributes.flip_status: None
        }

    def build_query(self):
        return [MessageQuery(self._device_protocol_version)]

    def process_message(self, msg):
        message = MessageC2Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, status.value):
                self._attributes[status] = getattr(message, status.value)
                new_status[status.value] = getattr(message, status.value)
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
        if message:
            self.build_send(message)

    @property
    def attributes(self):
        return super().attributes


class MideaAppliance(MideaC2Device):
    pass
