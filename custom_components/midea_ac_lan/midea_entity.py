from homeassistant.helpers.entity import Entity
from .const import DOMAIN
from .midea_devices import MIDEA_DEVICES


class MideaEntity(Entity):
    def __init__(self, device, entity_key: str):
        self._device = device
        self._device.register_update(self.update_state)
        self._config = MIDEA_DEVICES[self._device.device_type]["entities"][entity_key]
        self._entity_key = entity_key
        self._unique_id = f"{DOMAIN}.{self._device.device_id}_{entity_key}"
        self.entity_id = self._unique_id
        self._available = True
        self._device_name = f"Midea {self._device.device_id}"
        self._device_info = {
            "manufacturer": "Midea",
            "model": self._device.model,
            "identifiers": {(DOMAIN, self._device.device_id)},
            "name": MIDEA_DEVICES[self._device.device_type]["name"]
        }
    
    @property
    def device(self):
        return self._device

    @property
    def device_info(self):
        return self._device_info

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def should_poll(self):
        return False

    @property
    def state(self):
        return getattr(self._device, self._entity_key)

    @property
    def name(self):
        return f"{self._device_name} {self._config.get('name')}" if "name" in self._config \
            else self._device_name

    @property
    def available(self):
        return self._device.available

    @property
    def icon(self):
        return self._config.get("icon")

    def update_state(self, status):
        if self._entity_key in status or "available" in status:
            try:
                self.schedule_update_ha_state()
            except Exception:
                pass
