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
from homeassistant.components.climate.const import FAN_AUTO
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


DEVICE_TYPES = ["climate", "sensor", "switch"]

_LOGGER = logging.getLogger(__name__)
'''
SERVICES = {
    "set_fan_speed": {
        "method": "set_fan_speed",
        "schema": vol.Schema({
            vol.Required(ATTR_DEVICE_ID): cv.device_id,
            vol.Required("attribute"): vol.Any(vol.All(vol.Coerce(int), vol.Range(min=1, max=100)),
                                               vol.All(str, vol.In([FAN_AUTO])))
        })
    },
    "set_eco_mode": {
        "method": "set_eco_mode",
        "schema": vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_id,
            vol.Required("eco_mode"): cv.boolean
        })
    },
    "set_comfort_mode": {
        "method": "set_comfort_mode",
        "schema": vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_id,
            vol.Required("comfort_mode"): cv.boolean
        })
    },
    "set_prompt_tone": {
        "method": "set_prompt_tone",
        "schema": vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_id,
            vol.Required("prompt_tone"): cv.boolean
        })
    },
    "set_indirect_wind": {
        "method": "set_indirect_wind",
        "schema": vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_id,
            vol.Required("indirect_wind"): cv.boolean
        })
    },
}
'''


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
    '''
    def service_handler(service):
        service_call_data = SERVICES.get(service.service)
        params = {
            key: value for key, value in service.data.items() if key != ATTR_ENTITY_ID
        }
        entity_ids = service.data.get(ATTR_ENTITY_ID)
        devices = []
        if entity_ids:
            devices = [
                dev
                for dev in hass.data[DOMAIN][DEVICES].values()
                if dev.entity_id and dev.entity_id in entity_ids
            ]

        for dev in devices:
            _LOGGER.debug(f"The service {service_call_data['method']}({params}) called")
            # if dev and hasattr(dev, service_call_data["method"]):
            #     getattr(dev, service_call_data["method"])(**params)

    for service_name, service_data in SERVICES.items():
        schema = service_data.get("schema")
        hass.services.async_register(
            DOMAIN,
            service_name,
            service_handler,
            schema=schema
        )
    '''
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
