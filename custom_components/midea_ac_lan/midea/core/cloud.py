import logging
import time
import datetime
import json
import base64
from threading import Lock
from aiohttp import ClientSession
from secrets import token_hex
from .security import CloudSecurity, MeijuCloudSecurity, MSmartCloudSecurity

_LOGGER = logging.getLogger(__name__)

clouds = {
    "美的美居": {
        "class_name": "MeijuCloud",
        "app_id": "900",
        "app_key": "46579c15",
        "login_key": "ad0ee21d48a64bf49f4fb583ab76e799",
        "iot_key": bytes.fromhex(format(9795516279659324117647275084689641883661667, 'x')).decode(),
        "hmac_key": bytes.fromhex(format(117390035944627627450677220413733956185864939010425, 'x')).decode(),
        "api_url": "https://mp-prod.smartmidea.net/mas/v5/app/proxy?alias=",
    },
    "MSmartHome": {
        "class_name": "MSmartHomeCloud",
        "app_id": "1010",
        "app_key": "ac21b9f9cbfe4ca5a88562ef25e2b768",
        "iot_key": bytes.fromhex(format(7882822598523843940, 'x')).decode(),
        "hmac_key": bytes.fromhex(format(117390035944627627450677220413733956185864939010425, 'x')).decode(),
        "api_url": "https://mp-prod.appsmb.com/mas/v5/app/proxy?alias=",
    }
}

default_keys = {
    99: {
        "token": "ee755a84a115703768bcc7c6c13d3d629aa416f1e2fd798beb9f78cbb1381d09"
                 "1cc245d7b063aad2a900e5b498fbd936c811f5d504b2e656d4f33b3bbc6d1da3",
        "key": "ed37bd31558a4b039aaf4e7a7a59aa7a75fd9101682045f69baf45d28380ae5c"
    }
}


class MideaCloud:
    def __init__(
            self,
            session: ClientSession,
            security: CloudSecurity,
            app_key: str,
            account: str,
            password: str,
            api_url: str
    ):
        self._device_id = CloudSecurity.get_deviceid(account)
        self._session = session
        self._security = security
        self._api_lock = Lock()
        self._app_key = app_key
        self._account = account
        self._password = password
        self._api_url = api_url
        self._access_token = None
        self._login_id = None

    def _make_general_data(self):
        return {}

    async def _api_request(self, endpoint: str, data: dict, header=None) -> dict | None:
        header = header or {}
        if not data.get("reqId"):
            data.update({
                "reqId": token_hex(16)
            })
        if not data.get("stamp"):
            data.update({
                "stamp":  datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            })
        random = str(int(time.time()))
        url = self._api_url + endpoint
        dump_data = json.dumps(data)
        sign = self._security.sign(dump_data, random)
        header.update({
            "content-type": "application/json; charset=utf-8",
            "secretVersion": "1",
            "sign": sign,
            "random": random,
        })
        if self._access_token is not None:
            header.update({
                "accesstoken": self._access_token
            })
        response:dict = {"code": -1}
        for i in range(0, 3):
            try:
                with self._api_lock:
                    r = await self._session.request("POST", url, headers=header, data=dump_data, timeout=10)
                    raw = await r.read()
                    _LOGGER.debug(f"Midea cloud API url: {url}, data: {data}, response: {raw}")
                    response = json.loads(raw)
                    break
            except Exception as e:
                pass
        if int(response["code"]) == 0 and "data" in response:
            return response["data"]
        print(response)
        return None

    async def _get_login_id(self) -> str | None:
        data = self._make_general_data()
        data.update({
            "loginAccount": f"{self._account}"
        })
        if response := await self._api_request(
            endpoint="/v1/user/login/id/get",
            data=data
        ):
            return response.get("loginId")
        return None

    async def login(self) -> bool:
        raise NotImplementedError()

    async def get_keys(self, appliance_id: int):
        result = {}
        for method in [1, 2]:
            udp_id = self._security.get_udp_id(appliance_id, method)
            data = self._make_general_data()
            data.update({
                "udpid": udp_id
            })
            response = await self._api_request(
                endpoint="/v1/iot/secure/getToken",
                data=data
            )
            if response and "tokenlist" in response:
                for token in response["tokenlist"]:
                    if token["udpId"] == udp_id:
                        result[method] = {
                            "token": token["token"].lower(),
                            "key": token["key"].lower()
                        }
        result.update(default_keys)
        return result


