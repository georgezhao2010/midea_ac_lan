import logging
from homeassistant.components.fan import *
from homeassistant.const import (
    CONF_DEVICE_ID,
    STATE_ON,
    STATE_OFF
)
from .const import (
    DOMAIN,
    DEVICES,
)
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    climates = []
    for entity_key, config in MIDEA_DEVICES[device.device_type]["entities"].items():
        if config["type"] == "fan":
            if device.device_type == 0xfa:
                climates.append(MideaFAFan(device, entity_key))
    async_add_entities(climates)


class MideaFan(MideaEntity, FanEntity):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)
        self._attr_speed_count = self._device.speed_count

    def turn_on(
            self,
            percentage,
            preset_mode,
            **kwargs,
    ):
        if percentage:
            fan_speed = int(percentage / self.percentage_step + 0.5)
        else:
            fan_speed = None
        self._device.turn_on(fan_speed=fan_speed, mode=preset_mode)

    @property
    def preset_modes(self):
        return self._device.preset_modes

    @property
    def state(self):
        return STATE_ON if self._device.get_attribute("power") else STATE_OFF

    @property
    def is_on(self) -> bool:
        return self.state == STATE_ON

    @property
    def oscillating(self):
        return self._device.get_attribute("oscillate")

    @property
    def preset_mode(self):
        return self._device.get_attribute("mode")

    @property
    def fan_speed(self):
        return self._device.get_attribute("fan_speed")

    def turn_off(self):
        self._device.set_attribute(attr="power", value=False)

    def toggle(self):
        toggle = not self.is_on
        self._device.set_attribute(attr="power", value=toggle)

    def oscillate(self, oscillating: bool):
        self._device.set_attribute(attr="oscillate", value=oscillating)

    def set_preset_mode(self, preset_mode: str):
        self._device.set_attribute(attr="mode", value=preset_mode)

    @property
    def percentage(self):
        return int(self.fan_speed * self.percentage_step + 0.5)

    def set_percentage(self, percentage: int):
        fan_speed = int(percentage / self.percentage_step + 0.5)
        self._device.set_attribute(attr="fan_speed", value=fan_speed)

    def update_state(self, status):
        try:
            self.schedule_update_ha_state()
        except Exception:
            pass


class MideaFAFan(MideaFan):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)
        self._attr_supported_features = SUPPORT_SET_SPEED | SUPPORT_OSCILLATE | SUPPORT_PRESET_MODE


class MideaB6Fan(MideaFan):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)
        self._attr_supported_features = SUPPORT_SET_SPEED | SUPPORT_PRESET_MODE

    async def async_set_percentage(self, percentage: int) -> None:
        await self.hass.async_add_executor_job(self.set_percentage, percentage)

