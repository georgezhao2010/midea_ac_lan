from .midea_entity import MideaEntity, MIDEA_ENTITIES
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_DEVICE_ID, CONF_SENSORS
from .const import (
    DOMAIN,
    DEVICES
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_sensors = config_entry.options.get(
        CONF_SENSORS, []
    )
    sensors = []
    for entity_key, config in MIDEA_ENTITIES[device.device_type]["entities"].items():
        if config["type"] == "sensor" and entity_key in extra_sensors:
            sensor = ACSwitch(device, entity_key)
            sensors.append(sensor)
    async_add_entities(sensors)


class ACSwitch(MideaEntity, SensorEntity):
    @property
    def device_class(self):
        return self._config.get("device_class")

    @property
    def unit_of_measurement(self):
        return self._config.get("unit")