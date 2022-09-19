import logging
from .message import (
    MessageQuery,
    MessagePower,
    MessageStart,
    MessageDCResponse
)
from ...core.device import MiedaDevice
from ...backports.enum import StrEnum

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    start = "start"
    washing_data = "washing_data"
    progress = "progress"
    time_remaining = "time_remaining"


class MideaDADevice(MiedaDevice):
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
            device_type=0xDC,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.power: False,
            DeviceAttributes.start: False,
            DeviceAttributes.washing_data: bytearray([]),
            DeviceAttributes.progress: "Unknown",
            DeviceAttributes.time_remaining: None
        }

    def build_query(self):
        return [MessageQuery(self._device_protocol_version)]

    def process_message(self, msg):
        message = MessageDCResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        progress = ["Prog0", "Prog1", "Prog2", "Prog3",
                    "Prog4", "Prog5", "Prog6", "Prog7"]
        for status in self._attributes.keys():
            if hasattr(message, status.value):
                if status == DeviceAttributes.progress:
                    self._attributes[status] = progress[getattr(message, status.value)]
                else:
                    self._attributes[status] = getattr(message, status.value)
                new_status[status.value] = self._attributes[status]
        return new_status

    def set_attribute(self, attr, value):
        if attr == DeviceAttributes.power:
            message = MessagePower(self._device_protocol_version)
            message.power = value
            self.build_send(message)
        elif attr == DeviceAttributes.start:
            message = MessageStart(self._device_protocol_version)
            message.start = value
            message.washing_data = self._attributes[DeviceAttributes.washing_data]
            self.build_send(message)


class MideaAppliance(MideaDADevice):
    pass
