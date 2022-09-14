import logging
from .message import (
    MessageQuery,
    MessageFAResponse,
    MessageSet
)
from ...core.device import MiedaDevice
from ...backports.enum import StrEnum

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"


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
        }

    def build_query(self):
        return [MessageQuery(self._device_protocol_version)]

    def process_message(self, msg):
        message = MessageFAResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            new_status[status.value] = self._attributes[status]
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
