import logging
from .const import (
    DOMAIN,
    CONF_KEY,
    CONF_MODEL,
    MIDEA_DEFAULT_ACCOUNT,
    MIDEA_DEFAULT_PASSWORD,
    MIDEA_DEFAULT_SERVER
)
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import (
    CONF_DEVICE,
    CONF_TOKEN,
    CONF_DEVICE_ID,
    CONF_TYPE,
    CONF_HOST,
    CONF_PROTOCOL,
    CONF_PORT,
    CONF_SWITCHES,
    CONF_SENSORS,
)
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from .midea.core.discover import discover
from .midea.core.cloud import MideaCloud
from .midea.core.device import MiedaDevice
from .midea_devices import MIDEA_DEVICES
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

ADD_WAY = {"auto": "Auto", "manual": "Manual"}
PROTOCOLS = {2: "V2", 3: "V3"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    available_device = []
    devices = {}
    found_device = {}
    supports = {}
    for device_type, device_info in MIDEA_DEVICES.items():
        supports[device_type] = device_info["name"]

    def _already_configured(self, device_id):
        for entry in self._async_current_entries():
            _LOGGER.debug(entry.data)
            if device_id == entry.data.get(CONF_DEVICE_ID):
                return True
        return False

    async def async_step_user(self, user_input=None, error=None):
        if user_input is not None:
            if user_input["action"] == "auto":
                return await self.async_step_discover()
            else:
                self.found_device = {}
                return await self.async_step_manual()
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("action", default="auto"): vol.In(ADD_WAY)
            }),
            errors={"base": error} if error else None
        )

    async def async_step_discover(self, user_input=None, error=None):
        if user_input is not None:
            self.devices = discover(self.supports.keys())
            self.available_device = {}
            for device_id, device in self.devices.items():
                if not self._already_configured(device_id):
                    self.available_device[device_id] = \
                        f"{device_id} ({self.supports.get(device.get(CONF_TYPE))})"
            if len(self.available_device) > 0:
                return await self.async_step_auto()
            else:
                return await self.async_step_user(error="no_devices")
        return self.async_show_form(
            step_id="discover",
            errors={"base": error} if error else None
        )

    async def async_step_auto(self, user_input=None, error=None):
        if user_input is not None:
            device_id = user_input[CONF_DEVICE]
            device = self.devices.get(device_id)
            if device.get(CONF_PROTOCOL) == 3:
                session = async_create_clientsession(self.hass)
                cloud = MideaCloud(session, MIDEA_DEFAULT_ACCOUNT, MIDEA_DEFAULT_PASSWORD, MIDEA_DEFAULT_SERVER)
                if await cloud.login():
                    for byte_order_big in [False, True]:
                        token, key = await cloud.get_token(user_input[CONF_DEVICE], byte_order_big=byte_order_big)
                        if token and key:
                            dm = MiedaDevice(
                                device_id=device_id,
                                device_type=device.get(CONF_TYPE),
                                host=device.get(CONF_HOST),
                                port=device.get(CONF_PORT),
                                token=token,
                                key=key,
                                protocol=3,
                                model=device.get(CONF_MODEL))
                            _LOGGER.debug(f"Successful to take token and key, token: {token}, key: {key}, "
                                          f"byte_order_big: {byte_order_big}")
                            if dm.connect(refresh_status=False):
                                self.found_device = {
                                    CONF_DEVICE_ID: device_id,
                                    CONF_TYPE: device.get(CONF_TYPE),
                                    CONF_PROTOCOL: 3,
                                    CONF_HOST: device.get(CONF_HOST),
                                    CONF_PORT: device.get(CONF_PORT),
                                    CONF_MODEL: device.get(CONF_MODEL),
                                    CONF_TOKEN: token,
                                    CONF_KEY: key,
                                }
                                dm.close_socket()
                                return await self.async_step_manual()
                    return await self.async_step_auto(error="connect_error")
                return await self.async_step_auto(error="cant_get_token")
            else:
                self.found_device = {
                    CONF_DEVICE_ID: device_id,
                    CONF_TYPE: device.get(CONF_TYPE),
                    CONF_PROTOCOL: 2,
                    CONF_HOST: device.get(CONF_HOST),
                    CONF_PORT: device.get(CONF_PORT),
                    CONF_MODEL: device.get(CONF_MODEL),
                }
                return await self.async_step_manual()
        return self.async_show_form(
            step_id="auto",
            data_schema=vol.Schema({
                vol.Required(CONF_DEVICE, default=sorted(self.available_device)[0]):
                    vol.In(self.available_device),
            }),
            errors={"base": error} if error else None
        )

    async def async_step_manual(self, user_input=None, error=None):
        if user_input is not None:
            self.found_device = {
                CONF_DEVICE_ID: user_input[CONF_DEVICE_ID],
                CONF_TYPE: user_input[CONF_TYPE],
                CONF_PROTOCOL: user_input[CONF_PROTOCOL],
                CONF_HOST: user_input[CONF_HOST],
                CONF_PORT: user_input[CONF_PORT],
                CONF_MODEL: user_input[CONF_MODEL],
                CONF_TOKEN: user_input[CONF_TOKEN],
                CONF_KEY: user_input[CONF_KEY],
            }
            try:
                bytearray.fromhex(user_input[CONF_TOKEN])
                bytearray.fromhex(user_input[CONF_KEY])
            except ValueError:
                return await self.async_step_manual(error="invalid_token")
            if user_input[CONF_PROTOCOL] == 3 and (len(user_input[CONF_TOKEN]) == 0 or len(user_input[CONF_KEY]) == 0):
                return await self.async_step_manual(error="invalid_token")
            dm = MiedaDevice(
                device_id=user_input[CONF_DEVICE_ID],
                device_type=user_input[CONF_TYPE],
                host=user_input[CONF_HOST],
                port=user_input[CONF_PORT],
                token=user_input[CONF_TOKEN],
                key=user_input[CONF_KEY],
                protocol=user_input[CONF_PROTOCOL],
                model=user_input[CONF_MODEL])
            if dm.connect(refresh_status=False):
                dm.close_socket()
                return self.async_create_entry(
                    title=f"{user_input[CONF_DEVICE_ID]}",
                    data={
                        CONF_DEVICE_ID: user_input[CONF_DEVICE_ID],
                        CONF_TYPE: user_input[CONF_TYPE],
                        CONF_PROTOCOL: user_input[CONF_PROTOCOL],
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_PORT: user_input[CONF_PORT],
                        CONF_MODEL: user_input[CONF_MODEL],
                        CONF_TOKEN: user_input[CONF_TOKEN],
                        CONF_KEY: user_input[CONF_KEY],
                    })
            else:
                return await self.async_step_manual(error="config_incorrect")
        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_DEVICE_ID,
                    default=self.found_device.get(CONF_DEVICE_ID)
                ): int,
                vol.Required(
                    CONF_TYPE,
                    default=self.found_device.get(CONF_TYPE) if self.found_device.get(CONF_TYPE) else 0xac
                ): vol.In(self.supports),
                vol.Required(
                    CONF_HOST,
                    default=self.found_device.get(CONF_HOST)
                ): str,
                vol.Required(
                    CONF_PORT,
                    default=self.found_device.get(CONF_PORT) if self.found_device.get(CONF_PORT) else 6444
                ): int,
                vol.Required(
                    CONF_PROTOCOL,
                    default=self.found_device.get(CONF_PROTOCOL) if self.found_device.get(CONF_PROTOCOL) else 3
                ): vol.In(PROTOCOLS),
                vol.Required(
                    CONF_MODEL,
                    default=self.found_device.get(CONF_MODEL) if self.found_device.get(CONF_MODEL) else "Unknown"
                ): str,
                vol.Optional(
                    CONF_TOKEN,
                    default=self.found_device.get(CONF_TOKEN) if self.found_device.get(CONF_TOKEN) else ""
                ): str,
                vol.Optional(
                    CONF_KEY,
                    default=self.found_device.get(CONF_KEY) if self.found_device.get(CONF_KEY) else ""
                ): str,
            }),
            errors={"base": error} if error else None
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        device_type = self.config_entry.data.get(CONF_TYPE)
        if device_type is None:
            device_type = 0xac
        sensors = {}
        switches = {}
        for attribute, attribute_config in MIDEA_DEVICES.get(device_type).get("entities").items():
            if attribute_config.get("type") == "sensor":
                sensors[attribute] = attribute_config.get("name")
            elif attribute_config.get("type") == "switch":
                switches[attribute] = attribute_config.get("name")
        extra_sensors = self.config_entry.options.get(
            CONF_SENSORS, []
        )
        extra_switches = self.config_entry.options.get(
            CONF_SWITCHES, []
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_SENSORS,
                    default=extra_sensors,
                ): cv.multi_select(sensors),
                vol.Required(
                    CONF_SWITCHES,
                    default=extra_switches,
                ): cv.multi_select(switches),
            })
        )
