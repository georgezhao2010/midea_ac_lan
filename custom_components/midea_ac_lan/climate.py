import logging
from homeassistant.components.climate import *
from homeassistant.components.climate.const import *
from homeassistant.const import (
    TEMP_CELSIUS,
    PRECISION_HALVES,
    ATTR_TEMPERATURE,
    CONF_DEVICE_ID,
)

from .const import (
    DOMAIN,
    DEVICES,
)
from .midea.devices.ac.device import DeviceAttributes as ACAttributes
from .midea.devices.cc.device import DeviceAttributes as CCAttributes
from .midea_entity import MideaEntity

_LOGGER = logging.getLogger(__name__)

FAN_SPEED_1 = "Level 1"
FAN_SPEED_2 = "Level 2"
FAN_SPEED_3 = "Level 3"
FAN_SPEED_4 = "Level 4"
FAN_SPEED_5 = "Level 5"
FAN_SPEED_6 = "Level 6"
FAN_SPEED_7 = "Level 7"

TEMPERATURE_MAX = 30
TEMPERATURE_MIN = 17

FAN_SILENCE = "silence"
FAN_FULL_SPEED = "full speed"


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    if device.device_type == 0xac:
        async_add_entities([MideaACClimate(device)])
    elif device.device_type == 0xcc:
        async_add_entities([MideaCCClimate(device)])


class MideaClimate(MideaEntity, ClimateEntity):
    def __init__(self, device):
        super().__init__(device, "climate")
        self._device.entity = self

    @property
    def state(self):
        return self.hvac_mode

    @property
    def supported_features(self):
        return ClimateEntityFeature.TARGET_TEMPERATURE | \
               ClimateEntityFeature.FAN_MODE | \
               ClimateEntityFeature.PRESET_MODE | \
               ClimateEntityFeature.SWING_MODE | \
               ClimateEntityFeature.AUX_HEAT

    @property
    def min_temp(self):
        return TEMPERATURE_MIN

    @property
    def max_temp(self):
        return TEMPERATURE_MAX

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def target_temperature_low(self):
        return TEMPERATURE_MIN

    @property
    def target_temperature_high(self):
        return TEMPERATURE_MAX

    @property
    def hvac_modes(self):
        return self._modes

    @property
    def swing_modes(self):
        return self._swing_modes

    @property
    def is_on(self) -> bool:
        return self.hvac_mode != HVAC_MODE_OFF

    @property
    def hvac_mode(self) -> str:
        if self._device.get_attribute("power"):
            return self._modes[self._device.get_attribute("mode")]
        else:
            return HVAC_MODE_OFF

    @property
    def target_temperature(self):
        return self._device.get_attribute("target_temperature")

    @property
    def current_temperature(self):
        return self._device.get_attribute("indoor_temperature")

    @property
    def is_aux_heat(self):
        return self._device.get_attribute("aux_heat")

    @property
    def preset_modes(self):
        return self._preset_modes

    @property
    def preset_mode(self):
        if self._device.get_attribute("comfort_mode"):
            mode = PRESET_COMFORT
        elif self._device.get_attribute("eco_mode"):
            mode = PRESET_ECO
        elif self._device.get_attribute("boost_mode"):
            mode = PRESET_BOOST
        elif self._device.get_attribute("sleep_mode"):
            mode = PRESET_SLEEP
        else:
            mode = PRESET_NONE
        return mode

    @property
    def extra_state_attributes(self) -> dict:
        return self._device.attributes

    def turn_on(self):
        self._device.set_attribute(attr="power", value=True)

    def turn_off(self):
        self._device.set_attribute(attr="power", value=False)

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
                _LOGGER.error(f"Unknown hvac_mode {hvac_mode}")

    def set_hvac_mode(self, hvac_mode: str) -> None:
        if hvac_mode == HVAC_MODE_OFF:
            self.turn_off()
        else:
            self._device.set_attribute(attr="mode", value=self._modes.index(hvac_mode))

    def set_preset_mode(self, preset_mode: str) -> None:
        old_mode = self.preset_mode
        if preset_mode == PRESET_COMFORT:
            self._device.set_attribute(attr="comfort_mode", value=True)
        elif preset_mode == PRESET_SLEEP:
            self._device.set_attribute(attr="sleep_mode", value=True)
        elif preset_mode == PRESET_ECO:
            self._device.set_attribute(attr="eco_mode", value=True)
        elif preset_mode == PRESET_BOOST:
            self._device.set_attribute(attr="boost_mode", value=True)
        elif old_mode == PRESET_COMFORT:
            self._device.set_attribute(attr="comfort_mode", value=False)
        elif old_mode == PRESET_SLEEP:
            self._device.set_attribute(attr="sleep_mode", value=False)
        elif old_mode == PRESET_ECO:
            self._device.set_attribute(attr="eco_mode", value=False)
        elif old_mode == PRESET_BOOST:
            self._device.set_attribute(attr="boost_mode", value=False)

    def update_state(self, status):
        try:
            self.schedule_update_ha_state()
        except Exception:
            pass

    def turn_aux_heat_on(self) -> None:
        self._device.set_attribute(attr=ACAttributes.aux_heat, value=True)

    def turn_aux_heat_off(self) -> None:
        self._device.set_attribute(attr=ACAttributes.aux_heat, value=False)


