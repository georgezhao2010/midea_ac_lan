import logging
from .message import (
    MessageQuery01,
    MessageQuery07,
    MessageEDResponse,
    MessageNewSet,
    MessageOldSet
)
from ...core.device import MiedaDevice
from ...backports.enum import StrEnum

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    water_yield = "water_yield"
    in_tds = "in_tds"
    out_tds = "out_tds"
    filter1 = "filter1"
    filter2 = "filter2"
    filter3 = "filter3"
    life1 = "life1"
    life2 = "life2"
    life3 = "life3"
    child_lock = "child_lock"


class MideaEDDevice(MiedaDevice):

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
            device_type=0xED,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.power: False,
            DeviceAttributes.water_yield: None,
            DeviceAttributes.in_tds: None,
            DeviceAttributes.out_tds: None,
            DeviceAttributes.filter1: None,
            DeviceAttributes.filter2: None,
            DeviceAttributes.filter3: None,
            DeviceAttributes.life1: None,
            DeviceAttributes.life2: None,
            DeviceAttributes.life3: None,
            DeviceAttributes.child_lock: False
        }

    def _use_new_set(self):
        return True if (self._sub_type > 342 or self._sub_type == 340) else False

    def build_query(self):
        return [
            MessageQuery01(self._device_protocol_version),
            MessageQuery07(self._device_protocol_version),
        ]

    def process_message(self, msg):
        message = MessageEDResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, status.value):
                new_status[status.value] = getattr(message, status.value)
                self._attributes[status] = getattr(message, status.value)
        return new_status

    def set_attribute(self, attr, value):
        message = None
        if attr in [DeviceAttributes.power]:
            if self._use_new_set():
                if attr in [
                    DeviceAttributes.power,
                    DeviceAttributes.child_lock
                ]:
                    message = MessageNewSet(self._device_protocol_version)
            else:
                if attr in []:
                    message = MessageOldSet(self._device_protocol_version)
        if message is not None:
            setattr(message, str(attr), value)
            self.build_send(message)

    @property
    def attributes(self):
        return super().attributes


class MideaAppliance(MideaEDDevice):
    pass
