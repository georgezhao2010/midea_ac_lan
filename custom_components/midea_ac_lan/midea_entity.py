from .const import DOMAIN
from homeassistant.helpers.entity import Entity
from .state_manager import DeviceManager
from homeassistant.const import (
    TEMP_CELSIUS,
    DEVICE_CLASS_TEMPERATURE
)

MIDEA_ENTITIES = {
    "climate": {
        "type": "climate",
        "icon": "hass:air-conditioner",
        "should_poll": False
    },
    "swing_horizontal": {
        "type": "switch",
        "name": "Swing Horizontal",
        "icon": "hass:arrow-split-vertical",
        "switch": "set_swing_horizontal",
        "should_poll": False
    },
    "swing_vertical": {
        "type": "switch",
        "name": "Swing Vertical",
        "icon": "hass:arrow-split-horizontal",
        "switch": "set_swing_vertical",
        "should_poll": False
    },
    "eco_mode": {
        "type": "switch",
        "name": "ECO Mode",
        "icon": "hass:alpha-e-circle",
        "switch": "set_eco_mode",
        "should_poll": False
    },
    "comfort_mode": {
        "type": "switch",
        "name": "Comfort Mode",
        "icon": "hass:alpha-c-circle",
        "switch": "set_comfort_mode",
        "should_poll": False
    },
    "indirect_wind": {
        "type": "switch",
        "name": "Indirect Wind",
        "icon": "hass:weather-windy",
        "switch": "set_indirect_wind",
        "should_poll": False
    },
    "prompt_tone": {
        "type": "switch",
        "name": "Prompt Tone",
        "icon": "hass:bell",
        "switch": "set_prompt_tone",
        "should_poll": True
    },
    "outdoor_temperature": {
        "type": "sensor",
        "name": "Temperature Outdoor",
        "unit": TEMP_CELSIUS,
        "device_class": DEVICE_CLASS_TEMPERATURE,
        "should_poll": False
    }
}


class MideaEntity(Entity):
    def __init__(self, device_manager: DeviceManager, entity_key: str):
        self._dm = device_manager
        self._dm.add_update(self.update_state)
        self._config = MIDEA_ENTITIES[entity_key]
        self._entity_key = entity_key
        self._unique_id = f"{DOMAIN}.{self._dm.device_id}_{entity_key}"
        self.entity_id = self._unique_id
        self._available = False
        self._device_name = f"Midea AC {self._dm.device_id}"
        self._device_info = {
            "manufacturer": "Midea",
            "model": self._dm.model,
            "identifiers": {(DOMAIN, self._dm.device_id)},
            "name": self._device_name
        }
        self._state = self._dm.get_status(entity_key)

    @property
    def device_info(self):
        return self._device_info

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def should_poll(self):
        return self._config.get("should_poll")

    @property
    def state(self):
        return self._state

    @property
    def device_class(self):
        return self._config.get("device_class")

    @property
    def name(self):
        return f"{self._device_name} {self._config.get('name')}" if "name" in self._config \
            else self._device_name

    @property
    def available(self):
        return self._available

    @property
    def unit_of_measurement(self):
        return self._config.get("unit")

    @property
    def icon(self):
        return self._config.get("icon")

    def _update_state(self, status):
        result = False
        if self._available != status.get("available"):
            self._available = status.get("available")
            result = True
        if self._entity_key in status:
            value = status[self._entity_key]
            if value != self._state:
                self._state = value
                result = True
        return result

    def update_state(self, status):
        if self._update_state(status):
            self.schedule_update_ha_state()
