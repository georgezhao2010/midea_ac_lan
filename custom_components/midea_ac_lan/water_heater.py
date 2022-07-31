import logging
from homeassistant.components.water_heater import *
from homeassistant.const import (
    TEMP_CELSIUS,
    PRECISION_HALVES,
    ATTR_TEMPERATURE,
    CONF_DEVICE_ID,
)

from .const import (
    DOMAIN,
    DEVICES,
    TEMPERATURE_MIN,
    TEMPERATURE_MAX
)
from .midea_entity import MideaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    if device.device_type == 0xe2:
        async_add_entities([MideaE2WaterHeater(device)])


class MideaWaterHeater(MideaEntity, WaterHeaterEntity):
    def __init__(self, device):
        super().__init__(device, "water_heater")
        self._device.entity = self


class MideaE2WaterHeater(MideaWaterHeater):
    pass
