from .const import DOMAIN
from homeassistant.helpers.entity import Entity
from homeassistant.const import (
    TEMP_CELSIUS,
    DEVICE_CLASS_TEMPERATURE
)

MIDEA_ENTITIES = {
    0xac: {
        "name": "Midea Air-conditioner",
        "entities": {
            "climate": {
                "type": "climate",
                "icon": "hass:air-conditioner"
            },
            "swing_horizontal": {
                "type": "switch",
                "name": "Swing Horizontal",
                "icon": "hass:arrow-split-vertical"
            },
            "swing_vertical": {
                "type": "switch",
                "name": "Swing Vertical",
                "icon": "hass:arrow-split-horizontal"
            },
            "eco_mode": {
                "type": "switch",
                "name": "ECO Mode",
                "icon": "hass:alpha-e-circle"
            },
            "comfort_mode": {
                "type": "switch",
                "name": "Comfort Mode",
                "icon": "hass:alpha-c-circle"
            },
            "indirect_wind": {
                "type": "switch",
                "name": "Indirect Wind",
                "icon": "hass:weather-windy"
            },
            "prompt_tone": {
                "type": "switch",
                "name": "Prompt Tone",
                "icon": "hass:bell"
            },
            "outdoor_temperature": {
                "type": "sensor",
                "name": "Temperature Outdoor",
                "device_class": DEVICE_CLASS_TEMPERATURE
            }
        }
    },
    0xcc: {
        "name": "Midea AC control panel (not real support yet)",
        "entities": {
            "climate": {
                "type": "climate",
                "icon": "hass:air-conditioner"
            }
        }
    }
}


class MideaEntity(Entity):
    def __init__(self, device, entity_key: str):
        self._device = device
        self._device.register_update(self.update_state)
        self._config = MIDEA_ENTITIES[self._device.device_type]["entities"][entity_key]
        self._entity_key = entity_key
        self._unique_id = f"{DOMAIN}.{self._device.device_id}_{entity_key}"
        self.entity_id = self._unique_id
        self._available = True
        self._device_name = f"Midea {self._device.device_id}"
        self._device_info = {
            "manufacturer": "Midea",
            "model": self._device.model,
            "identifiers": {(DOMAIN, self._device.device_id)},
            "name": MIDEA_ENTITIES[self._device.device_type]["name"]
        }

    @property
    def device_info(self):
        return self._device_info

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def should_poll(self):
        return False  # self._config.get("should_poll")

    @property
    def state(self):
        return getattr(self._device, self._entity_key)

    @property
    def device_class(self):
        return self._config.get("device_class")

    @property
    def name(self):
        return f"{self._device_name} {self._config.get('name')}" if "name" in self._config \
            else self._device_name

    @property
    def available(self):
        return self._device.available

    @property
    def unit_of_measurement(self):
        return self._config.get("unit")

    @property
    def icon(self):
        return self._config.get("icon")

    def update_state(self, status):
        if self._entity_key in status or "available" in status:
            try:
                self.schedule_update_ha_state()
            except AttributeError:
                pass
