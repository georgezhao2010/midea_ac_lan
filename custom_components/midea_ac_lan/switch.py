import logging
from .midea_entity import MideaEntity, MIDEA_ENTITIES
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.const import (
    STATE_ON,
    STATE_OFF,
)
from homeassistant.const import (
    CONF_DEVICE
)
from .const import (
    DOMAIN,
    MANAGERS
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE)
    dm = hass.data[DOMAIN][MANAGERS].get(device_id)
    devices = []
    for entity_key, config in MIDEA_ENTITIES.items():
        if config["type"] == "switch":
            dev = ACSwitch(dm, entity_key)
            devices.append(dev)
    async_add_entities(devices)


class ACSwitch(MideaEntity, ToggleEntity):
    @property
    def is_on(self) -> bool:
        return self._state

    @property
    def state(self):
        return STATE_ON if self._state else STATE_OFF

    def turn_on(self):
        if self._config.get("should_poll"):
            self._state = True
        getattr(self._dm, self._config.get("switch"))(True)

    def turn_off(self):
        if self._config.get("should_poll"):
            self._state = False
        getattr(self._dm, self._config.get("switch"))(False)