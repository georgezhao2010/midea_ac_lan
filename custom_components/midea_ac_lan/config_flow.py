import logging
from .const import DOMAIN, DEVICES, CONF_K1, CONF_MAKE_SWITCH
from homeassistant import config_entries
from homeassistant.const import CONF_DEVICE, CONF_TOKEN
from .midea.discover import discover
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    available_device = []
    devices = {}
    cur_device_id = None

    async def async_step_user(self, user_input=None, error=None):
        if DOMAIN not in self.hass.data:
            self.hass.data[DOMAIN] = {}
        if DEVICES not in self.hass.data[DOMAIN]:
            self.hass.data[DOMAIN][DEVICES] = []
        if user_input is not None:
            self.devices = discover()
            self.available_device = []
            for device_id, device in self.devices.items():
                if device_id not in self.hass.data[DOMAIN][DEVICES]:
                    self.available_device.append(device_id)
            if len(self.available_device) > 0:
                return await self.async_step_devinfo()
        return self.async_show_form(
            step_id="user",
            errors={"base": error} if error else None
        )

    async def async_step_devinfo(self, user_input=None, error=None):
        if user_input is not None:
            device = self.devices.get(user_input[CONF_DEVICE])
            self.cur_device_id = user_input[CONF_DEVICE]
            if device.get("protocol") == 3:
                self.devices[self.cur_device_id][CONF_MAKE_SWITCH] = user_input[CONF_MAKE_SWITCH]
                return await self.async_step_protocol()
            else:
                return self.async_create_entry(
                    title=f"{user_input[CONF_DEVICE]}",
                    data=user_input)
        return self.async_show_form(
            step_id="devinfo",
            data_schema=vol.Schema({
                vol.Required(CONF_DEVICE, default=sorted(self.available_device)[0]):
                    vol.In(self.available_device),
                vol.Required(CONF_MAKE_SWITCH, default=True): bool,
            }),
            errors={"base": error} if error else None
        )

    async def async_step_protocol(self, user_input=None, error=None):
        if user_input is not None:
            device = self.devices.get(self.cur_device_id)
            user_input[CONF_DEVICE] = self.cur_device_id
            user_input[CONF_MAKE_SWITCH] = device[CONF_MAKE_SWITCH]
            return self.async_create_entry(
                title=f"{self.cur_device_id}",
                data=user_input)
        return self.async_show_form(
            step_id="protocol",
            data_schema=vol.Schema({
                vol.Required(CONF_TOKEN): str,
                vol.Required(CONF_K1): str
            }),
            errors={"base": error} if error else None
        )
