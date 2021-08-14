from .const import DOMAIN, DEVICES, MANAGERS, CONF_K1, CONF_MAKE_SWITCH
try:
    from homeassistant.core import HomeAssistant
    from homeassistant.const import CONF_DEVICE, CONF_TOKEN
except ImportError:
    class HomeAssistant:
        pass
    CONF_DEVICE = "Device"
    CONF_TOKEN = "Token"

from .state_manager import DeviceManager
from .midea.discover import discover

DEVICE_TYPES = ["climate", "sensor", "switch"]


async def async_setup(hass: HomeAssistant, hass_config: dict):
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry):
    device_id = config_entry.data.get(CONF_DEVICE)
    token = bytearray.fromhex(config_entry.data.get(CONF_TOKEN))
    key = bytearray.fromhex(config_entry.data.get(CONF_K1))
    make_switch = config_entry.data.get(CONF_MAKE_SWITCH)
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    if DEVICES not in hass.data[DOMAIN]:
        hass.data[DOMAIN][DEVICES] = []
    if device_id is not None:
        hass.data[DOMAIN][DEVICES].append(device_id)
    devices = discover()
    device = devices.get(device_id)
    if device is not None:
        dm = DeviceManager(device["id"], device["ip"], device["port"], token, key, device["protocol"], device["model"])
        dm.open(start_thread=True)
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
    device_id = config_entry.data.get(CONF_DEVICE)
    make_switch = config_entry.data.get(CONF_MAKE_SWITCH)
    if device_id is not None:
        hass.data[DOMAIN][DEVICES].remove(device_id)
        dm = hass.data[DOMAIN][MANAGERS].get(device_id)
        if dm is not None:
            dm.close()
        hass.data[DOMAIN][MANAGERS].remove(device_id)
    if make_switch:
        for platform in DEVICE_TYPES:
            await hass.config_entries.async_forward_entry_unload(config_entry, platform)
    else:
        await hass.config_entries.async_forward_entry_unload(config_entry, "climate")
    return True
