import logging
from homeassistant.components.climate import *
from homeassistant.components.climate.const import *
from homeassistant.const import (
    CONF_DEVICE_ID,
    TEMP_CELSIUS,
    PRECISION_HALVES,
    PRECISION_TENTHS,
    ATTR_TEMPERATURE
)
from .const import (
    DOMAIN,
    MANAGERS,
    TEMPERATURE_MIN,
    TEMPERATURE_MAX,
    FAN_VERY_LOW,
    FAN_VERY_HIGH,
    FAN_FULL_SPEED
)
from .state_manager import DeviceManager
from .midea_entity import MideaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    dm = hass.data[DOMAIN][MANAGERS].get(device_id)
    dev = MideaClimate(dm)
    async_add_entities([dev])


class MideaClimate(MideaEntity, ClimateEntity):
    def __init__(self, device_manager: DeviceManager):
        super().__init__(device_manager, "climate")
        self._modes = [HVAC_MODE_OFF, HVAC_MODE_AUTO, HVAC_MODE_COOL, HVAC_MODE_DRY, HVAC_MODE_HEAT, HVAC_MODE_FAN_ONLY]
        self._fan_speeds = {FAN_VERY_LOW: 10,
                            FAN_LOW: 30,
                            FAN_MEDIUM: 50,
                            FAN_HIGH: 70,
                            FAN_VERY_HIGH: 90,
                            FAN_FULL_SPEED: 100,
                            FAN_AUTO: 102}
        self._swing_modes = [SWING_OFF, SWING_VERTICAL, SWING_HORIZONTAL, SWING_BOTH]
        self._is_on = self._dm.get_status("power")
        mode = self._dm.get_status("mode")
        if self._is_on and 0 < mode < len(self._modes):
            self._state = self._modes[mode]
        else:
            self._state = HVAC_MODE_OFF
        self._target_temperature = self._dm.get_status("target_temperature")
        self._indoor_temperature = self._dm.get_status("indoor_temperature")
        self._outdoor_temperature = self._dm.get_status("outdoor_temperature")
        fan_speed = self._dm.get_status("fan_speed")
        if fan_speed > 100:
            self._fan_mode = FAN_AUTO
        elif fan_speed == 100:
            self._fan_mode = FAN_FULL_SPEED
        elif fan_speed > 80:
            self._fan_mode = FAN_VERY_HIGH
        elif fan_speed > 60:
            self._fan_mode = FAN_HIGH
        elif fan_speed > 40:
            self._fan_mode = FAN_MEDIUM
        elif fan_speed > 20:
            self._fan_mode = FAN_LOW
        else:
            self._fan_mode = FAN_VERY_LOW
        swing = 0
        if self._dm.get_status("swing_vertical"):
            swing += 1
        if self._dm.get_status("swing_horizontal"):
            swing += 2
        self._swing_mode = self._swing_modes[swing]

    @property
    def supported_features(self):
        return SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE | SUPPORT_SWING_MODE

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
        return self._is_on

    @property
    def hvac_mode(self) -> str:
        return self.state

    @property
    def fan_mode(self) -> str:
        return self._fan_mode

    @property
    def swing_mode(self):
        return self._swing_mode

    @property
    def target_temperature(self):
        return self._target_temperature

    @property
    def current_temperature(self):
        return self._indoor_temperature

    @property
    def outdoor_temperature(self):
        return self._outdoor_temperature

    def turn_on(self):
        self._dm.set_power(power=True)
        _LOGGER.debug("Turn the device on")

    def turn_off(self):
        self._dm.set_power(power=False)
        _LOGGER.debug("Turn the device off")

    def set_temperature(self, **kwargs) -> None:
        temperature = float(kwargs[ATTR_TEMPERATURE])
        self._dm.set_target_temperature(temperature)

    def set_fan_mode(self, fan_mode: str) -> None:
        fan_speed = self._fan_speeds.get(fan_mode)
        self._dm.set_fan_speed(fan_speed=fan_speed)

    def set_hvac_mode(self, hvac_mode: str) -> None:
        if hvac_mode == HVAC_MODE_OFF:
            self.turn_off()
        else:
            self._dm.set_mode(mode=self._modes.index(hvac_mode))

    def set_swing_mode(self, swing_mode: str) -> None:
        swing = self._swing_modes.index(swing_mode)
        swing_vertical = swing & 1 > 0
        swing_horizontal = swing & 2 > 0
        self._dm.set_swing(swing_vertical=swing_vertical, swing_horizontal=swing_horizontal)

    def _update_state(self, status):
        result = False
        if "power" in status:
            self._is_on = status["power"]
            result = True
        if "mode" in status:
            mode = status["mode"]
            if self._is_on and 0 < mode < len(self._modes):
                self._state = self._modes[mode]
            else:
                self._state = HVAC_MODE_OFF
            result = True
        if "fan_speed" in status:
            fan_speed = status["fan_speed"]
            if fan_speed > 100:
                self._fan_mode = FAN_AUTO
            elif fan_speed == 100:
                self._fan_mode = FAN_FULL_SPEED
            elif fan_speed > 80:
                self._fan_mode = FAN_VERY_HIGH
            elif fan_speed > 60:
                self._fan_mode = FAN_HIGH
            elif fan_speed > 40:
                self._fan_mode = FAN_MEDIUM
            elif fan_speed > 20:
                self._fan_mode = FAN_LOW
            else:
                self._fan_mode = FAN_VERY_LOW
            result = True
        if "swing_vertical" in status and "swing_horizontal" in status:
            swing = 0
            if status["swing_vertical"]:
                swing += 1
            if status["swing_horizontal"]:
                swing += 2
            self._swing_mode = self._swing_modes[swing]
            result = True
        if "target_temperature" in status:
            self._target_temperature = status["target_temperature"]
            result = True
        if "indoor_temperature" in status:
            self._indoor_temperature = status["indoor_temperature"]
            result = True
        if "outdoor_temperature" in status:
            self._outdoor_temperature = status["outdoor_temperature"]
            result = True
        return result

    def update_state(self, status):
        if self._update_state(status):
            self.schedule_update_ha_state()
