import logging
from homeassistant.components.light import *
from homeassistant.const import (
    Platform,
    CONF_DEVICE_ID,
    CONF_SWITCHES,
    STATE_ON,
    STATE_OFF
)
from .const import (
    DOMAIN,
    DEVICES
)
from .midea.devices.x13.device import DeviceAttributes as X13Attributes
from .midea_entity import MideaEntity
from .midea_devices import MIDEA_DEVICES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(
        CONF_SWITCHES, []
    )
    devs = []
    for entity_key, config in MIDEA_DEVICES[device.device_type]["entities"].items():
        if config["type"] == Platform.LIGHT and (config.get("default") or entity_key in extra_switches):
            devs.append(MideaLight(device, entity_key))
    async_add_entities(devs)


class MideaLight(MideaEntity, LightEntity):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)

    @property
    def is_on(self) -> bool:
        return self.state == STATE_ON

    @property
    def state(self):
        return STATE_ON if self._device.get_attribute(X13Attributes.power) else STATE_OFF

    @property
    def brightness(self) -> int | None:
        return self._device.get_attribute(X13Attributes.brightness)

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        return self._device.get_attribute(X13Attributes.rgb_color)

    @property
    def color_temp(self) -> int | None:
        return self._device.get_attribute(X13Attributes.color_temperature)

    @property
    def effect_list(self) -> list[str] | None:
        return getattr(self._device, "effects")

    @property
    def effect(self) -> str | None:
        return self._device.get_attribute(X13Attributes.effect)

    @property
    def supported_features(self) -> LightEntityFeature:
        supported_features = 0
        if self._device.get_attribute(X13Attributes.brightness):
            supported_features |= SUPPORT_BRIGHTNESS
        if self._device.get_attribute(X13Attributes.color_temperature):
            supported_features |= SUPPORT_COLOR_TEMP
        if self._device.get_attribute(X13Attributes.effect):
            supported_features |= SUPPORT_EFFECT
        if self._device.get_attribute(X13Attributes.rgb_color):
            supported_features |= SUPPORT_COLOR
        return supported_features

    def turn_on(self, **kwargs: Any):
        if not self.is_on:
            self._device.set_attribute(attr=X13Attributes.power, value=True)
        for key in kwargs:
            value = kwargs.get(key)
            if key == ATTR_BRIGHTNESS:
                self._device.set_attribute(attr=X13Attributes.brightness, value=value)
            if key == ATTR_COLOR_TEMP:
                self._device.set_attribute(attr=X13Attributes.color_temperature, value=value)
            if key == ATTR_EFFECT:
                self._device.set_attribute(attr=X13Attributes.effect, value=value)

    def turn_off(self):
        self._device.set_attribute(attr=X13Attributes.power, value=False)

    def update_state(self, status):
        try:
            self.schedule_update_ha_state()
        except Exception as e:
            _LOGGER.debug(f"Entity {self.entity_id} update_state {repr(e)}, status = {status}")