class MideaACClimate(MideaClimate):
    def __init__(self, device):
        super().__init__(device)
        self._modes = [HVAC_MODE_OFF, HVAC_MODE_AUTO, HVAC_MODE_COOL, HVAC_MODE_DRY, HVAC_MODE_HEAT, HVAC_MODE_FAN_ONLY]
        self._fan_speeds = {
            FAN_SILENCE: 20,
            FAN_LOW: 40,
            FAN_MEDIUM: 60,
            FAN_HIGH: 80,
            FAN_FULL_SPEED: 100,
            FAN_AUTO: 102
        }
        self._swing_modes = [SWING_OFF, SWING_VERTICAL, SWING_HORIZONTAL, SWING_BOTH]
        self._preset_modes = [PRESET_NONE, PRESET_COMFORT, PRESET_ECO, PRESET_BOOST]

    @property
    def fan_modes(self):
        return list(self._fan_speeds.keys())

    @property
    def fan_mode(self) -> str:
        fan_speed = self._device.get_attribute(ACAttributes.fan_speed)
        if fan_speed > 100:
            return FAN_AUTO
        elif fan_speed > 80:
            return FAN_FULL_SPEED
        elif fan_speed > 60:
            return FAN_HIGH
        elif fan_speed > 40:
            return FAN_MEDIUM
        elif fan_speed > 20:
            return FAN_LOW
        else:
            return FAN_SILENCE

    @property
    def target_temperature_step(self):
        return PRECISION_HALVES

    @property
    def swing_mode(self):
        swing_mode = (1 if self._device.get_attribute(ACAttributes.swing_vertical) else 0) + \
                     (2 if self._device.get_attribute(ACAttributes.swing_horizontal) else 0)
        return self._swing_modes[swing_mode]

    @property
    def outdoor_temperature(self):
        return self._device.get_attribute(ACAttributes.outdoor_temperature)

    def set_fan_mode(self, fan_mode: str) -> None:
        fan_speed = self._fan_speeds.get(fan_mode)
        if fan_speed:
            self._device.set_attribute(attr=ACAttributes.fan_speed, value=fan_speed)

    def set_swing_mode(self, swing_mode: str) -> None:
        swing = self._swing_modes.index(swing_mode)
        swing_vertical = swing & 1 > 0
        swing_horizontal = swing & 2 > 0
        self._device.set_swing(swing_vertical=swing_vertical, swing_horizontal=swing_horizontal)


class MideaCCClimate(MideaClimate):
    def __init__(self, device):
        super().__init__(device)
        self._modes = [HVAC_MODE_OFF, HVAC_MODE_FAN_ONLY, HVAC_MODE_DRY, HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_AUTO]
        self._fan_speeds_7level = {
            FAN_SPEED_1: 0x01,
            FAN_SPEED_2: 0x02,
            FAN_SPEED_3: 0x04,
            FAN_SPEED_4: 0x08,
            FAN_SPEED_5: 0x10,
            FAN_SPEED_6: 0x20,
            FAN_SPEED_7: 0x40,
            FAN_AUTO: 0x80
        }
        self._fan_speeds_3level = {
            FAN_LOW: 0x01,
            FAN_MEDIUM: 0x08,
            FAN_HIGH: 0x40,
            FAN_AUTO: 0x80
        }
        self._swing_modes = [SWING_OFF, SWING_ON]
        self._preset_modes = [PRESET_NONE, PRESET_SLEEP, PRESET_ECO]

    @property
    def fan_modes(self):
        if self._device.get_attribute(CCAttributes.fan_speed_level):
            # 3 classes
            return list(self._fan_speeds_3level.keys())
        else:
            # 7 classes
            return list(self._fan_speeds_7level.keys())

    @property
    def fan_mode(self) -> str:
        if self._device.get_attribute(CCAttributes.fan_speed_level):
            modes = self._fan_speeds_3level
        else:
            modes = self._fan_speeds_7level
        return list(modes.keys())[list(modes.values()).index(self._device.get_attribute(CCAttributes.fan_speed))]

    @property
    def target_temperature_step(self):
        return self._device.get_attribute(CCAttributes.temperature_precision)

    @property
    def swing_mode(self):
        return SWING_ON if self._device.get_attribute(CCAttributes.swing) else SWING_OFF

    def set_fan_mode(self, fan_mode: str) -> None:
        fan_speed = self._fan_speeds_7level.get(fan_mode) or self._fan_speeds_3level.get(fan_mode)
        if fan_speed:
            self._device.set_attribute(attr=CCAttributes.fan_speed, value=fan_speed)

    def set_swing_mode(self, swing_mode: str) -> None:
        self._device.set_attribute(attr=CCAttributes.swing, value=(swing_mode == SWING_ON))
