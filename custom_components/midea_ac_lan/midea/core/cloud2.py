from aiohttp import ClientSession
from threading import Lock
from .security import Security
import datetime
import json
import logging

_LOGGER = logging.getLogger(__name__)

CLIENT_TYPE = 1         # Android
FORMAT = 2              # JSON
LANGUAGE = "en_US"
APP_ID = "1117"
SRC = "17"


class MideaCloud2:
    def __init__(self, session: ClientSession, username: str, password: str):
        self.session = session
        self.username = username
        self.password = password
        self.server = "https://mapp.appsmb.com"
        self.login_id = None
        self.access_token = ""
        self._api_lock = Lock()
        self.login_session = None
        self.sessionid = None
        self.home_groups = None
        self.security = Security(False)

    async def api_request(self, endpoint, args=None, data=None):
        args = args or {}
        if data is None:
            data = {
                "appId": APP_ID,
                "format": FORMAT,
                "clientType": CLIENT_TYPE,
                "language": LANGUAGE,
                "src": SRC,
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
                    break;
            except Exception as e:
                pass
        if "errorCode" in response and int(response["errorCode"]) == 0 and "result" in response:
            return response["result"]
        return None

    async def get_login_id(self):
        response = await self.api_request(
            "/v1/user/login/id/get",
            {"loginAccount": self.username}
        )
        if response:
            self.login_id = response["loginId"]
            return True
        return False

    async def login(self):
        result = await self.get_login_id()
        if result:
            login_session = await self.api_request(
                "/v1/user/login",
                args={
                    "loginAccount": self.username,
                    "password": self.security.encryptPassword(self.login_id, self.password)
                }
            )
            if login_session:
                self.access_token = login_session["accessToken"]
                self.sessionid = login_session["sessionId"]
                return True
        return False

    async def get_token(self, device_id: int, byte_order_big=False):
        if byte_order_big:
            udpid = Security.get_udpid(device_id.to_bytes(6, "big"))
        else:
            udpid = Security.get_udpid(device_id.to_bytes(6, "little"))
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
