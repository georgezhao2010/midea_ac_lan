import logging
from .message import (
    MessageQuery,
    MessageE2Response,
    MessagePowerOn,
    MessagePowerOff,
)
from ...core.device import MiedaDevice
from enum import Enum

_LOGGER = logging.getLogger(__name__)


class DeviceProperties(Enum):
    power = "power"


class MideaFADevice(MiedaDevice):
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
            device_type=0xFA,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._power = False

    def build_query(self):
        return []

    def process_message(self, msg):
        return {}
