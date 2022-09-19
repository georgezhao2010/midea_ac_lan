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
    mode = "mode"
    additional = "additional"
    door = "door"
    rinse_aid = "rinse_aid"
    salt = "salt"
    child_lock = "child_lock"
    uv = "uv"
    dry = "dry"
    dry_status = "dry_status"
    storage = "storage"
    storage_status = "storage_status"
    time_remaining = "time_remaining"
    progress = "progress"
    storage_remaining = "storage_remaining"
    temperature = "temperature"
    humidity = "humidity"


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
            model: str,
            customize: str
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
            DeviceAttributes.mode: 0,
            DeviceAttributes.additional: 0,
            DeviceAttributes.uv: False,
            DeviceAttributes.dry: False,
            DeviceAttributes.dry_status: False,
            DeviceAttributes.door: False,
            DeviceAttributes.rinse_aid: False,
            DeviceAttributes.salt: False,
            DeviceAttributes.child_lock: False,
            DeviceAttributes.storage: False,
            DeviceAttributes.storage_status: False,
            DeviceAttributes.time_remaining: None,
            DeviceAttributes.progress: None,
            DeviceAttributes.storage_remaining: None,
            DeviceAttributes.temperature: None,
            DeviceAttributes.humidity: None
        }
        self.modes = {
            1: "Auto",
            2: "Heavy",
            3: "Normal",
            4: "Energy Saving",
            5: "Delicate",
            7: "Quick",
            8: "Rinse",
            19: "Quiet"
        }
        self._status = ["Off", "Idle", "Delay", "Running", "Error"]
        self._progress = ["Idle", "Pre-wash", "Wash", "Rinse", "Dry", "Complete"]

    def build_query(self):
        return [MessageQuery(self._device_protocol_version)]

    def process_message(self, msg):
        message = MessageE1Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, status.value):
                if status == DeviceAttributes.status:
                    v = getattr(message, status.value)
                    if v < len(self._status):
                        self._attributes[status] = self._status[v]
                    else:
                        self._attributes[status] = None
                elif status == DeviceAttributes.progress:
                    v = getattr(message, status.value)
                    if v < len(self._progress):
                        self._attributes[status] = self._progress[v]
                    else:
                        self._attributes[status] = None
                else:
                    self._attributes[status] = getattr(message, status.value)
                new_status[status.value] = self._attributes[status]
        return new_status

    def set_attribute(self, attr, value):
        if attr == DeviceAttributes.power:
            message = MessagePower(self._device_protocol_version)
            message.power = value
            self.build_send(message)
        elif attr == DeviceAttributes.child_lock:
            message = MessageLock(self._device_protocol_version)
            message.lock = value
            self.build_send(message)
        elif attr == DeviceAttributes.storage:
            message = MessageStorage(self._device_protocol_version)
            message.storage = value
            self.build_send(message)


class MideaAppliance(MideaE1Device):
    pass
