import logging
from ...core.device import MiedaDevice
from .message import (
    MessageQuery,
    MessageSetNormal,
    MessageCCResponse
)
from ...backports.enum import StrEnum

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    mode = "mode"
    target_temperature = "target_temperature"
    fan_speed = "fan_speed"

    eco_mode = "eco_mode"
    sleep_mode = "sleep_mode"
    night_light = "night_light"
    aux_heat = "aux_heat"
    swing = "swing"
    ventilation = "ventilation"

    temperature_precision = "temperature_precision"
    fan_speed_level = "fan_speed_level"
    indoor_temperature = "indoor_temperature"

    aux_heat_status = "aux_heat_status"
    auto_aux_heat_running = "auto_aux_heat_running"


class MideaCCDevice(MiedaDevice):
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
            device_type=0xCC,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.power: False,
            DeviceAttributes.mode: 1,
            DeviceAttributes.target_temperature: 26.0,
            DeviceAttributes.fan_speed: 0x80,
            DeviceAttributes.sleep_mode: False,
            DeviceAttributes.eco_mode: False,
            DeviceAttributes.night_light: False,
            DeviceAttributes.ventilation: False,
            DeviceAttributes.aux_heat: False,
            DeviceAttributes.aux_heat_status: 0,
            DeviceAttributes.auto_aux_heat_running: False,
            DeviceAttributes.swing: False,
            DeviceAttributes.fan_speed_level: True,
            DeviceAttributes.indoor_temperature: None,
            DeviceAttributes.temperature_precision: 1
        }

    def build_query(self):
        return [MessageQuery()]

    def process_message(self, msg):
        message = MessageCCResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, status.value):
                self._attributes[status] = getattr(message, status.value)
                new_status[status.value] = getattr(message, status.value)
        aux_heat = \
            self._attributes[DeviceAttributes.aux_heat_status] == 1 or \
            self._attributes[DeviceAttributes.auto_aux_heat_running]
        if self._attributes[DeviceAttributes.aux_heat] != aux_heat:
            self._attributes[DeviceAttributes.aux_heat] = aux_heat
            new_status[DeviceAttributes.aux_heat.value] = self._attributes[DeviceAttributes.aux_heat]
        return new_status

    def make_message_set(self):
        message = MessageSetNormal()
        message.power = self._attributes[DeviceAttributes.power]
        message.mode = self._attributes[DeviceAttributes.mode]
        message.target_temperature = self._attributes[DeviceAttributes.target_temperature]
        message.fan_speed = self._attributes[DeviceAttributes.fan_speed]
        message.eco_mode = self._attributes[DeviceAttributes.eco_mode]
        message.sleep_mode = self._attributes[DeviceAttributes.sleep_mode]
        message.night_light = self._attributes[DeviceAttributes.night_light]
        message.aux_heat_status = self._attributes[DeviceAttributes.aux_heat_status]
        message.swing = self._attributes[DeviceAttributes.swing]
        return message

    def set_target_temperature(self, target_temperature, mode):
        message = self.make_message_set()
        message.target_temperature = target_temperature
        if mode is not None:
            message.power = True
            message.mode = mode
        self.build_send(message)

    def set_attribute(self, attr, value):
        # if nat a sensor
        if attr not in [DeviceAttributes.indoor_temperature,
                        DeviceAttributes.temperature_precision,
                        DeviceAttributes.fan_speed_level,
                        DeviceAttributes.aux_heat_status,
                        DeviceAttributes.auto_aux_heat_running]:
            message = self.make_message_set()
            setattr(message, str(attr), value)
            if attr == DeviceAttributes.mode:
                setattr(message, DeviceAttributes.power.value, True)
            elif attr == DeviceAttributes.eco_mode and value:
                setattr(message, DeviceAttributes.sleep_mode.value, False)
            elif attr == DeviceAttributes.sleep_mode and value:
                setattr(message, DeviceAttributes.eco_mode.value, False)
            elif attr == DeviceAttributes.aux_heat:
                if value:
                    setattr(message, DeviceAttributes.aux_heat_status.value, 1)
                else:
                    setattr(message, DeviceAttributes.aux_heat_status.value, 2)
            self.build_send(message)

    @property
    def attributes(self):
        return super().attributes


class MideaAppliance(MideaCCDevice):
    pass
