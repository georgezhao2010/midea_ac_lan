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
    zone_temp_type = "zone_temp_type"
    zone1_room_temp_mode = "zone1_room_temp_mode"
    zone2_room_temp_mode = "zone2_room_temp_mode"
    zone1_water_temp_mode = "zone1_water_temp_mode"
    zone2_water_temp_mode = "zone2_water_temp_mode"
    mode = "mode"
    mode_auto = "mode_auto"
    zone_target_temp = "zone_target_temp"
    dhw_target_temp = "dhw_target_temp"
    room_target_temp = "room_target_temp"
    zone_heating_temp_max = "zone_heating_temp_max"
    zone_heating_temp_min = "zone_heating_temp_min"
    zone_cooling_temp_max = "zone_cooling_temp_max"
    zone_cooling_temp_min = "zone_cooling_temp_min"
    tank_actual_temperature = "tank_actual_temperature"
    room_temp_max = "room_temp_max"
    room_temp_min = "room_temp_min"
    dhw_temp_max = "dhw_temp_max"
    dhw_temp_min = "dhw_temp_min"
    target_temperature = "target_temperature"
    temperature_max = "temperature_max"
    temperature_min = "temperature_min"


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
            DeviceAttributes.zone_temp_type: [False, False],
            DeviceAttributes.zone1_room_temp_mode: False,
            DeviceAttributes.zone2_room_temp_mode: False,
            DeviceAttributes.zone1_water_temp_mode: False,
            DeviceAttributes.zone2_water_temp_mode: False,
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
            DeviceAttributes.tank_actual_temperature: None,
            DeviceAttributes.target_temperature: [25, 25],
            DeviceAttributes.temperature_max: [0, 0],
            DeviceAttributes.temperature_min: [0, 0]
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
        if len(new_status) > 0:
            for zone in [0, 1]:
                if self._attributes[DeviceAttributes.zone_temp_type][zone]:  # Water temp mode
                    self._attributes[DeviceAttributes.target_temperature][zone] = \
                        self._attributes[DeviceAttributes.zone_target_temp][zone]
                    if self._attributes[DeviceAttributes.mode_auto] == 2:  # cooling mode
                        self._attributes[DeviceAttributes.temperature_max][zone] = \
                            self._attributes[DeviceAttributes.zone_cooling_temp_max][zone]
                        self._attributes[DeviceAttributes.temperature_min][zone] = \
                            self._attributes[DeviceAttributes.zone_cooling_temp_min][zone]
                    elif self._attributes[DeviceAttributes.mode] == 3:  # heating mode
                        self._attributes[DeviceAttributes.temperature_max][zone] = \
                            self._attributes[DeviceAttributes.zone_heating_temp_max][zone]
                        self._attributes[DeviceAttributes.temperature_min][zone] = \
                            self._attributes[DeviceAttributes.zone_heating_temp_min][zone]
                else:  # Room temp mode
                    self._attributes[DeviceAttributes.target_temperature][zone] = \
                        self._attributes[DeviceAttributes.room_target_temp]
                    self._attributes[DeviceAttributes.temperature_max][zone] = \
                        self._attributes[DeviceAttributes.room_temp_max]
                    self._attributes[DeviceAttributes.temperature_min][zone] = \
                        self._attributes[DeviceAttributes.room_temp_min]
            if self._attributes[DeviceAttributes.zone1_power]:
                if self._attributes[DeviceAttributes.zone_temp_type][zone]:
                    self._attributes[DeviceAttributes.zone1_water_temp_mode] = True
                    self._attributes[DeviceAttributes.zone1_room_temp_mode] = False
                else:
                    self._attributes[DeviceAttributes.zone1_water_temp_mode] = False
                    self._attributes[DeviceAttributes.zone1_room_temp_mode] = True
            else:
                self._attributes[DeviceAttributes.zone1_water_temp_mode] = False
                self._attributes[DeviceAttributes.zone1_room_temp_mode] = False
            if self._attributes[DeviceAttributes.zone2_power]:
                if self._attributes[DeviceAttributes.zone_temp_type][zone]:
                    self._attributes[DeviceAttributes.zone2_water_temp_mode] = True
                    self._attributes[DeviceAttributes.zone2_room_temp_mode] = False
                else:
                    self._attributes[DeviceAttributes.zone2_water_temp_mode] = False
                    self._attributes[DeviceAttributes.zone2_room_temp_mode] = True
            else:
                self._attributes[DeviceAttributes.zone2_water_temp_mode] = False
                self._attributes[DeviceAttributes.zone2_room_temp_mode] = False
            new_status[DeviceAttributes.zone1_water_temp_mode.value] = \
                self._attributes[DeviceAttributes.zone1_water_temp_mode]
            new_status[DeviceAttributes.zone2_water_temp_mode.value] = \
                self._attributes[DeviceAttributes.zone2_water_temp_mode]
            new_status[DeviceAttributes.zone1_room_temp_mode.value] = \
                self._attributes[DeviceAttributes.zone1_room_temp_mode]
            new_status[DeviceAttributes.zone2_room_temp_mode.value] = \
                self._attributes[DeviceAttributes.zone2_room_temp_mode]

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
        if attr in [
            DeviceAttributes.zone1_power,
            DeviceAttributes.zone2_power,
            DeviceAttributes.dhw_power,
            DeviceAttributes.zone1_curve,
            DeviceAttributes.zone2_curve,
            DeviceAttributes.disinfect,
            DeviceAttributes.fast_dhw,
            DeviceAttributes.dhw_target_temp
        ]:
            message = self.make_message_set()
            setattr(message, str(attr), value)
            self.build_send(message)

    def set_mode(self, zone, mode):
        message = self.make_message_set()
        if zone == 0:
            message.zone1_power = True
        else:
            message.zone2_power = True
        message.mode = mode
        self.build_send(message)

    def set_target_temperature(self, zone, target_temperature, mode):
        message = self.make_message_set()
        if self._attributes[DeviceAttributes.zone_temp_type][zone]:
            message.zone_target_temp[zone] = target_temperature
        else:
            message.room_target_temp = target_temperature
        if mode is not None:
            if zone == 0:
                message.zone1_power = True
            else:
                message.zone2_power = True
            message.mode = mode
        self.build_send(message)

    @property
    def attributes(self):
        return super().attributes


class MideaAppliance(MideaC3Device):
    pass
