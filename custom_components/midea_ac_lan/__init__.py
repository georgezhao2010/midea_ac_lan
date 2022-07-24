import logging
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
)
from .midea.devices.ac.device import MideaACDevice

_LOGGER = logging.getLogger(__name__)


async def update_listener(hass, config_entry):
    for platform in ["sensor", "switch"]:
        await hass.config_entries.async_forward_entry_unload(config_entry, platform)
    for platform in ["sensor", "switch"]:
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(
            config_entry, platform))


async def async_setup(hass: HomeAssistant, hass_config: dict):
    hass.data.setdefault(DOMAIN, {})
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
    del hass.data[config_entry.entry_id]
    for platform in ["sensor", "switch", "climate"]:
        await hass.config_entries.async_forward_entry_unload(config_entry, platform)
    return True
