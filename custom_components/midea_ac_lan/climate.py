import logging
from homeassistant.components.climate import *
from homeassistant.components.climate.const import *
from homeassistant.const import (
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    PRECISION_HALVES,
    ATTR_TEMPERATURE,
    CONF_DEVICE_ID,
    CONF_TYPE,
)

from .const import (
    DOMAIN,
    DEVICES,
    TEMPERATURE_MIN,
    TEMPERATURE_MAX,
    FAN_VERY_LOW,
    FAN_VERY_HIGH,
    FAN_FULL_SPEED,
)
from .midea.devices.ac.device import MideaACDevice
# from .midea.devices.cc.device import MideaCCDevice
from .midea_entity import MideaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    if device.device_type == 0xac:
        async_add_entities([MideaACClimate(device)])
    #  elif device.device_type == 0xcc:
    #      async_add_entities([MideaCCDevice(device)])


class MideaACClimate(MideaEntity, ClimateEntity):
    def __init__(self, device: MideaACDevice):
        super().__init__(device, "climate")
        self._modes = [HVAC_MODE_OFF, HVAC_MODE_AUTO, HVAC_MODE_COOL, HVAC_MODE_DRY, HVAC_MODE_HEAT, HVAC_MODE_FAN_ONLY]
        self._fan_speeds = {FAN_VERY_LOW: 10,
                            FAN_LOW: 30,
                            FAN_MEDIUM: 50,
                            FAN_HIGH: 70,
                            FAN_VERY_HIGH: 90,
                            FAN_FULL_SPEED: 100,
                            FAN_AUTO: 102}
        self._swing_modes = [SWING_OFF, SWING_VERTICAL, SWING_HORIZONTAL, SWING_BOTH]

    @property
    def state(self):
        return self.hvac_mode

    @property
    def supported_features(self):
        return SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE | SUPPORT_SWING_MODE | SUPPORT_AUX_HEAT

    @property
    def min_temp(self):
        return TEMPERATURE_MIN

    @property
    def max_temp(self):
        return TEMPERATURE_MAX

    @property
    def temperature_unit(self):
        # return TEMP_FAHRENHEIT if self._device.temp_fahrenheit else TEMP_CELSIUS
        return TEMP_CELSIUS

    @property
    def target_temperature_low(self):
        return TEMPERATURE_MIN

    @property
    def target_temperature_high(self):
        return TEMPERATURE_MAX

    @property
    def target_temperature_step(self):
        return PRECISION_HALVES

    @property
    def hvac_modes(self):
        return self._modes

    @property
    def fan_modes(self):
        return list(self._fan_speeds.keys())

    @property
    def swing_modes(self):
        return self._swing_modes

    @property
    def is_on(self) -> bool:
        return self.hvac_modes != HVAC_MODE_OFF

    @property
    def hvac_mode(self) -> str:
        if self._device.power:
            return self._modes[getattr(self._device, "mode")]
        else:
            return HVAC_MODE_OFF

    @property
    def fan_mode(self) -> str:
        if self._device.fan_speed > 100:
            return FAN_AUTO
        elif self._device.fan_speed == 100:
            return FAN_FULL_SPEED
        elif self._device.fan_speed > 80:
            return FAN_VERY_HIGH
        elif self._device.fan_speed > 60:
            return FAN_HIGH
        elif self._device.fan_speed > 40:
            return FAN_MEDIUM
        elif self._device.fan_speed > 20:
            return FAN_LOW
        else:
            return FAN_VERY_LOW

    @property
    def swing_mode(self):
        swing_mode = 1 if self._device.swing_vertical else 0 + \
            2 if self._device.swing_horizontal else 0
        return self._swing_modes[swing_mode]

    @property
    def target_temperature(self):
        return self._device.target_temperature

    @property
    def current_temperature(self):
        return self._device.indoor_temperature

    @property
    def outdoor_temperature(self):
        return self._device.outdoor_temperature

    @property
    def is_aux_heat(self):
        return self._device.aux_heat

    def turn_on(self):
        self._device.power = True

    def turn_off(self):
        self._device.power = False

    def set_temperature(self, **kwargs) -> None:
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = float(kwargs.get(ATTR_TEMPERATURE))
        hvac_mode = kwargs.get(ATTR_HVAC_MODE)
        if hvac_mode == HVAC_MODE_OFF:
            self.turn_off()
        else:
            try:
                mode = self._modes.index(hvac_mode) if hvac_mode else None
                self._device.set_target_temperature(
                    target_temperature=temperature, mode=mode)
            except ValueError as e:
                _LOGGER.error(f"Unknown hvac_mode {hvac_mode} in set_temperature")

    def set_fan_mode(self, fan_mode: str) -> None:
        fan_speed = self._fan_speeds.get(fan_mode)
        if fan_speed:
            self._device.fan_speed = fan_speed

    def set_hvac_mode(self, hvac_mode: str) -> None:
        if hvac_mode == HVAC_MODE_OFF:
            self.turn_off()
        else:
            self._device.mode = self._modes.index(hvac_mode)

    def set_swing_mode(self, swing_mode: str) -> None:
        swing = self._swing_modes.index(swing_mode)
        swing_vertical = swing & 1 > 0
        swing_horizontal = swing & 2 > 0
        self._device.set_swing(swing_vertical=swing_vertical, swing_horizontal=swing_horizontal)

    def turn_aux_heat_on(self) -> None:
        self._device.aux_heat = True

    def turn_aux_heat_off(self) -> None:
        self._device.aux_heat = False

    def update_state(self, status):
        try:
            self.schedule_update_ha_state()
        except Exception:
            pass
    
    @property
    def extra_state_attributes(self) -> dict:
        return self._device.attributes
