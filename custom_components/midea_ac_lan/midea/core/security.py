import logging
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.strxor import strxor
from Crypto.Random import get_random_bytes
from hashlib import md5, sha256
from urllib.parse import urlparse
import hmac
import urllib

_LOGGER = logging.getLogger(__name__)

MSGTYPE_HANDSHAKE_REQUEST = 0x0
MSGTYPE_HANDSHAKE_RESPONSE = 0x1
MSGTYPE_ENCRYPTED_RESPONSE = 0x3
MSGTYPE_ENCRYPTED_REQUEST = 0x6


class CloudSecurity:
    def __init__(self, iotKey, loginKey):
        self._hmackey = "PROD_VnoClJI9aikS8dyy"
        self._iotkey = iotKey
        self._loginKey = loginKey

    def sign(self, data: str, random: str) -> str:
        msg = self._iotkey
        if data:
            msg += data
        msg += random
        sign = hmac.new(self._hmackey.encode("ascii"), msg.encode("ascii"), sha256)
        return sign.hexdigest()

    def encryptPassword(self, loginId, data):
        m = sha256()
        m.update(data.encode("ascii"))
        loginHash = loginId + m.hexdigest() + self._loginKey
        m = sha256()
        m.update(loginHash.encode("ascii"))
        return m.hexdigest()

    def encrypt_iam_password(self, loginId, data) -> str:
        md = md5()
        md.update(data.encode("ascii"))
        md_second = md5()
        md_second.update(md.hexdigest().encode("ascii"))
        login_hash = loginId + md_second.hexdigest() + self._loginKey
        sha = sha256()
        sha.update(login_hash.encode("ascii"))
        return sha.hexdigest()

    @staticmethod
    def get_deviceid(username):
        return md5(username.encode("utf-8")).digest().hex()[:16]

    @staticmethod
    def get_udpid(data):
        data = bytearray(sha256(data).digest())
        for i in range(0, 16):
            data[i] ^= data[i + 16]
        return data[0: 16].hex()

    @staticmethod
    def decrypt_with_key(data, key="96c7acdfdb8af79a"):
        if isinstance(data, str):
            data = bytes.fromhex(data)
        if isinstance(key, str):
            key = key.encode()
        return unpad(AES.new(key, AES.MODE_ECB).decrypt(data), 16).decode()

    @staticmethod
    def encrypt_with_key(data, key="96c7acdfdb8af79a"):
        if isinstance(data, str):
            data = bytes.fromhex(data)
        if isinstance(key, str):
            key = key.encode()
        return AES.new(key, AES.MODE_ECB).encrypt(pad(data, 16))


class MeijuCloudSecurity(CloudSecurity):
    def __init__(self, iotKey, loginKey):
        super().__init__(iotKey, loginKey)

    def encrypt_iam_password(self, loginId, data) -> str:
        md = md5()
        md.update(data.encode("ascii"))
        md_second = md5()
        md_second.update(md.hexdigest().encode("ascii"))
        return md_second.hexdigest()


class SmartLifeSecurity(CloudSecurity):
    def __init__(self, iotKey, loginKey):
        super().__init__(iotKey, loginKey)

    def sign(self, url, payload):
        path = urlparse(url).path
        query = sorted(payload.items(), key=lambda x: x[0])
        query = urllib.parse.unquote_plus(urllib.parse.urlencode(query))
        sign = path + query + self._loginKey
        m = sha256()
        m.update(sign.encode("ASCII"))
        return m.hexdigest()


class LocalSecurity:
    def __init__(self):
        self.blockSize = 16
        self.iv = b"\0" * 16
        self.aes_key = bytes.fromhex("6a92ef406bad2f0359baad994171ea6d")
        self.salt = bytes.fromhex("78686469776a6e6368656b6434643531326368646a783564386534633339344432443753")
        self._tcp_key = None
        self._request_count = 0
        self._response_count = 0

    def aes_decrypt(self, raw):
        try:
            return unpad(AES.new(self.aes_key, AES.MODE_ECB).decrypt(bytearray(raw)), self.blockSize)
        except ValueError as e:
            _LOGGER.error(f"Error in aes_decrypt: {repr(e)} - data: {raw.hex()}")
        return bytearray(0)

    def aes_encrypt(self, raw):
        return AES.new(self.aes_key, AES.MODE_ECB).encrypt(bytearray(pad(raw, self.blockSize)))

    def aes_cbc_decrypt(self, raw, key):
        return AES.new(key=key, mode=AES.MODE_CBC, iv=self.iv).decrypt(raw)

    def aes_cbc_encrypt(self, raw, key):
        return AES.new(key=key, mode=AES.MODE_CBC, iv=self.iv).encrypt(raw)

    def encode32_data(self, raw):
        return md5(raw + self.salt).digest()

    def tcp_key(self, response, key):
        if response == b"ERROR":
            raise Exception("authentication failed")
        if len(response) != 64:
            raise Exception("unexpected data length")
        payload = response[:32]
        sign = response[32:]
        plain = self.aes_cbc_decrypt(payload, key)
        if sha256(plain).digest() != sign:
            raise Exception("sign does not match")
        self._tcp_key = strxor(plain, key)
        self._request_count = 0
        self._response_count = 0
        return self._tcp_key

    def encode_8370(self, data, msgtype):
        header = bytearray([0x83, 0x70])
        size, padding = len(data), 0
        if msgtype in (MSGTYPE_ENCRYPTED_RESPONSE, MSGTYPE_ENCRYPTED_REQUEST):
            if (size + 2) % 16 != 0:
                padding = 16 - (size + 2 & 0xf)
                size += padding + 32
                data += get_random_bytes(padding)
        header += size.to_bytes(2, "big")
        header += bytearray([0x20, padding << 4 | msgtype])
        data = self._request_count.to_bytes(2, "big") + data
        self._request_count += 1
        if self._request_count >= 0xFFFF:
            self._request_count = 0
        if msgtype in (MSGTYPE_ENCRYPTED_RESPONSE, MSGTYPE_ENCRYPTED_REQUEST):
            sign = sha256(header + data).digest()
            data = self.aes_cbc_encrypt(raw=data, key=self._tcp_key) + sign
        return header + data

    def decode_8370(self, data):
        if len(data) < 6:
            return [], data
        header = data[:6]
        if header[0] != 0x83 or header[1] != 0x70:
            raise Exception("not an 8370 message")
        size = int.from_bytes(header[2:4], "big") + 8
        leftover = None
        if len(data) < size:
            return [], data
        elif len(data) > size:
            leftover = data[size:]
            data = data[:size]
        if header[4] != 0x20:
            raise Exception("missing byte 4")
        padding = header[5] >> 4
        msgtype = header[5] & 0xf
        data = data[6:]
        if msgtype in (MSGTYPE_ENCRYPTED_RESPONSE, MSGTYPE_ENCRYPTED_REQUEST):
            sign = data[-32:]
            data = data[:-32]
            data = self.aes_cbc_decrypt(raw=data, key=self._tcp_key)
            if sha256(header + data).digest() != sign:
                raise Exception("sign does not match")
            if padding:
                data = data[:-padding]
        self._response_count = int.from_bytes(data[:2], "big")
        data = data[2:]
        if leftover:
            packets, incomplete = self.decode_8370(leftover)
            return [data] + packets, incomplete
        return [data], b""