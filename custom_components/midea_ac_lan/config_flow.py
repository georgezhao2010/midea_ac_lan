import voluptuous as vol
import os
try:
    from homeassistant.helpers.json import save_json
except ImportError:
    from homeassistant.util.json import save_json
import logging
from .const import (
    DOMAIN,
    EXTRA_SENSOR,
    EXTRA_CONTROL,
    CONF_ACCOUNT,
    CONF_SERVER,
    CONF_KEY,
    CONF_MODEL,
    CONF_REFRESH_INTERVAL
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
    CONF_CUSTOMIZE,
    CONF_PASSWORD,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from .midea.core.discover import discover
from .midea.core.cloud import get_midea_cloud
from .midea.core.device import MiedaDevice
from .midea_devices import MIDEA_DEVICES

_LOGGER = logging.getLogger(__name__)

ADD_WAY = {"discovery": "Discovery automatically", "manually": "Configure manually", "list": "List all appliances only"}
PROTOCOLS = {1: "V1", 2: "V2", 3: "V3"}
STORAGE_PATH = f".storage/{DOMAIN}"

servers = {
    1: "MSmartHome",
    2: "美的美居",
}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    _account = None
    _password = None
    _server = None
    available_device = []
    devices = {}
    found_device = {}
    supports = {}
    unsorted = {}
    for device_type, device_info in MIDEA_DEVICES.items():
        unsorted[device_type] = device_info["name"]

    unsorted = sorted(unsorted.items(), key=lambda x: x[1])
    for item in unsorted:
        supports[item[0]] = item[1]

    def _save_device_token(self, device_id, protocol, token, key):
        os.makedirs(self.hass.config.path(STORAGE_PATH), exist_ok=True)
        record_file = self.hass.config.path(f"{STORAGE_PATH}/{device_id}.json")
        json_data = {"protocol": f"v{protocol}", "token": token, "key": key}
        save_json(record_file, json_data)

    def _get_configured_account(self):
        for entry in self._async_current_entries():
            if entry.data.get(CONF_TYPE) == CONF_ACCOUNT:
                password = bytes.fromhex(format((
                        int(entry.data.get(CONF_PASSWORD), 16) ^
                        int(entry.data.get(CONF_ACCOUNT).encode("utf-8").hex(), 16)
                ), 'X')).decode('UTF-8')
                return entry.data.get(CONF_ACCOUNT), password, servers[entry.data.get(CONF_SERVER)]
        return None, None, None

    def _already_configured(self, device_id, ip_address):
        for entry in self._async_current_entries():
            if device_id == entry.data.get(CONF_DEVICE_ID) or ip_address == entry.data.get(CONF_IP_ADDRESS):
                return True
        return False

    async def async_step_user(self, user_input=None, error=None):
        if user_input is not None:
            if user_input["action"] == "discovery":
                return await self.async_step_discovery()
            elif user_input["action"] == "manually":
                self.found_device = {}
                return await self.async_step_manually()
            else:
                return await self.async_step_list()
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("action", default="discovery"): vol.In(ADD_WAY)
            }),
            errors={"base": error} if error else None
        )

    async def async_step_login(self, user_input=None, error=None):
        if user_input is not None:
            session = async_create_clientsession(self.hass)
            cloud = get_midea_cloud(
                session=session,
                cloud_name=servers[user_input[CONF_SERVER]],
                account=user_input[CONF_ACCOUNT],
                password=user_input[CONF_PASSWORD]
            )
            _LOGGER.debug(
                f"account = {user_input[CONF_ACCOUNT]}, password = {user_input[CONF_PASSWORD]}, server = {servers[user_input[CONF_SERVER]]}")
            if await cloud.login():
                password = format((int(user_input[CONF_ACCOUNT].encode("utf-8").hex(), 16) ^
                                   int(user_input[CONF_PASSWORD].encode("utf-8").hex(), 16)), 'x')
                return self.async_create_entry(
                    title=f"{user_input[CONF_ACCOUNT]}",
                    data={
                        CONF_TYPE: CONF_ACCOUNT,
                        CONF_ACCOUNT: user_input[CONF_ACCOUNT],
                        CONF_PASSWORD: password,
                        CONF_SERVER: user_input[CONF_SERVER]
                    })
            else:
                return await self.async_step_login(error="login_failed")
        return self.async_show_form(
            step_id="login",
            data_schema=vol.Schema({
                vol.Required(CONF_ACCOUNT): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_SERVER, default=1): vol.In(servers)
            }),
            errors={"base": error} if error else None
        )

    async def async_step_list(self, user_input=None, error=None):
        all_devices = discover()
        if len(all_devices) > 0:
            table = "Appliance code|Type|IP address|SN|Supported\n:--:|:--:|:--:|:--:|:--:"
            for device_id, device in all_devices.items():
                supported = device.get(CONF_TYPE) in self.supports.keys()
                table += f"\n{device_id}|{'%02X' % device.get(CONF_TYPE)}|{device.get(CONF_IP_ADDRESS)}|" \
                         f"{device.get('sn')}|" \
                         f"{'<font color=gree>YES</font>' if supported else '<font color=red>NO</font>'}"
        else:
            table = "Not found"
        return self.async_show_form(
            step_id="list",
            description_placeholders={"table": table},
            errors={"base": error} if error else None
        )

    async def async_step_discovery(self, user_input=None, error=None):
        self._account, self._password, self._server = self._get_configured_account()
        if self._account is None:
            return await self.async_step_login()
        if user_input is not None:
            if user_input[CONF_IP_ADDRESS].lower() == "auto":
                ip_address = None
            else:
                ip_address = user_input[CONF_IP_ADDRESS]
            self.devices = discover(self.supports.keys(), ip_address=ip_address)
            self.available_device = {}
            for device_id, device in self.devices.items():
                if not self._already_configured(device_id, device.get(CONF_IP_ADDRESS)):
                    self.available_device[device_id] = \
                        f"{device_id} ({self.supports.get(device.get(CONF_TYPE))})"
            if len(self.available_device) > 0:
                return await self.async_step_auto()
            else:
                return await self.async_step_discovery(error="no_devices")
        return self.async_show_form(
            step_id="discovery",
            data_schema=vol.Schema({
                vol.Required(CONF_IP_ADDRESS, default="auto"): str
            }),
            errors={"base": error} if error else None
        )

    async def async_step_auto(self, user_input=None, error=None):
        if user_input is not None:
            device_id = user_input[CONF_DEVICE]
            device = self.devices.get(device_id)
            if device.get(CONF_PROTOCOL) == 3:
                session = async_create_clientsession(self.hass)
                cloud = get_midea_cloud(self._server, session, self._account, self._password)
                if await cloud.login():
                    keys = await cloud.get_keys(user_input[CONF_DEVICE])
                    for method, key in keys.items():
                        dm = MiedaDevice(
                            name="",
                            device_id=device_id,
                            device_type=device.get(CONF_TYPE),
                            ip_address=device.get(CONF_IP_ADDRESS),
                            port=device.get(CONF_PORT),
                            token=key["token"],
                            key=key["key"],
                            protocol=3,
                            model=device.get(CONF_MODEL),
                            attributes={}
                        )
                        _LOGGER.debug(f"Successful to take token and key, token: {key['token']},"
                                      f" key: {key['key']}, method: {method}")
                        if dm.connect(refresh_status=False):
                            self.found_device = {
                                CONF_DEVICE_ID: device_id,
                                CONF_TYPE: device.get(CONF_TYPE),
                                CONF_PROTOCOL: 3,
                                CONF_IP_ADDRESS: device.get(CONF_IP_ADDRESS),
                                CONF_PORT: device.get(CONF_PORT),
                                CONF_MODEL: device.get(CONF_MODEL),
                                CONF_TOKEN: key["token"],
                                CONF_KEY: key["key"],
                            }
                            dm.close_socket()
                            return await self.async_step_manually()
                    return await self.async_step_auto(error="connect_error")
                return await self.async_step_auto(error="login_failed")
            else:
                self.found_device = {
                    CONF_DEVICE_ID: device_id,
                    CONF_TYPE: device.get(CONF_TYPE),
                    CONF_PROTOCOL: 2,
                    CONF_IP_ADDRESS: device.get(CONF_IP_ADDRESS),
                    CONF_PORT: device.get(CONF_PORT),
                    CONF_MODEL: device.get(CONF_MODEL),
                }
                return await self.async_step_manually()
        return self.async_show_form(
            step_id="auto",
            data_schema=vol.Schema({
                vol.Required(CONF_DEVICE, default=list(self.available_device.keys())[0]):
                    vol.In(self.available_device),
            }),
            errors={"base": error} if error else None
        )

    async def async_step_manually(self, user_input=None, error=None):
        if user_input is not None:
            self.found_device = {
                CONF_DEVICE_ID: user_input[CONF_DEVICE_ID],
                CONF_TYPE: user_input[CONF_TYPE],
                CONF_PROTOCOL: user_input[CONF_PROTOCOL],
                CONF_IP_ADDRESS: user_input[CONF_IP_ADDRESS],
                CONF_PORT: user_input[CONF_PORT],
                CONF_MODEL: user_input[CONF_MODEL],
                CONF_TOKEN: user_input[CONF_TOKEN],
                CONF_KEY: user_input[CONF_KEY]
            }
            try:
                bytearray.fromhex(user_input[CONF_TOKEN])
                bytearray.fromhex(user_input[CONF_KEY])
            except ValueError:
                return await self.async_step_manually(error="invalid_token")
            if user_input[CONF_PROTOCOL] == 3 and (len(user_input[CONF_TOKEN]) == 0 or len(user_input[CONF_KEY]) == 0):
                return await self.async_step_manually(error="invalid_token")
            dm = MiedaDevice(
                name="",
                device_id=user_input[CONF_DEVICE_ID],
                device_type=user_input[CONF_TYPE],
                ip_address=user_input[CONF_IP_ADDRESS],
                port=user_input[CONF_PORT],
                token=user_input[CONF_TOKEN],
                key=user_input[CONF_KEY],
                protocol=user_input[CONF_PROTOCOL],
                model=user_input[CONF_MODEL],
                attributes={}
            )
            if dm.connect(refresh_status=False):
                dm.close_socket()
                self._save_device_token(
                    user_input[CONF_DEVICE_ID],
                    user_input[CONF_PROTOCOL],
                    user_input[CONF_TOKEN],
                    user_input[CONF_KEY]
                )
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
                return await self.async_step_manually(error="config_incorrect")
        return self.async_show_form(
            step_id="manually",
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
        ip_address = self.config_entry.options.get(
            CONF_IP_ADDRESS, None
        )
        if ip_address is None:
            ip_address = self.config_entry.data.get(
                CONF_IP_ADDRESS, None
            )
        refresh_interval = self.config_entry.options.get(
            CONF_REFRESH_INTERVAL, 30
        )
        extra_sensors = self.config_entry.options.get(
            CONF_SENSORS, []
        )
        extra_switches = self.config_entry.options.get(
            CONF_SWITCHES, []
        )
        customize = self.config_entry.options.get(
            CONF_CUSTOMIZE, ""
        )
        data_schema = vol.Schema({
            vol.Required(
                CONF_IP_ADDRESS,
                default=ip_address
            ): str,
            vol.Required(
                CONF_REFRESH_INTERVAL,
                default=refresh_interval
            ): int
        })
        if len(sensors) > 0:
            data_schema = data_schema.extend({
                vol.Required(
                    CONF_SENSORS,
                    default=extra_sensors,
                ):
                    cv.multi_select(sensors)
            })
        if len(switches) > 0:
            data_schema = data_schema.extend({
                vol.Required(
                    CONF_SWITCHES,
                    default=extra_switches,
                ):
                    cv.multi_select(switches)
            })
        data_schema = data_schema.extend({
            vol.Optional(
                CONF_CUSTOMIZE,
                default=customize,
            ):
                str
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema
        )
