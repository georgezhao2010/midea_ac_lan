import logging
from .midea_entity import MideaEntity, MIDEA_ENTITIES
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.const import (
    STATE_ON,
    STATE_OFF,
    CONF_DEVICE_ID,
    CONF_SWITCHES
)
from .const import (
    DOMAIN,
    DEVICES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(
        CONF_SWITCHES, []
    )
    switches = []
    for entity_key, config in MIDEA_ENTITIES[device.device_type]["entities"].items():
        if config["type"] == "switch" and entity_key in extra_switches:
            dev = ACSwitch(device, entity_key)
            switches.append(dev)
    async_add_entities(switches)


class ACSwitch(MideaEntity, ToggleEntity):
    @property
    def is_on(self) -> bool:
        return getattr(self._device, self._entity_key)

    @property
    def state(self):
        return STATE_ON if getattr(self._device, self._entity_key) else STATE_OFF

    def turn_on(self):
        setattr(self._device, self._entity_key, True)

    def turn_off(self):
        setattr(self._device, self._entity_key, False)
