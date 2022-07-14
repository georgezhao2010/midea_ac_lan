import logging
from homeassistant.components.climate import *
from homeassistant.components.climate.const import *
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    ATTR_ENTITY_ID,
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
from .midea_entity import MideaEntity

_LOGGER = logging.getLogger(__name__)

SERVICES = {
    "set_fan_speed": {
        "method": "set_fan_speed",
        "schema": vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_id,
            vol.Required("fan_speed"): vol.Any(vol.All(vol.Coerce(int), vol.Range(min=1, max=100)),
                                               vol.All(str, vol.In([FAN_AUTO])))
        })
    },
    "set_eco_mode": {
        "method": "set_eco_mode",
        "schema": vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_id,
            vol.Required("eco_mode"): cv.boolean
        })
    },
    "set_comfort_mode": {
        "method": "set_comfort_mode",
        "schema": vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_id,
            vol.Required("comfort_mode"): cv.boolean
        })
    },
    "set_prompt_tone": {
        "method": "set_prompt_tone",
        "schema": vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_id,
            vol.Required("prompt_tone"): cv.boolean
        })
    },
    "set_indirect_wind": {
        "method": "set_indirect_wind",
        "schema": vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_id,
            vol.Required("indirect_wind"): cv.boolean
        })
    },
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device_type = config_entry.data.get(CONF_TYPE)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    climate = None
    if device_type == 0xac:
        climate = MideaACClimate(device)
    if climate:
        async_add_entities([climate])

    def service_handler(service):
        service_call_data = SERVICES.get(service.service)
        params = {
            key: value for key, value in service.data.items() if key != ATTR_ENTITY_ID
        }
        entity_ids = service.data.get(ATTR_ENTITY_ID)
        devices = []
        if entity_ids:
            devices = [
                dev
                for dev in hass.data[DOMAIN][DEVICES].values()
                if device.entity_id in entity_ids
            ]

        for dev in devices:
            if dev and hasattr(dev, service_call_data["method"]):
                getattr(dev, service_call_data["method"])(**params)

    for service_name, service_data in SERVICES.items():
        schema = service_data.get("schema")
        hass.services.async_register(
            DOMAIN,
            service_name,
            service_handler,
            schema=schema
        )


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
        return TEMP_FAHRENHEIT if self._device.temp_fahrenheit else TEMP_CELSIUS

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

    '''
    def _update_state(self, status):
        result = False
        if (self._temp_units == TEMP_FAHRENHEIT) != status.get("temp_fahrenheit"):
            self._temp_units = TEMP_FAHRENHEIT if status.get("temp_fahrenheit") else TEMP_CELSIUS
        if self._available != status.get("available"):
            self._available = status.get("available")
            result = True
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
            self._fan_speed_num = status["fan_speed"]
            if self._fan_speed_num > 100:
                self._fan_mode = FAN_AUTO
            elif self._fan_speed_num == 100:
                self._fan_mode = FAN_FULL_SPEED
            elif self._fan_speed_num > 80:
                self._fan_mode = FAN_VERY_HIGH
            elif self._fan_speed_num > 60:
                self._fan_mode = FAN_HIGH
            elif self._fan_speed_num > 40:
                self._fan_mode = FAN_MEDIUM
            elif self._fan_speed_num > 20:
                self._fan_mode = FAN_LOW
            else:
                self._fan_mode = FAN_VERY_LOW
            result = True
        if "swing_vertical" in status and "swing_horizontal" in status:
            swing = 0
            if status["swing_vertical"]:
                self._swing_vertical = "on"
                swing += 1
            else:
                self._swing_vertical = "off"
            if status["swing_horizontal"]:
                self._swing_horizontal = "on"
                swing += 2
            else:
                self._swing_horizontal = "off"
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
        if "eco_mode" in status:
            self._eco_mode = self._dm.get_status("eco_mode")
            result = True
        if "comfort_mode" in status:
            self._comfort_mode = self._dm.get_status("comfort_mode")
            result = True
        if "indirect_wind" in status:
            self._indirect_wind = self._dm.get_status("indirect_wind")
            result = True
        if "prompt_tone" in status:
            self._prompt_tone = self._dm.get_status("prompt_tone")
            result = True
        if "aux_heat" in status:
            self._aux_heat = self._dm.get_status("aux_heat")
            result = True
        return result

    def update_state(self, status):
        if self._update_state(status):
            self.schedule_update_ha_state()
    '''
    def update_state(self, status):
        if self._entity_key in status or "available" in status:
            self.async_write_ha_state()
    
    @property
    def extra_state_attributes(self) -> dict:
        ret = {
            "eco_mode": "on" if self._device.eco_mode else "off",
            "comfort_mode": "on" if self._device.comfort_mode else "off",
            "indirect_wind": "on" if self._device.indirect_wind else "off",
            "prompt_tone": "on" if self._device.prompt_tone else "off",
            "fan_speed": "auto" if self._device.fan_speed > 100 else self._device.fan_speed,
            "swing_horizontal": self._device.swing_horizontal,
            "swing_vertical": self._device.swing_vertical
        }
        return ret

