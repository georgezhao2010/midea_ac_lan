from aiohttp import ClientSession
from secrets import token_hex, token_urlsafe
from .security import Security
from threading import Lock
import datetime
import logging
import time
import json

_LOGGER = logging.getLogger(__name__)

CLIENT_TYPE = 1                 # Android
FORMAT = 2                      # JSON
LANGUAGE = "en_US"
APP_ID = "1010"
SRC = "1010"


class MideaCloud:
    def __init__(self, session: ClientSession, username: str, password: str, server: str = None):
        self.session = session
        self.username = username
        self.password = password
        self.server = "https://mp-prod.smartmidea.net/mas/v5/app/proxy?alias=" if server == "cn" \
            else "https://mp-prod.appsmb.com/mas/v5/app/proxy?alias="
        self.login_id = None
        self.access_token = ""
        self._api_lock = Lock()
        self.login_session = None
        self.home_groups = None
        self.security = Security(server == "cn")

    async def api_request(self, endpoint, args=None, data=None):
        args = args or {}
        headers = {}
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

        if not data.get("reqId"):
            data.update({
                "reqId": token_hex(16),
            })

        url = self.server + endpoint
        random = str(int(time.time()))

        sign = self.security.new_sign(json.dumps(data), random)
        headers.update({
            "Content-Type": "application/json",
            "secretVersion": "1",
            "sign": sign,
            "random": random,
            "accessToken": self.access_token
        })
        try:
            with self._api_lock:
                r = await self.session.request("POST", url, headers=headers, data=json.dumps(data), timeout=10)
                raw = await r.read()
                _LOGGER.debug(f"Endpoint: {endpoint}, Response: {str(raw)}")
                response = json.loads(raw)
        except Exception as e:
            response = {"code": -1}
        # Check for errors, raise if there are any
        if int(response["code"]) == 0 and "data" in response:
            return response["data"]
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
                "/mj/user/login",
                data={
                    "data": {
                        # "appKey": loginKey,
                        "platform": FORMAT,
                    },
                    "iotData": {
                        "appId": APP_ID,
                        "clientType": CLIENT_TYPE,
                        "iampwd": self.security.encrypt_iam_password(self.login_id, self.password),
                        "loginAccount": self.username,
                        "password": self.security.encryptPassword(self.login_id, self.password),
                        "pushToken": token_urlsafe(120),
                        "reqId": token_hex(16),
                        "src": SRC,
                        "stamp": datetime.time().strftime("%Y%m%d%H%M%S"),
                    },
                }
            )
            if login_session:
                self.access_token = login_session["mdata"]["accessToken"]
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
            {"udpid": udpid}
        )
        if response and "tokenlist" in response:
            for token in response["tokenlist"]:
                if token["udpId"] == udpid:
                    return token["token"].upper(), token["key"].upper()
        return None, None
