import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from .const import (
    DOMAIN,
    CONF_KEY,
    CONF_MODEL,
    DEVICES,
)
from homeassistant.core import HomeAssistant
from homeassistant.const import (
    CONF_TOKEN,
    CONF_HOST,
    CONF_PORT,
    CONF_PROTOCOL,
    CONF_DEVICE_ID,
    CONF_TYPE,
    TEMP_FAHRENHEIT,
    ATTR_DEVICE_ID,
    ATTR_ENTITY_ID
)
from .midea.devices.ac.device import MideaACDevice

_LOGGER = logging.getLogger(__name__)

SERVICE_ATTRIBUTES = [
    "aux_heat",
    "breezyless",
    "comfort_mode",
    "dry",
    "eco_mode",
    "indirect_wind",
    "natural_wind",
    "night_light",
    "prompt_tone",
    "screen_display",
    "smart_eye",
    "swing_horizontal",
    "swing_vertical",
    "turbo_mode",
]

SERVICES_SCHEMA = {
    "set_fan_speed": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required("fan_speed"): vol.Any(vol.All(vol.Coerce(int), vol.Range(min=1, max=100)),
                                           vol.All(str, vol.In(["auto"])))
    }),
    "set_attribute": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required("attribute"): vol.In(SERVICE_ATTRIBUTES),
        vol.Required("value"): cv.boolean
    })
}


async def update_listener(hass, config_entry):
    for platform in ["sensor", "switch"]:
        await hass.config_entries.async_forward_entry_unload(config_entry, platform)
    for platform in ["sensor", "switch"]:
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(
            config_entry, platform))


async def async_setup(hass: HomeAssistant, hass_config: dict):
    hass.data.setdefault(DOMAIN, {})

    def service_set_fan_speed(service):
        entity_ids = service.data.get(ATTR_ENTITY_ID)
        fan_speed = service.data.get("fan_speed")
        if fan_speed == 'auto':
            fan_speed = 102
        devices = []
        if entity_ids:
            devices = [
                dev
                for dev in hass.data[DOMAIN][DEVICES].values()
                if dev.entity.entity_id in entity_ids
            ]
        for dev in devices:
            setattr(dev, "fan_speed", fan_speed)

    def service_set_attribute(service):
        entity_ids = service.data.get(ATTR_ENTITY_ID)
        attribute = service.data.get("attribute")
        value = service.data.get("value")
        if attribute in SERVICE_ATTRIBUTES:
            devices = []
            if entity_ids:
                devices = [
                    dev
                    for dev in hass.data[DOMAIN][DEVICES].values()
                    if dev.entity.entity_id in entity_ids
                ]
            for dev in devices:
                if hasattr(dev, attribute):
                    setattr(dev, attribute, value)

    hass.services.async_register(
        DOMAIN,
        "set_fan_speed",
        service_set_fan_speed,
        schema=SERVICES_SCHEMA["set_fan_speed"]
    )
    hass.services.async_register(
        DOMAIN,
        "set_attribute",
        service_set_attribute,
        schema=SERVICES_SCHEMA["set_attribute"]
    )
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device_type = config_entry.data.get(CONF_TYPE)
    if device_type is None:
        device_type = 0xac
    token = config_entry.data.get(CONF_TOKEN)
    key = config_entry.data.get(CONF_KEY)
    host = config_entry.data.get(CONF_HOST)
    port = config_entry.data.get(CONF_PORT)
    model = config_entry.data.get(CONF_MODEL)
    protocol = config_entry.data.get(CONF_PROTOCOL)
    _LOGGER.debug("Starting set up")
    if protocol == 3 and (key is None or key is None):
        _LOGGER.error("For V3 devices, the key and the token is required.")
        return False
    device = None
    if device_type == 0xac:
        device = MideaACDevice(
            device_id=device_id,
            device_type=device_type,
            host=host,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            temp_fahrenheit=hass.config.units.temperature_unit == TEMP_FAHRENHEIT
        )
    elif device_type == 0xcc:
        pass
    if device:
        device.open()
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}
        if DEVICES not in hass.data[DOMAIN]:
            hass.data[DOMAIN][DEVICES] = {}
        hass.data[DOMAIN][DEVICES][device_id] = device
        for platform in ["sensor", "switch", "climate"]:
            hass.async_create_task(hass.config_entries.async_forward_entry_setup(
                config_entry, platform))
        config_entry.add_update_listener(update_listener)
        return True
    return False


async def async_unload_entry(hass: HomeAssistant, config_entry):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    if device_id is not None:
        dm = hass.data[DOMAIN][DEVICES].get(device_id)
        if dm is not None:
            dm.close()
        hass.data[DOMAIN][DEVICES].pop(device_id)
    for platform in ["sensor", "switch", "climate"]:
        await hass.config_entries.async_forward_entry_unload(config_entry, platform)
    return True
