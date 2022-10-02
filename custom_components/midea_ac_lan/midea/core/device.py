import threading
from ..backports.enum import StrEnum
from enum import IntEnum
from .security import Security, MSGTYPE_HANDSHAKE_REQUEST, MSGTYPE_ENCRYPTED_REQUEST
from .packet_builder import PacketBuilder
from .message import MessageType, MessageQuerySubtype, MessageSubtypeResponse
import socket
import logging
import time

_LOGGER = logging.getLogger(__name__)


class AuthException(Exception):
    pass


class ResponseException(Exception):
    pass


class RefreshFailed(Exception):
    pass


class DeviceAttributes(StrEnum):
    pass


class ParseMessageResult(IntEnum):
    SUCCESS = 0
    PADDING = 1
    ERROR = 99


class MiedaDevice(threading.Thread):
    def __init__(self,
                 name: str,
                 device_id: int,
                 device_type: int,
                 ip_address: str,
                 port: int,
                 token: str,
                 key: str,
                 protocol: int,
                 model: str):
        threading.Thread.__init__(self)
        self._attributes = {}
        self._socket = None
        self._ip_address = ip_address
        self._port = port
        self._security = Security()
        self._token = bytearray.fromhex(token) if token else None
        self._key = bytearray.fromhex(key) if key else None
        self._buffer = b""
        self._name = name
        self._device_id = device_id
        self._device_type = device_type
        self._protocol = protocol
        self._model = model
        self._updates = []
        self._unsupported_protocol = []
        self._is_run = False
        self._available = True
        self._device_protocol_version = 0
        self._sub_type = None
        self._sn = None

    @property
    def name(self):
        return self._name

    @property
    def available(self):
        return self._available

    @property
    def device_id(self):
        return self._device_id

    @property
    def device_type(self):
        return self._device_type

    @property
    def model(self):
        return self._model

    @property
    def sub_type(self):
        return self._sub_type

    @staticmethod
    def fetch_v2_message(msg):
        result = []
        while len(msg) > 0:
            factual_msg_len = len(msg)
            if factual_msg_len < 6:
                break
            alleged_msg_len = msg[4] + (msg[5] << 8)
            if factual_msg_len >= alleged_msg_len:
                result.append(msg[:alleged_msg_len])
                msg = msg[alleged_msg_len:]
        return result, msg

    def connect(self, refresh_status=True):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(10)
            self._socket.connect((self._ip_address, self._port))
            _LOGGER.debug(f"[{self._device_id}] Connected")
            if self._protocol == 3:
                self.authenticate()
            _LOGGER.debug(f"[{self._device_id}] Authentication success")
            if refresh_status:
                if self._sub_type is None:
                    self.get_sub_type()
                self.refresh_status(wait_response=True)
            self.enable_device(True)
            return True
        except socket.timeout:
            _LOGGER.debug(f"[{self._device_id}] Connection timed out")
        except socket.error:
            _LOGGER.debug(f"[{self._device_id}] Connection error")
        except AuthException:
            _LOGGER.debug(f"[{self._device_id}] Authentication failed")
        except ResponseException:
            _LOGGER.debug(f"[{self._device_id}] Unexpected response received")
        except RefreshFailed:
            _LOGGER.debug(f"[{self._device_id}] Refresh status is timed out")
        except Exception as e:
            _LOGGER.error(f"[{self._device_id}] Unknown error {repr(e)}")
        self.enable_device(False)
        return False

    def authenticate(self):
        request = self._security.encode_8370(
            self._token, MSGTYPE_HANDSHAKE_REQUEST)
        _LOGGER.debug(f"[{self._device_id}] Handshaking")
        self._socket.send(request)
        response = self._socket.recv(512)
        if len(response) < 20:
            raise AuthException()
        response = response[8: 72]
        self._security.tcp_key(response, self._key)

    def send_message(self, data):
        if self._protocol == 3:
            self.send_message_V3(data, msg_type=MSGTYPE_ENCRYPTED_REQUEST)
        else:
            self.send_message_V2(data)

    def send_message_V2(self, data):
        if self._socket is not None:
            self._socket.send(data)

    def send_message_V3(self, data, msg_type=MSGTYPE_ENCRYPTED_REQUEST):
        data = self._security.encode_8370(data, msg_type)
        self.send_message_V2(data)

    def build_send(self, cmd):
        data = cmd.serialize()
        _LOGGER.debug(f"[{self._device_id}] Sending: {cmd}")
        msg = PacketBuilder(self._device_id, data).finalize()
        self.send_message(msg)

    def get_sub_type(self):
        cmd = MessageQuerySubtype(self.device_type)
        if cmd is not None:
            self.build_send(cmd)
            try:
                while True:
                    msg = self._socket.recv(512)
                    if len(msg) == 0:
                        raise socket.error
                    result = self.parse_message(msg)
                    if result == ParseMessageResult.SUCCESS:
                        break
                    elif result == ParseMessageResult.PADDING:
                        continue
                    else:
                        raise ResponseException
            except socket.timeout:
                pass

    def refresh_status(self, wait_response=False):
        cmds = self.build_query()
        error_count = 0
        for cmd in cmds:
            if cmd.__class__.__name__ not in self._unsupported_protocol:
                self.build_send(cmd)
                if wait_response:
                    try:
                        while True:
                            msg = self._socket.recv(512)
                            if len(msg) == 0:
                                raise socket.error
                            result = self.parse_message(msg)
                            if result == ParseMessageResult.SUCCESS:
                                break
                            elif result == ParseMessageResult.PADDING:
                                continue
                            else:
                                raise ResponseException
                    except socket.timeout:
                        error_count += 1
                        self._unsupported_protocol.append(cmd.__class__.__name__)
                        _LOGGER.debug(f"[{self._device_id}] Does not supports "
                                      f"the protocol {cmd.__class__.__name__}, ignored")
                    except ResponseException:
                        error_count += 1
            else:
                error_count += 1
        if error_count == len(cmds):
            raise RefreshFailed

    def set_subtype(self):
        pass

    def pre_process_message(self, msg):
        if msg[9] == MessageType.querySubtype:
            message = MessageSubtypeResponse(msg)
            _LOGGER.debug(f"[{self.device_id}] Received: {message}")
            self._sub_type = message.sub_type
            self.set_subtype()
            self._device_protocol_version = message.device_protocol_version
            _LOGGER.debug(f"[{self._device_id}] Subtype: {self._sub_type}. "
                          f"Device protocol version: {self._device_protocol_version}")
            return False
        return True

    def parse_message(self, msg):
        if self._protocol == 3:
            messages, self._buffer = self._security.decode_8370(self._buffer + msg)
        else:
            messages, self._buffer = self.fetch_v2_message(self._buffer + msg)
        if len(messages) == 0:
            return ParseMessageResult.PADDING
        for message in messages:
            if message == b"ERROR":
                return ParseMessageResult.ERROR
            payload_len = message[4] + (message[5] << 8) - 56
            payload_type = message[2] + (message[3] << 8)
            if payload_type in [0x1001, 0x0001]:
                # Heartbeat detected
                pass
            elif len(message) > 56:
                cryptographic = message[40:-16]
                if payload_len % 16 == 0:
                    decrypted = self._security.aes_decrypt(cryptographic)
                    if self.pre_process_message(decrypted):
                        status = self.process_message(decrypted)
                        if len(status) > 0:
                            self.update_all(status)
                        else:
                            _LOGGER.debug(f"[{self._device_id}] Unidentified protocol")
                else:
                    _LOGGER.warning(
                        f"[{self._device_id}] Illegal payload, "
                        f"original message = {msg.hex()}, buffer = {self._buffer.hex()}, "
                        f"8370 decoded = {message.hex()}, payload type = {payload_type}, "
                        f"alleged payload length = {payload_len}, factual payload length = {len(cryptographic)}"
                    )
            else:
                _LOGGER.warning(
                    f"[{self._device_id}] Illegal message, "
                    f"original message = {msg.hex()}, buffer = {self._buffer.hex()}, "
                    f"8370 decoded = {message.hex()}, payload type = {payload_type}, "
                    f"alleged payload length = {payload_len}, message length = {len(message)}, "
                )
        return ParseMessageResult.SUCCESS

    def build_query(self):
        raise NotImplementedError

    def process_message(self, msg):
        raise NotImplementedError

    def send_heartbeat(self):
        msg = PacketBuilder(self._device_id, bytearray([0x00])).finalize(msg_type=0)
        self.send_message(msg)

    def register_update(self, update):
        self._updates.append(update)

    def update_all(self, status):
        _LOGGER.debug(f"[{self._device_id}] Status update: {status}")
        for update in self._updates:
            update(status)

    def enable_device(self, available=True):
        self._available = available
        status = {"available": available}
        self.update_all(status)

    def open(self):
        if not self._is_run:
            self._is_run = True
            threading.Thread.start(self)

    def close(self):
        if self._is_run:
            self._is_run = False
            self.close_socket()

    def close_socket(self):
        self._unsupported_protocol = []
        self._buffer = b""
        if self._socket:
            self._socket.close()
            self._socket = None

    def run(self):
        while self._is_run:
            while self._socket is None:
                if self.connect(refresh_status=True) is False:
                    if not self._is_run:
                        return
                    self.close_socket()
                    time.sleep(5)
            timeout_counter = 0
            start = time.time()
            previous_refresh = start
            previous_heartbeat = start
            while True:
                try:
                    now = time.time()
                    if now - previous_refresh >= 30:
                        self.refresh_status()
                        previous_refresh = now
                    if now - previous_heartbeat >= 10:
                        self.send_heartbeat()
                        previous_heartbeat = now
                    msg = self._socket.recv(512)
                    msg_len = len(msg)
                    if msg_len == 0:
                        raise socket.error("Connection closed by peer")
                    result = self.parse_message(msg)
                    if result == ParseMessageResult.ERROR:
                        _LOGGER.debug(f"[{self._device_id}] Message 'ERROR' received")
                        self.close_socket()
                        break
                    elif result == ParseMessageResult.SUCCESS:
                        timeout_counter = 0
                except socket.timeout:
                    timeout_counter = timeout_counter + 1
                    if timeout_counter >= 12:
                        _LOGGER.debug(f"[{self._device_id}] Heartbeat timed out")
                        self.close_socket()
                        break
                except socket.error as e:
                    _LOGGER.debug(f"[{self._device_id}] Socket error {repr(e)}")
                    self.close_socket()
                    break
                except Exception as e:
                    _LOGGER.debug(f"[{self._device_id}] Unknown error {repr(e)}")
                    self.close_socket()
                    break

    def set_attribute(self, attr, value):
        raise NotImplementedError

    def get_attribute(self, attr):
        return self._attributes.get(attr)

    def set_customize(self, customize):
        pass

    @property
    def attributes(self):
        ret = {}
        for status in self._attributes.keys():
            ret[status.value] = self._attributes[status]
        return ret
