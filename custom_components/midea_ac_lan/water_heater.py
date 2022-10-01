import functools as ft
from homeassistant.components.water_heater import *
from homeassistant.const import (
    TEMP_CELSIUS,
    PRECISION_WHOLE,
    ATTR_TEMPERATURE,
    CONF_DEVICE_ID,
    CONF_SWITCHES,
    STATE_ON,
    STATE_OFF,
)
from .const import (
    DOMAIN,
    DEVICES
)
from .midea.devices.c3.device import DeviceAttributes as C3Attributes
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity

E2_TEMPERATURE_MAX = 75
E2_TEMPERATURE_MIN = 30
E3_TEMPERATURE_MAX = 65
E3_TEMPERATURE_MIN = 35


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(
        CONF_SWITCHES, []
    )
    devs = []
    for entity_key, config in MIDEA_DEVICES[device.device_type]["entities"].items():
        if config["type"] == "water_heater" and (config.get("default") or entity_key in extra_switches):
            if device.device_type == 0xE2:
                devs.append(MideaE2WaterHeater(device, entity_key))
            elif device.device_type == 0xE3:
                devs.append(MideaE3WaterHeater(device, entity_key))
            elif device.device_type == 0xC3:
                devs.append(MideaC3WaterHeater(device, entity_key))
    async_add_entities(devs)


class MideaWaterHeater(MideaEntity, WaterHeaterEntity):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)
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
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)

    @property
    def min_temp(self):
        return E2_TEMPERATURE_MIN

    @property
    def max_temp(self):
        return E2_TEMPERATURE_MAX


class MideaE3WaterHeater(MideaWaterHeater):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)

    @property
    def min_temp(self):
        return E3_TEMPERATURE_MIN

    @property
    def max_temp(self):
        return E3_TEMPERATURE_MAX


class MideaC3WaterHeater(MideaWaterHeater):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)

    @property
    def state(self):
        return STATE_ON if self._device.get_attribute(C3Attributes.dhw_power) else STATE_OFF

    @property
    def current_temperature(self):
        return self._device.get_attribute(C3Attributes.tank_actual_temperature)

    @property
    def target_temperature(self):
        return self._device.get_attribute(C3Attributes.dhw_target_temp)

    def set_temperature(self, **kwargs):
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = int(kwargs.get(ATTR_TEMPERATURE))
        self._device.set_attribute(C3Attributes.dhw_target_temp, temperature)

    @property
    def min_temp(self):
        return self._device.get_attribute(C3Attributes.dhw_temp_min)

    @property
    def max_temp(self):
        return self._device.get_attribute(C3Attributes.dhw_temp_max)

    def turn_on(self):
        self._device.set_attribute(attr=C3Attributes.dhw_power, value=True)

    def turn_off(self):
        self._device.set_attribute(attr=C3Attributes.dhw_power, value=False)
