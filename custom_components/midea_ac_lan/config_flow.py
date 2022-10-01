import logging
from .const import (
    DOMAIN,
    EXTRA_SENSOR,
    EXTRA_CONTROL,
    CONF_KEY,
    CONF_MODEL,
    MIDEA_DEFAULT_ACCOUNT,
    MIDEA_DEFAULT_PASSWORD,
    MIDEA_DEFAULT_SERVER
)
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import (
    CONF_NAME,
    CONF_DEVICE,
    CONF_TOKEN,
    CONF_DEVICE_ID,
    CONF_TYPE,
    CONF_IP_ADDRESS,
    CONF_PROTOCOL,
    CONF_PORT,
    CONF_SWITCHES,
    CONF_SENSORS,
    CONF_CUSTOMIZE
)
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from .midea.core.discover import discover
from .midea.core.cloud import MideaCloud
from .midea.core.device import MiedaDevice
from .midea_devices import MIDEA_DEVICES
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

ADD_WAY = {"auto": "Auto", "by_ip": "By IP", "manual": "Manual", "list": "Just list appliances"}
PROTOCOLS = {1: "V1", 2: "V2", 3: "V3"}
DEFAULT_TOKEN = "EE755A84A115703768BCC7C6C13D3D629AA416F1E2FD798BEB9F78CBB1381D09" \
                "1CC245D7B063AAD2A900E5B498FBD936C811F5D504B2E656D4F33B3BBC6D1DA3"
