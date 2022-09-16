import logging
from .message import (
    MessageQuery,
    MessageEDResponse,
    MessageSet
)
from ...core.device import MiedaDevice
from ...backports.enum import StrEnum

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    water_litre = "water_litre"
    in_tds = "in_tds"
    out_tds = "out_tds"
    filter1 = "filter1"
    filter2 = "filter2"
    filter3 = "filter3"
    life1 = "life1"
    life2 = "life2"
    life3 = "life3"




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
            model: str
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
            DeviceAttributes.water_litre: 0,
            DeviceAttributes.in_tds: 0,
            DeviceAttributes.out_tds: 0,
            DeviceAttributes.filter1: 0,
            DeviceAttributes.filter2: 0,
            DeviceAttributes.filter3: 0,
            DeviceAttributes.life1: 0,
            DeviceAttributes.life2: 0,
            DeviceAttributes.life3: 0
        }

    def build_query(self):
        return [MessageQuery(self._device_protocol_version)]

    def process_message(self, msg):
        message = MessageEDResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            new_status[status.value] = getattr(message, status.value)
            self._attributes[status] = getattr(message, status.value)
        return new_status

    def set_attribute(self, attr, value):
        message = None

        if message is not None:
            self.build_send(message)

    @property
    def attributes(self):
        return super().attributes


class MideaAppliance(MideaEDDevice):
    pass
