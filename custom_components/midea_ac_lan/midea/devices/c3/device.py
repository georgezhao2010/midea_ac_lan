import logging
from ...core.device import MiedaDevice
from .message import (
    MessageQuery,
    MessageC3Response,
    MessageSet
)
from ...backports.enum import StrEnum

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    zone1_power = "zone1_power"
    zone2_power = "zone2_power"
    dhw_power = "dhw_power"
    zone1_curve = "zone1_curve"
    zone2_curve = "zone2_curve"
    disinfect = "disinfect"
    fast_dhw = "fast_dhw"
    mode = "mode"
    mode_auto = "mode_auto"
    zone_target_temp = "zone_target_temp"
    dhw_target_temp = "dhw_target_temp"
    room_target_temp = "room_target_temp"
    zone_heating_temp_max = "zone_heating_temp_max"
    zone_heating_temp_min = "zone_heating_temp_min"
    zone_cooling_temp_max = "zone_cooling_temp_max"
    zone_cooling_temp_min = "zone_cooling_temp_min"
    room_temp_max = "room_temp_max"
    room_temp_min = "room_temp_min"
    dhw_temp_max = "dhw_temp_max"
    dhw_temp_min = "dhw_temp_min"
    tank_actual_temperature = "tank_actual_temperature"


class MideaC3Device(MiedaDevice):
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
            device_type=0xC3,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.zone1_power: False,
            DeviceAttributes.zone2_power: False,
            DeviceAttributes.dhw_power: False,
            DeviceAttributes.zone1_curve: False,
            DeviceAttributes.zone2_curve: False,
            DeviceAttributes.disinfect: False,
            DeviceAttributes.fast_dhw: False,
            DeviceAttributes.mode: 1,
            DeviceAttributes.mode_auto: 1,
            DeviceAttributes.zone_target_temp: [25, 25],
            DeviceAttributes.dhw_target_temp: 25,
            DeviceAttributes.room_target_temp: 30,
            DeviceAttributes.zone_heating_temp_max: [55, 55],
            DeviceAttributes.zone_heating_temp_min: [25, 25],
            DeviceAttributes.zone_cooling_temp_max: [25, 25],
            DeviceAttributes.zone_cooling_temp_min: [5, 5],
            DeviceAttributes.room_temp_max: 60,
            DeviceAttributes.room_temp_min: 34,
            DeviceAttributes.dhw_temp_max: 60,
            DeviceAttributes.dhw_temp_min: 20,
            DeviceAttributes.tank_actual_temperature: None
        }

    def build_query(self):
        return [MessageQuery(self._device_protocol_version)]

    def process_message(self, msg):
        message = MessageC3Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, status.value):
                self._attributes[status] = getattr(message, status.value)
                new_status[status.value] = getattr(message, status.value)
        if self._attributes[DeviceAttributes.mode] == 1:  # auto mode
            pass
        elif self._attributes[DeviceAttributes.mode] == 2:  # cooling mode
            pass
        elif self._attributes[DeviceAttributes.mode] == 3:  # heating mode
            pass
        return new_status

    def make_message_set(self):
        message = MessageSet(self._device_protocol_version)
        message.zone1_power = self._attributes[DeviceAttributes.zone1_power]
        message.zone2_power = self._attributes[DeviceAttributes.zone2_power]
        message.dhw_power = self._attributes[DeviceAttributes.dhw_power]
        message.mode = self._attributes[DeviceAttributes.mode]
        message.zone_target_temp = self._attributes[DeviceAttributes.zone_target_temp]
        message.dhw_target_temp = self._attributes[DeviceAttributes.dhw_target_temp]
        message.room_target_temp = self._attributes[DeviceAttributes.room_target_temp]
        message.zone1_curve = self._attributes[DeviceAttributes.zone1_curve]
        message.zone2_curve = self._attributes[DeviceAttributes.zone2_curve]
        message.disinfect = self._attributes[DeviceAttributes.disinfect]
        message.fast_dhw = self._attributes[DeviceAttributes.fast_dhw]
        return message

    def set_attribute(self, attr, value):
        message = self.make_message_set()
        setattr(message, str(attr), value)
        if attr == DeviceAttributes.mode:
            setattr(message, DeviceAttributes.zone1_power.value, True)
            setattr(message, DeviceAttributes.zone2_power.value, True)
        self.build_send(message)

    def set_target_temperature(self, zone, target_temperature, mode):
        message = self.make_message_set()
        message.zone_target_temp[zone] = target_temperature
        if mode is not None:
            message.power = True
            message.mode = mode
        self.build_send(message)

    @property
    def attributes(self):
        return super().attributes


class MideaAppliance(MideaC3Device):
    pass
