import logging
from .message import (
    MessageQuery,
    MessageSwitchDisplay,
    MessageNewProtocolQuery,
    MessageACResponse,
    MessageGeneralSet,
    MessageNewProtocolSet,
    MessagePowerQuery
)
from ...core.device import MiedaDevice
from ...backports.enum import StrEnum

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    prompt_tone = "prompt_tone"

    power = "power"
    mode = "mode"
    target_temperature = "target_temperature"
    fan_speed = "fan_speed"

    swing_vertical = "swing_vertical"
    swing_horizontal = "swing_horizontal"
    boost_mode = "boost_mode"
    smart_eye = "smart_eye"
    dry = "dry"
    eco_mode = "eco_mode"
    aux_heat = "aux_heat"
    sleep_mode = "sleep_mode"
    natural_wind = "natural_wind"
    temp_fahrenheit = "temp_fahrenheit"
    screen_display = "screen_display"
    full_dust = "full_dust"
    comfort_mode = "comfort_mode"

    indoor_temperature = "indoor_temperature"
    outdoor_temperature = "outdoor_temperature"

    indirect_wind = "indirect_wind"
    indoor_humidity = "indoor_humidity"
    breezeless = "breezeless"
    night_light = "night_light"

    total_energy_consumption = "total_energy_consumption"
    current_energy_consumption = "current_energy_consumption"
    realtime_power = "realtime_power"


class MideaACDevice(MiedaDevice):
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
            device_type=0xAC,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.prompt_tone: True,
            DeviceAttributes.power: False,
            DeviceAttributes.mode: 0,
            DeviceAttributes.target_temperature: 24.0,
            DeviceAttributes.fan_speed: 102,
            DeviceAttributes.swing_vertical: False,
            DeviceAttributes.swing_horizontal: False,
            DeviceAttributes.boost_mode: False,
            DeviceAttributes.smart_eye: False,
            DeviceAttributes.dry: False,
            DeviceAttributes.eco_mode: False,
            DeviceAttributes.aux_heat: False,
            DeviceAttributes.sleep_mode: False,
            DeviceAttributes.night_light: False,
            DeviceAttributes.natural_wind: False,
            DeviceAttributes.temp_fahrenheit: False,
            DeviceAttributes.screen_display: False,
            DeviceAttributes.full_dust: False,
            DeviceAttributes.comfort_mode: False,
            DeviceAttributes.indoor_temperature: None,
            DeviceAttributes.outdoor_temperature: None,
            DeviceAttributes.indirect_wind: False,
            DeviceAttributes.indoor_humidity: None,
            DeviceAttributes.breezeless: False,
            DeviceAttributes.total_energy_consumption: None,
            DeviceAttributes.current_energy_consumption: None,
            DeviceAttributes.realtime_power: None
        }

    def build_query(self):
        return [
            MessageQuery(self._device_protocol_version),
            MessageNewProtocolQuery(self._device_protocol_version),
            MessagePowerQuery(self._device_protocol_version)
        ]

    def process_message(self, msg):
        message = MessageACResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, status.value):
                self._attributes[status] = getattr(message, status.value)
                new_status[status.value] = getattr(message, status.value)
        if (DeviceAttributes.power in new_status and not self._attributes[DeviceAttributes.power]) or \
                (DeviceAttributes.swing_vertical in new_status and self._attributes[DeviceAttributes.swing_vertical]):
            self._attributes[DeviceAttributes.indirect_wind] = False
            new_status[DeviceAttributes.indirect_wind.value] = False
        return new_status

    def make_message_set(self):
        message = MessageGeneralSet(self._device_protocol_version)
        message.power = self._attributes[DeviceAttributes.power]
        message.prompt_tone = self._attributes[DeviceAttributes.prompt_tone]
        message.mode = self._attributes[DeviceAttributes.mode]
        message.target_temperature = self._attributes[DeviceAttributes.target_temperature]
        message.fan_speed = self._attributes[DeviceAttributes.fan_speed]
        message.swing_vertical = self._attributes[DeviceAttributes.swing_vertical]
        message.swing_horizontal = self._attributes[DeviceAttributes.swing_horizontal]
        message.boost_mode = self._attributes[DeviceAttributes.boost_mode]
        message.smart_eye = self._attributes[DeviceAttributes.smart_eye]
        message.dry = self._attributes[DeviceAttributes.dry]
        message.eco_mode = self._attributes[DeviceAttributes.eco_mode]
        message.aux_heat = self._attributes[DeviceAttributes.aux_heat]
        message.sleep_mode = self._attributes[DeviceAttributes.sleep_mode]
        message.natural_wind = self._attributes[DeviceAttributes.natural_wind]
        message.temp_fahrenheit = self._attributes[DeviceAttributes.temp_fahrenheit]
        message.comfort_mode = self._attributes[DeviceAttributes.comfort_mode]
        return message

    def set_attribute(self, attr, value):
        # if nat a sensor
        if attr not in [DeviceAttributes.indoor_temperature,
                        DeviceAttributes.outdoor_temperature,
                        DeviceAttributes.indoor_humidity]:
            if attr == DeviceAttributes.prompt_tone:
                self._attributes[DeviceAttributes.prompt_tone] = value
                self.update_all({DeviceAttributes.prompt_tone.value: value})
            elif attr == DeviceAttributes.screen_display:
                message = MessageSwitchDisplay(self._device_protocol_version)
                self.build_send(message)
            elif attr in [DeviceAttributes.indirect_wind, DeviceAttributes.breezeless, DeviceAttributes.night_light]:
                message = MessageNewProtocolSet(self._device_protocol_version)
                setattr(message, str(attr), value)
                message.prompt_tone = self._attributes[DeviceAttributes.prompt_tone]
                self.build_send(message)
            elif attr in self._attributes.keys():
                message = self.make_message_set()
                setattr(message, str(attr), value)
                if attr == DeviceAttributes.mode:
                    setattr(message, DeviceAttributes.power.value, True)
                self.build_send(message)

    def set_target_temperature(self, target_temperature, mode):
        message = self.make_message_set()
        message.target_temperature = target_temperature
        if mode is not None:
            message.power = True
            message.mode = mode
        self.build_send(message)

    def set_swing(self, swing_vertical, swing_horizontal):
        message = self.make_message_set()
        message.swing_vertical = swing_vertical
        message.swing_horizontal = swing_horizontal
        self.build_send(message)

    @property
    def attributes(self):
        return super().attributes


class MideaAppliance(MideaACDevice):
    pass
