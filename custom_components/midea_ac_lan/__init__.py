import logging
from .const import DOMAIN, MANAGERS, DEVICES, CONF_KEY, CONF_MAKE_SWITCH, CONF_MODEL
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_DEVICE_ID, CONF_TOKEN, CONF_HOST, CONF_PORT, CONF_PROTOCOL
from .state_manager import DeviceManager
from .midea.discover import discover

DEVICE_TYPES = ["climate", "sensor", "switch"]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, hass_config: dict):
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    token = config_entry.data.get(CONF_TOKEN)
    key = config_entry.data.get(CONF_KEY)
    make_switch = config_entry.data.get(CONF_MAKE_SWITCH)
    host = config_entry.data.get(CONF_HOST)
    port = config_entry.data.get(CONF_PORT)
    model = config_entry.data.get(CONF_MODEL)
    protocol = config_entry.data.get(CONF_PROTOCOL)
    if protocol == 3 and (key is None or key is None):
        _LOGGER.error("For V3 devices, the key and the token is required.")
        return False
    dm = DeviceManager(device_id, host, port, token, key, protocol, model)
    dm.open(start_thread=True)
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    if MANAGERS not in hass.data[DOMAIN]:
        hass.data[DOMAIN][MANAGERS] = {}
    hass.data[DOMAIN][MANAGERS][device_id] = dm
    if make_switch:
        for platform in DEVICE_TYPES:
            hass.async_create_task(hass.config_entries.async_forward_entry_setup(
                config_entry, platform))
    else:
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(
            config_entry, "climate"))

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    make_switch = config_entry.data.get(CONF_MAKE_SWITCH)
    if device_id is not None:
        dm = hass.data[DOMAIN][MANAGERS].get(device_id)
        if dm is not None:
            dm.close()
        hass.data[DOMAIN][MANAGERS].pop(device_id)
        hass.data[DOMAIN][DEVICES].pop(device_id)
    if make_switch:
        for platform in DEVICE_TYPES:
            await hass.config_entries.async_forward_entry_unload(config_entry, platform)
    else:
        await hass.config_entries.async_forward_entry_unload(config_entry, "climate")
    return True
