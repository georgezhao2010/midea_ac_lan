from .midea_entity import MideaEntity, MIDEA_ENTITIES
from homeassistant.const import (
    CONF_DEVICE_ID
)
from .const import (
    DOMAIN,
    MANAGERS
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    dm = hass.data[DOMAIN][MANAGERS].get(device_id)
    devices = []
    for entity_key, config in MIDEA_ENTITIES.items():
        if config["type"] == "sensor":
            dev = MideaEntity(dm, entity_key)
            devices.append(dev)
    async_add_entities(devices)
