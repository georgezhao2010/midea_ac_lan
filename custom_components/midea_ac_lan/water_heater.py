import logging
import functools as ft
from homeassistant.components.water_heater import *
from homeassistant.const import (
    TEMP_CELSIUS,
    PRECISION_WHOLE,
    ATTR_TEMPERATURE,
    CONF_DEVICE_ID,
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
        return self.current_operation if self._device.get_attribute("power") else STATE_OFF

    @property
    def supported_features(self):
        return WaterHeaterEntityFeature.TARGET_TEMPERATURE | \
               WaterHeaterEntityFeature.OPERATION_MODE

    @property
    def precision(self):
        return PRECISION_WHOLE

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def current_operation(self):
        mode_num = self._device.get_attribute("mode")
        if 0 <= mode_num < len(self._operations):
            return self._operations[mode_num]
        return None

    @property
    def current_temperature(self):
        return self._device.get_attribute("temperature")

    @property
    def target_temperature(self):
        return self._device.get_attribute("target_temperature")

    def set_temperature(self, **kwargs):
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = int(kwargs.get(ATTR_TEMPERATURE))
        self._device.set_attribute("target_temperature", temperature)

    def set_operation_mode(self, operation_mode):
        if operation_mode in self.operation_list:
            self._device.set_attribute(attr="mode", value=self._operations.index(operation_mode))

    @property
    def operation_list(self):
        return self._operations

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
        self._device.entity = self
        self._operations = [
            "None", "e-Plus", "Rapid", "Summer",
            "Winter", "Energy Saving"
        ]

    @property
    def min_temp(self):
        return E2_TEMPERATURE_MIN

    @property
    def max_temp(self):
        return E2_TEMPERATURE_MAX


class MideaE3WaterHeater(MideaWaterHeater):
    def __init__(self, device):
        super().__init__(device)
        self._device.entity = self
        self._operations = [
            "Shower", "Kitchen", "Bathtub",
            "Temperature", "Cloud", "Energy Saving"
        ]

    @property
    def min_temp(self):
        return E3_TEMPERATURE_MIN

    @property
    def max_temp(self):
        return E3_TEMPERATURE_MAX
