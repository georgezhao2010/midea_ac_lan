from .midea_entity import MideaEntity, MIDEA_ENTITIES
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_DEVICE_ID
from .const import (
    DOMAIN,
    DEVICES
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    sensors = []
    for entity_key, config in MIDEA_ENTITIES[device.device_type]["entities"].items():
        if config["type"] == "sensor":
            sensor = ACSwitch(device, entity_key)
            sensors.append(sensor)
    async_add_entities(sensors)


class ACSwitch(MideaEntity, SensorEntity):
    pass
