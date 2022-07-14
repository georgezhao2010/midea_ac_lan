import logging
from .midea_entity import MideaEntity, MIDEA_ENTITIES
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.const import (
    STATE_ON,
    STATE_OFF,
    DEVICE_ID,
)
from .const import (
    DOMAIN,
    DEVICES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    switches = []
    for entity_key, config in MIDEA_ENTITIES.items():
        if config["type"] == "switch":
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
        """
        if self._config.get("should_poll"):
            self._state = True
        getattr(self._dm, self._config.get("switch"))(True)
        """
        setattr(self._device, self._entity_key, True)

    def turn_off(self):
        """
        if self._config.get("should_poll"):
            self._state = False
        getattr(self._dm, self._config.get("switch"))(False)
        """
        setattr(self._device, self._entity_key, False)

