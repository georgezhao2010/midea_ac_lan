import logging
import functools as ft
from homeassistant.components.water_heater import *
from homeassistant.const import (
    TEMP_CELSIUS,
    PRECISION_WHOLE,
    ATTR_TEMPERATURE,
    CONF_DEVICE_ID,
    STATE_ON,
    STATE_OFF,
)
from .const import (
    DOMAIN,
    DEVICES
)
from .midea_entity import MideaEntity

E2_TEMPERATURE_MAX = 75
E2_TEMPERATURE_MIN = 30
E3_TEMPERATURE_MAX = 65
E3_TEMPERATURE_MIN = 35

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    if device.device_type == 0xe2:
        async_add_entities([MideaE2WaterHeater(device)])
    elif device.device_type == 0xe3:
        async_add_entities([MideaE3WaterHeater(device)])


class MideaWaterHeater(MideaEntity, WaterHeaterEntity):
    def __init__(self, device):
        super().__init__(device, "water_heater")
        self._operations = []

    @property
    def state(self):
        return STATE_ON if self._device.get_attribute("power") else STATE_OFF

    @property
    def supported_features(self):
        return WaterHeaterEntityFeature.TARGET_TEMPERATURE

    @property
    def extra_state_attributes(self) -> dict:
        return self._device.attributes

    @property
    def precision(self):
        return PRECISION_WHOLE

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def current_operation(self):
        return None

    @property
    def current_temperature(self):
        return self._device.get_attribute("current_temperature")

    @property
    def target_temperature(self):
        return self._device.get_attribute("target_temperature")

    def set_temperature(self, **kwargs):
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = int(kwargs.get(ATTR_TEMPERATURE))
        self._device.set_attribute("target_temperature", temperature)

    def set_operation_mode(self, operation_mode):
        pass

    @property
    def operation_list(self):
        return []

    def turn_on(self):
        self._device.set_attribute(attr="power", value=True)

    def turn_off(self):
        self._device.set_attribute(attr="power", value=False)

    async def async_turn_on(self, **kwargs):
        await self.hass.async_add_executor_job(ft.partial(self.turn_on, **kwargs))

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(ft.partial(self.turn_off, **kwargs))

    def update_state(self, status):
        try:
            self.schedule_update_ha_state()
        except Exception:
            pass


class MideaE2WaterHeater(MideaWaterHeater):
    def __init__(self, device):
        super().__init__(device)

    @property
    def min_temp(self):
        return E2_TEMPERATURE_MIN

    @property
    def max_temp(self):
        return E2_TEMPERATURE_MAX


class MideaE3WaterHeater(MideaWaterHeater):
    def __init__(self, device):
        super().__init__(device)

    @property
    def min_temp(self):
        return E3_TEMPERATURE_MIN

    @property
    def max_temp(self):
        return E3_TEMPERATURE_MAX
