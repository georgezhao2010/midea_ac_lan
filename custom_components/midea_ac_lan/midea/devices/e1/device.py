import logging
from .message import (
    MessageQuery,
    MessagePower,
    MessageStorage,
    MessageLock,
    MessageE1Response
)
from ...core.device import MiedaDevice
from ...backports.enum import StrEnum

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    status = "status"
    door = "door"
    rinse_aid = "rinse_aid"
    salt = "salt"
    child_lock = "child_lock"
    storage = "storage"
    time_remaining = "time_remaining"
    progress = "progress"
    storage_remaining = "storage_remaining"


class MideaE1Device(MiedaDevice):
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
            device_type=0xE1,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.power: False,
            DeviceAttributes.status: None,
            DeviceAttributes.door: False,
            DeviceAttributes.rinse_aid: False,
            DeviceAttributes.salt: False,
            DeviceAttributes.child_lock: False,
            DeviceAttributes.storage: False,
            DeviceAttributes.time_remaining: None,
            DeviceAttributes.progress: None,
            DeviceAttributes.storage_remaining: None
        }

    def build_query(self):
        return [MessageQuery()]

    def process_message(self, msg):
        message = MessageE1Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        a_status = ["Off", "Idle", "Delay", "Running", "Error"]
        progress = ["Idle", "Pre-wash", "Wash", "Rinse", "Dry", "Finished", "Storage"]
        for status in self._attributes.keys():
            if hasattr(message, status.value):
                if status == DeviceAttributes.status:
                    v = getattr(message, status.value)
                    if 0 <= v <= 4:
                        self._attributes[status] = a_status[v]
                    else:
                        self._attributes[status] = None
                elif status == DeviceAttributes.progress:
                    v = getattr(message, status.value)
                    if 0 <= v <= 5:
                        self._attributes[status] = progress[v]
                    else:
                        self._attributes[status] = None
                else:
                    self._attributes[status] = getattr(message, status.value)
                new_status[status.value] = self._attributes[status]
        return new_status

    def set_attribute(self, attr, value):
        if attr == DeviceAttributes.power:
            message = MessagePower()
            message.power = value
            self.build_send(message)
        elif attr == DeviceAttributes.child_lock:
            message = MessageLock()
            message.lock = value
            self.build_send(message)
        elif attr == DeviceAttributes.storage:
            message = MessageStorage()
            message.storage = value
            self.build_send(message)


class MideaAppliance(MideaE1Device):
    pass
