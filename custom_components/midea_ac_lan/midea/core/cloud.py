from aiohttp import ClientSession
from secrets import token_hex, token_urlsafe
from .security import CloudSecurity, MeijuCloudSecurity, SmartLifeSecurity
from threading import Lock
import datetime
import logging
import time
import json

_LOGGER = logging.getLogger(__name__)

CLIENT_TYPE = 1  # Android
FORMAT = 2  # JSON
APP_KEY = "4675636b"


class MideaCloudBase:
    LANGUAGE = "en_US"
    APP_ID = "1010"
    SRC = "1010"
    LOGIN_KEY = None
    IOT_KEY = None

    def __init__(self, session: ClientSession, security, username: str, password: str, server: str = None):
        self.session = session
        self.username = username
        self.password = password
        self.server = None
        self.login_id = None
        self.access_token = ""
        self.key = ""
        self._api_lock = Lock()
        self.login_session = None
        self.security = security
        self.server = server
        self._device_id = CloudSecurity.get_deviceid(username)

    async def api_request(self, endpoint, args=None, data=None):
        args = args or {}
        headers = {}
        if data is None:
            data = {
                "appId": self.APP_ID,
                "format": FORMAT,
                "clientType": CLIENT_TYPE,
                "language": self.LANGUAGE,
                "src": self.SRC,
                "stamp": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
                "deviceId": self._device_id,
            }
        data.update(args)

        if not data.get("reqId"):
            data.update({
                "reqId": token_hex(16),
            })

        url = self.server + endpoint
        random = str(int(time.time()))

        sign = self.security.sign(json.dumps(data), random)
        headers.update({
            "Content-Type": "application/json",
            "secretVersion": "1",
            "sign": sign,
            "random": random,
            "accessToken": self.access_token
        })
        response = {"code": -1}
        for i in range(0, 3):
            try:
                with self._api_lock:
                    r = await self.session.request("POST", url, headers=headers, data=json.dumps(data), timeout=10)
                    raw = await r.read()
                    _LOGGER.debug(f"Endpoint: {endpoint}, Response: {str(raw)}")
                    response = json.loads(raw)
                    break
            except Exception as e:
                _LOGGER.debug(f"Cloud error: {repr(e)}")
        if int(response["code"]) == 0 and "data" in response:
            return response["data"]
        return None

    async def get_login_id(self):
        response = await self.api_request(
            "/v1/user/login/id/get",
            args={"loginAccount": self.username}
        )
        if response:
            self.login_id = response["loginId"]
            return True
        return False

    async def login(self):
        result = await self.get_login_id()
        if result:
            response = await self.api_request(
                "/mj/user/login",
                data={
                    "data": {
                        "appKey": APP_KEY,
                        "platform": FORMAT,
                        "deviceId": self._device_id
                    },
                    "iotData": {
                        "appId": self.APP_ID,
                        "clientType": CLIENT_TYPE,
                        "iampwd": self.security.encrypt_iam_password(self.login_id, self.password),
                        "loginAccount": self.username,
                        "password": self.security.encryptPassword(self.login_id, self.password),
                        "pushToken": token_urlsafe(120),
                        "reqId": token_hex(16),
                        "src": self.SRC,
                        "stamp": datetime.time().strftime("%Y%m%d%H%M%S"),
                    },
                }
            )
            if response:
                self.access_token = response["mdata"]["accessToken"]
                if "key" in response:
                    self.key = CloudSecurity.decrypt_with_key(response["key"])
                return True
        return False

    async def get_token(self, device_id: int, byte_order_big=False):
        if byte_order_big:
            udpid = CloudSecurity.get_udpid(device_id.to_bytes(6, "big"))
        else:
            udpid = CloudSecurity.get_udpid(device_id.to_bytes(6, "little"))
        _LOGGER.debug(f"The udpid of deivce [{device_id}] generated "
                      f"with byte order '{'big' if byte_order_big else 'little'}': {udpid}")
        response = await self.api_request(
            "/v1/iot/secure/getToken",
            args={"udpid": udpid}
        )
        if response and "tokenlist" in response:
            for token in response["tokenlist"]:
                if token["udpId"] == udpid:
                    return token["token"].upper(), token["key"].upper()
        return None, None


class MSmartHomeCloud(MideaCloudBase):
    LOGIN_KEY = "ac21b9f9cbfe4ca5a88562ef25e2b768"
    IOT_KEY = "meicloud"
    SERVER = "https://mp-prod.appsmb.com/mas/v5/app/proxy?alias="

    def __init__(self, session: ClientSession, username: str, password: str):
        super().__init__(session=session,
                         security=CloudSecurity(self.IOT_KEY, self.LOGIN_KEY),
                         username=username,
                         password=password,
                         server=self.SERVER)


class MeijuCloud(MideaCloudBase):
    LANGUAGE = "zh_CN"
    LOGIN_KEY = "ad0ee21d48a64bf49f4fb583ab76e799"
    IOT_KEY = "prod_secret123@muc"
    SERVER = "https://mp-prod.smartmidea.net/mas/v5/app/proxy?alias="

    def __init__(self, session: ClientSession, username: str, password: str):
        super().__init__(session=session,
                         security=MeijuCloudSecurity(self.IOT_KEY, self.LOGIN_KEY),
                         username=username,
                         password=password,
                         server=self.SERVER)


class SmartLifeCloud(MideaCloudBase):
    LANGUAGE = "en_US"
    APP_ID = "1117"
    SRC = "17"
    LOGIN_KEY = "ff0cf6f5f0c3471de36341cab3f7a9af"
    SERVER = "https://mapp.appsmb.com"

    def __init__(self, session: ClientSession, username: str, password: str):
        super().__init__(session=session,
                         security=SmartLifeSecurity(self.IOT_KEY, self.LOGIN_KEY),
                         username=username,
                         password=password,
                         server=self.SERVER)
        self.sessionid = None

    async def api_request(self, endpoint, args=None, data=None):
        args = args or {}
        if data is None:
            data = {
                "appId": self.APP_ID,
                "format": FORMAT,
                "clientType": CLIENT_TYPE,
                "language": self.LANGUAGE,
                "src": self.SRC,
                "stamp": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            }
        data.update(args)
        if self.sessionid is not None:
            data["sessionId"] = self.sessionid

        url = self.server + endpoint
        data["sign"] = self.security.sign(url, data)

        response = {}
        for i in range(0, 3):
            try:
                with self._api_lock:
                    r = await self.session.request("POST", url, data=data, timeout=10)
                    raw = await r.read()
                    _LOGGER.debug(f"Endpoint: {endpoint}, Response: {str(raw)}")
                    response = json.loads(raw)
                    break
            except Exception as e:
                _LOGGER.debug(f"Cloud error: {repr(e)}")
        if "errorCode" in response and int(response["errorCode"]) == 0 and "result" in response:
            return response["result"]
        return None

    async def login(self):
        result = await self.get_login_id()
        if result:
            response = await self.api_request(
                "/v1/user/login",
                args={
                    "loginAccount": self.username,
                    "password": self.security.encryptPassword(self.login_id, self.password)
                }
            )
            if response:
                self.access_token = response["accessToken"]
                self.sessionid = response["sessionId"]
                return True
        return False