class MeijuCloud(MideaCloud):
    APP_ID = "900"
    APP_VERSION = "8.20.0.2"

    def __init__(
            self,
            cloud_name: str,
            session: ClientSession,
            account: str,
            password: str,
    ):
        super().__init__(
            session=session,
            security=MeijuCloudSecurity(
                login_key=clouds[cloud_name].get("login_key"),
                iot_key=clouds[cloud_name].get("iot_key"),
                hmac_key=clouds[cloud_name].get("hmac_key"),
            ),
            app_key=clouds[cloud_name]["app_key"],
            account=account,
            password=password,
            api_url=clouds[cloud_name]["api_url"]
        )

    async def login(self) -> bool:
        if login_id := await self._get_login_id():
            self._login_id = login_id
            stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            data = {
                "iotData": {
                    "clientType": 1,
                    "deviceId": self._device_id,
                    "iampwd": self._security.encrypt_iam_password(self._login_id, self._password),
                    "iotAppId": self.APP_ID,
                    "loginAccount": self._account,
                    "password": self._security.encrypt_password(self._login_id, self._password),
                    "reqId": token_hex(16),
                    "stamp": stamp
                },
                "data": {
                    "appKey": self._app_key,
                    "deviceId": self._device_id,
                    "platform": 2
                },
                "timestamp": stamp,
                "stamp": stamp
            }
            if response := await self._api_request(
                endpoint="/mj/user/login",
                data=data
            ):
                self._access_token = response["mdata"]["accessToken"]
                self._security.set_aes_keys(
                    self._security.aes_decrypt_with_fixed_key(
                        response["key"]
                    ), None
                )

                return True
        return False


class MSmartHomeCloud(MideaCloud):
    APP_ID = "1010"
    SRC = "10"
    APP_VERSION = "3.0.2"

    def __init__(
            self,
            cloud_name: str,
            session: ClientSession,
            account: str,
            password: str,
    ):
        super().__init__(
            session=session,
            security=MSmartCloudSecurity(
                login_key=clouds[cloud_name].get("app_key"),
                iot_key=clouds[cloud_name].get("iot_key"),
                hmac_key=clouds[cloud_name].get("hmac_key"),
            ),
            app_key=clouds[cloud_name]["app_key"],
            account=account,
            password=password,
            api_url=clouds[cloud_name]["api_url"]
        )
        self._auth_base = base64.b64encode(
            f"{self._app_key}:{clouds['MSmartHome']['iot_key']}".encode("ascii")
        ).decode("ascii")
        self._uid = ""

    def _make_general_data(self):
        return {
            "appVersion": self.APP_VERSION,
            "src": self.SRC,
            "format": "2",
            "stamp": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            "platformId": "1",
            "deviceId": self._device_id,
            "reqId": token_hex(16),
            "uid": self._uid,
            "clientType": "1",
            "appId": self.APP_ID,
        }

    async def _api_request(self, endpoint: str, data: dict, header=None) -> dict | None:
        header = header or {}
        header.update({
            "x-recipe-app": self.APP_ID,
            "authorization": f"Basic {self._auth_base}"
        })
        if len(self._uid) > 0:
            header.update({
                "uid": self._uid
            })
        return await super()._api_request(endpoint, data, header)

    async def _re_route(self):
        data = self._make_general_data()
        data.update({
            "userType": "0",
            "userName": f"{self._account}"
        })
        if response := await self._api_request(
            endpoint="/v1/multicloud/platform/user/route",
            data=data
        ):
            if api_url := response.get("masUrl"):
                self._api_url = api_url

    async def login(self) -> bool:
        await self._re_route()
        if login_id := await self._get_login_id():
            self._login_id = login_id
            iot_data = self._make_general_data()
            iot_data.pop("uid")
            stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            iot_data.update({
                "iampwd": self._security.encrypt_iam_password(self._login_id, self._password),
                "loginAccount": self._account,
                "password": self._security.encrypt_password(self._login_id, self._password),
                "stamp": stamp
            })
            data = {
                "iotData": iot_data,
                "data": {
                    "appKey": self._app_key,
                    "deviceId": self._device_id,
                    "platform": "2"
                },
                "stamp": stamp
            }
            if response := await self._api_request(
                endpoint="/mj/user/login",
                data=data
            ):
                self._uid = response["uid"]
                self._access_token = response["mdata"]["accessToken"]
                self._security.set_aes_keys(response["accessToken"], response["randomData"])
                return True
        return False


def get_midea_cloud(cloud_name: str, session: ClientSession, account: str, password: str) -> MideaCloud | None:
    cloud = None
    if cloud_name in clouds.keys():
        cloud = globals()[clouds[cloud_name]["class_name"]](
            cloud_name=cloud_name,
            session=session,
            account=account,
            password=password
        )
    return cloud
