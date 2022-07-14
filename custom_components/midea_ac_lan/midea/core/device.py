import threading
from .security import Security, MSGTYPE_HANDSHAKE_REQUEST, MSGTYPE_ENCRYPTED_REQUEST
from .packet_builder import PacketBuilder
import socket
import logging
import time

_LOGGER = logging.getLogger(__name__)


class AuthException(Exception):
    pass


class ResponseException(Exception):
    pass


class MiedaDevice(threading.Thread):
    def __init__(self,
                 device_id: int,
                 device_type: int,
                 host: str,
                 port: int,
                 token: str,
                 key: str,
                 protocol: int,
                 model: str):
        threading.Thread.__init__(self)
        self._socket = None
        self._host = host
        self._port = port
        self._security = Security()
        self._token = bytearray.fromhex(token) if token else None
        self._key = bytearray.fromhex(key) if key else None
        self._buffer = b""
        self._device_id = device_id
        self._device_type = device_type
        self._protocol = protocol
        self._model = model
        self._updates = []
        self._is_run = False
        self._available = True

    @property
    def available(self):
        return self._available

    @property
    def device_id(self):
        return self._device_id

    @property
    def model(self):
        return self._model

    def connect(self, refresh_status=True):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(10)
            self._socket.connect((self._host, self._port))
            _LOGGER.debug(f"Device [{self._device_id}] connected at socket {self._socket}")
            # auth
            if self._protocol == 3:
                self.authenticate()
            _LOGGER.debug(f"Device [{self._device_id}] authenticated")
            self.enable_device(True)
            if refresh_status:
                self.refresh_status(wait_response=True)
            return True
        except socket.timeout:
            pass
        except socket.error:
            pass
        except AuthException:
            pass
        return False

    def authenticate(self):
        request = self._security.encode_8370(
            self._token, MSGTYPE_HANDSHAKE_REQUEST)
        _LOGGER.debug(f"Device [{self._device_id}] Handshaking")
        self._socket.send(request)
        response = self._socket.recv(512)
        if len(response) < 20:
            raise AuthException()
        _LOGGER.debug(f"Device [{self._device_id}] Handshake completed")
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
        _LOGGER.debug(f"Send to device [{self._device_id}]: {cmd}")
        msg = PacketBuilder(self._device_id, data).finalize()
        self.send_message(msg)

    def refresh_status(self, wait_response=False):
        cmd = self.build_query()
        self.build_send(cmd)
        if wait_response:
            msg = self._socket.recv(512)
            msg_len = len(msg)
            if msg_len == 0:
                raise socket.error
            if not self.parse_message(msg):
                raise ResponseException

    def parse_message(self, msg):
        if self._protocol == 3:
            messages, self._buffer = self._security.decode_8370(self._buffer + msg)
        else:
            messages = [msg]
        for message in messages:
            if len(message) > 40 + 16 + 16 and message[3] != 0x10 and message[3] != 0x00:  # Heartbeat of V3
                message = self._security.aes_decrypt(message[40:-16])
                self.process_message(message)
            else:
                if message == b"ERROR":
                    return False
        return True

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
        if self._socket:
            self._socket.close()
            self._socket = None
            self._buffer = b""

    def run(self):
        while self._is_run:
            while self._socket is None:
                _LOGGER.debug(f"Device [{self._device_id}] ready to re-open device")
                if self.connect(True) is False:
                    if not self._is_run:
                        return
                    self.enable_device(False)
                    time.sleep(5)
                    continue
            counter = 0
            timeout_counter = 0
            while True:
                try:
                    msg = self._socket.recv(512)
                    msg_len = len(msg)
                    if msg_len == 0:
                        raise socket.error("Zero-length received")
                    timeout_counter = 0
                    if not self.parse_message(msg):
                        _LOGGER.debug(f"Device [{self._device_id}] b'ERROR' message received, reconnecting")
                        self.close_socket()
                        break
                except socket.timeout:
                    timeout_counter = timeout_counter + 1
                    if timeout_counter >= 10:
                        _LOGGER.debug(f"Device [{self._device_id}] heartbeat timed out detected, reconnecting")
                        self.close_socket()
                        break
                    self.send_heartbeat()
                    if counter >= 5:
                        self.refresh_status()
                        counter = 0
                    else:
                        counter = counter + 1
                except socket.error as e:
                    _LOGGER.debug(f"Device [{self._device_id}] except socket.error {e} raised in socket.recv()")
                    self.close_socket()
                    break
                except Exception as e:
                    _LOGGER.debug(f"Device [{self._device_id}] except {e} raised")
                    self.close_socket()
                    break
            self.enable_device(False)