DEFAULT_KEY = "ED37BD31558A4B039AAF4E7A7A59AA7A75FD9101682045F69BAF45D28380AE5C"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    available_device = []
    devices = {}
    found_device = {}
    supports = {}
    for device_type, device_info in MIDEA_DEVICES.items():
        supports[device_type] = device_info["name"]

    def _already_configured(self, device_id, ip_address):
        for entry in self._async_current_entries():
            if device_id == entry.data.get(CONF_DEVICE_ID) or ip_address == entry.data.get(CONF_IP_ADDRESS):
                return True
        return False

    async def async_step_user(self, user_input=None, error=None):
        if user_input is not None:
            if user_input["action"] == "auto":
                return await self.async_step_discover()
            elif user_input["action"] == "manual":
                self.found_device = {}
                return await self.async_step_manual()
            elif user_input["action"] == "by_ip":
                return await self.async_step_byip()
            else:
                return await self.async_step_list()
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
                if not self._already_configured(device_id, device.get(CONF_IP_ADDRESS)):
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

    async def async_step_list(self, user_input=None, error=None):
        all_devices = discover()

        if len(all_devices) > 0:
            table = "Appliance code|Type|IP address|SN|Supported\n:--:|:--:|:--:|:--:|:--:"
            for device_id, device in all_devices.items():
                table += f"\n{device_id}|{'%02X' % device.get(CONF_TYPE)}|{device.get(CONF_IP_ADDRESS)}|" + \
                         f"{device.get('sn')}|{device.get(CONF_TYPE) in self.supports.keys()}"
        else:
            table = "Not found"
        return self.async_show_form(
            step_id="list",
            description_placeholders={"table": table},
            errors={"base": error} if error else None
        )

    async def async_step_byip(self, user_input=None, error=None):
        if user_input is not None:
            self.devices = discover(self.supports.keys(), ip_address=user_input[CONF_IP_ADDRESS])
            self.available_device = {}
            for device_id, device in self.devices.items():
                if not self._already_configured(device_id, device.get(CONF_IP_ADDRESS)):
                    self.available_device[device_id] = \
                        f"{device_id} ({self.supports.get(device.get(CONF_TYPE))})"
            if len(self.available_device) > 0:
                return await self.async_step_auto()
            else:
                return await self.async_step_byip(error="no_devices")
        return self.async_show_form(
            step_id="byip",
            data_schema=vol.Schema({
                vol.Required(CONF_IP_ADDRESS): str
            }),
            errors={"base": error} if error else None
        )

    async def async_step_auto(self, user_input=None, error=None):
        if user_input is not None:
            device_id = user_input[CONF_DEVICE]
            device = self.devices.get(device_id)
            if device.get(CONF_PROTOCOL) == 3:
                session = async_create_clientsession(self.hass)
                cloud = MideaCloud(session, MIDEA_DEFAULT_ACCOUNT, MIDEA_DEFAULT_PASSWORD, MIDEA_DEFAULT_SERVER)
                dm = MiedaDevice(
                    name="",
                    device_id=device_id,
                    device_type=device.get(CONF_TYPE),
                    ip_address=device.get(CONF_IP_ADDRESS),
                    port=device.get(CONF_PORT),
                    token=DEFAULT_TOKEN,
                    key=DEFAULT_KEY,
                    protocol=3,
                    model=device.get(CONF_MODEL)
                )
                if dm.connect(refresh_status=False):
                    self.found_device = {
                        CONF_DEVICE_ID: device_id,
                        CONF_TYPE: device.get(CONF_TYPE),
                        CONF_PROTOCOL: 3,
                        CONF_IP_ADDRESS: device.get(CONF_IP_ADDRESS),
                        CONF_PORT: device.get(CONF_PORT),
                        CONF_MODEL: device.get(CONF_MODEL),
                        CONF_TOKEN: DEFAULT_TOKEN,
                        CONF_KEY: DEFAULT_KEY,
                    }
                    dm.close_socket()
                    return await self.async_step_manual()
                elif await cloud.login():
                    for byte_order_big in [False, True]:
                        token, key = await cloud.get_token(user_input[CONF_DEVICE], byte_order_big=byte_order_big)
                        if token and key:
                            dm = MiedaDevice(
                                name="",
                                device_id=device_id,
                                device_type=device.get(CONF_TYPE),
                                ip_address=device.get(CONF_IP_ADDRESS),
                                port=device.get(CONF_PORT),
                                token=token,
                                key=key,
                                protocol=3,
                                model=device.get(CONF_MODEL)
                            )
                            _LOGGER.debug(f"Successful to take token and key, token: {token}, key: {key}, "
                                          f"byte_order_big: {byte_order_big}")
                            if dm.connect(refresh_status=False):
                                self.found_device = {
                                    CONF_DEVICE_ID: device_id,
                                    CONF_TYPE: device.get(CONF_TYPE),
                                    CONF_PROTOCOL: 3,
                                    CONF_IP_ADDRESS: device.get(CONF_IP_ADDRESS),
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
                    CONF_IP_ADDRESS: device.get(CONF_IP_ADDRESS),
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
                CONF_IP_ADDRESS: user_input[CONF_IP_ADDRESS],
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
                name="",
                device_id=user_input[CONF_DEVICE_ID],
                device_type=user_input[CONF_TYPE],
                ip_address=user_input[CONF_IP_ADDRESS],
                port=user_input[CONF_PORT],
                token=user_input[CONF_TOKEN],
                key=user_input[CONF_KEY],
                protocol=user_input[CONF_PROTOCOL],
                model=user_input[CONF_MODEL])
            if dm.connect(refresh_status=False):
                dm.close_socket()
                return self.async_create_entry(
                    title=f"{user_input[CONF_NAME]}",
                    data={
                        CONF_NAME: user_input[CONF_NAME],
                        CONF_DEVICE_ID: user_input[CONF_DEVICE_ID],
                        CONF_TYPE: user_input[CONF_TYPE],
                        CONF_PROTOCOL: user_input[CONF_PROTOCOL],
                        CONF_IP_ADDRESS: user_input[CONF_IP_ADDRESS],
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
                    CONF_NAME,
                    default=self.supports.get(self.found_device.get(CONF_TYPE))
                ): str,
                vol.Required(
                    CONF_DEVICE_ID,
                    default=self.found_device.get(CONF_DEVICE_ID)
                ): int,
                vol.Required(
                    CONF_TYPE,
                    default=self.found_device.get(CONF_TYPE) if self.found_device.get(CONF_TYPE) else 0xac
                ): vol.In(self.supports),
                vol.Required(
                    CONF_IP_ADDRESS,
                    default=self.found_device.get(CONF_IP_ADDRESS)
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
        self._device_type = config_entry.data.get(CONF_TYPE)
        if self._device_type is None:
            self._device_type = 0xac
        if CONF_SENSORS in self.config_entry.options:
            for key in self.config_entry.options[CONF_SENSORS]:
                if key not in MIDEA_DEVICES[self._device_type]["entities"]:
                    self.config_entry.options[CONF_SENSORS].remove(key)
        if CONF_SWITCHES in self.config_entry.options:
            for key in self.config_entry.options[CONF_SWITCHES]:
                if key not in MIDEA_DEVICES[self._device_type]["entities"]:
                    self.config_entry.options[CONF_SWITCHES].remove(key)

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        sensors = {}
        switches = {}
        for attribute, attribute_config in MIDEA_DEVICES.get(self._device_type).get("entities").items():
            attribute_name = attribute if type(attribute) is str else attribute.value
            if attribute_config.get("type") in EXTRA_SENSOR:
                sensors[attribute_name] = attribute_config.get("name")
            elif attribute_config.get("type") in EXTRA_CONTROL and not attribute_config.get("default"):
                switches[attribute_name] = attribute_config.get("name")
        extra_sensors = self.config_entry.options.get(
            CONF_SENSORS, []
        )
        extra_switches = self.config_entry.options.get(
            CONF_SWITCHES, []
        )
        customize = self.config_entry.options.get(
            CONF_CUSTOMIZE, ""
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
                vol.Optional(
                    CONF_CUSTOMIZE,
                    default=customize,
                ): str
            })
        )
