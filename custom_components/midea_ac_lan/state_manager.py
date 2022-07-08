import logging
import time
import threading
import socket
from .midea.security import Security, MSGTYPE_HANDSHAKE_REQUEST, MSGTYPE_ENCRYPTED_REQUEST
from .midea.message_parser import MessageParser
from .midea.command import CommandRequest, CommandNewProtocolSet, CommandGeneralSet
from .midea.packet_builder import PacketBuilder

_LOGGER = logging.getLogger(__name__)


class AuthException(Exception):
    pass


class DeviceState:
    def __init__(self):
        self.available = False
        self.prompt_tone = True
        self.power = False
        self.mode = 0
        self.fan_speed = 102
        self.swing_vertical = False
        self.swing_horizontal = False
        self.target_temperature = 20.0
        self.indoor_temperature = 20.0
        self.outdoor_temperature = 20.0
        self.comfort_mode = False
        self.eco_mode = False
        self.aux_heat = False
        self.indirect_wind = False


class DeviceManager(threading.Thread):
    def __init__(self, device_id, host, port, token, key, protocol, model):
        threading.Thread.__init__(self)
        self._lock = threading.Lock()
        self._socket = None
        self._host = host
        self._port = port
        self._is_run = False
        self._on_updates = []
        self._timeout_counter = 0
        self._security = Security()
        self._token = bytearray.fromhex(token) if token else None
        self._key = bytearray.fromhex(key) if key else None
        self._buffer = b''
        self._device_id = device_id
        self._protocol = protocol
        self._model = model
        self._status = DeviceState()
        self._entity_id = None
        self._updates = []

    def set_token_key(self, token, key):
        self._token = bytearray.fromhex(token) if token else None
        self._key = bytearray.fromhex(key) if key else None

    def run(self):

        while self._is_run:
            while self._socket is None:
                _LOGGER.debug(f"Device [{self._device_id}] ready to re-open device")
                if self.open(False) is False:
                    time.sleep(10)
                if not self._is_run:
                    _LOGGER.debug(f"Device [{self._device_id}] thread existing")
                    if self._socket is not None:
                        self._socket.close()
                        self._socket = None
                    break
            counter = 0
            timeout_counter = 0
            _LOGGER.debug(f"Device [{self._device_id}] ready to receive loop")
            while self._is_run:
                try:
                    msg = self._socket.recv(1024)
                    _LOGGER.debug(f"Device [{self._device_id}] received original message as hex {msg.hex()}")
                    if not self._is_run:
                        break
                    msg_len = len(msg)
                    if msg_len == 0:
                        raise socket.error("zero-length received")
                    timeout_counter = 0
                    # Message process
                    if not self.process_message(msg):
                        _LOGGER.debug(f"Device [{self._device_id}] b'ERROR' message received, reconnecting")
                        self._close()
                        break
                except socket.timeout:
                    timeout_counter = timeout_counter + 1
                    if timeout_counter >= 10:
                        _LOGGER.debug(f"Device [{self._device_id}] heartbeat timed out detected, reconnecting")
                        self._close()
                        break
                    self.send_heartbeat()
                    if counter >= 5:
                        self.refresh_status()
                        counter = 0
                    else:
                        counter = counter + 1
                except socket.error as e:
                    _LOGGER.debug(f"Device [{self._device_id}] except socket.error {e} raised in socket.recv()")
                    self._close()
                    break
                except Exception as e:
                    _LOGGER.debug(f"Device [{self._device_id}] except {e} raised")
                    self._close()
                    break
            self.enable_devices(False)

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

    def enable_devices(self, enable=True):
        self.update_all({"available": enable})

    def update_all(self, updates):
        if updates:
            _LOGGER.debug(f"Device [{self._device_id}] status update to: {updates}")
            for update in self._updates:
                update(updates)

    def process_message(self, msg):
        if self._protocol == 3:
            messages, self._buffer = self._security.decode_8370(self._buffer + msg)
        else:
            messages = [msg]
        for message in messages:
            if len(message) > 40 + 16 + 16 and message[3] != 0x10 and message[3] != 0x00:  # Heartbeat of V3
                message = self._security.aes_decrypt(message[40:-16])
                parser = MessageParser(message)
                updates = self.parse_message(parser)
                self.update_all(updates)
            else:
                if message == b'ERROR':
                    return False
                _LOGGER.debug(f"Device [{self._device_id}] heartbeat detected")
        return True

    def parse_message(self, parser: MessageParser):
        updates = {"available": True}
        if parser.msg_type == 0x2C0 or parser.msg_type == 0x3C0:
            self._status.power = parser.power
            self._status.mode = parser.mode
            self._status.fan_speed = parser.fan_speed
            self._status.swing_vertical = parser.swing_vertical
            self._status.swing_horizontal = parser.swing_horizontal
            self._status.target_temperature = parser.target_temperature
            self._status.indoor_temperature = parser.indoor_temperature
            if parser.outdoor_temperature != 102.0:
                self._status.outdoor_temperature = parser.outdoor_temperature
            else:
                self._status.outdoor_temperature = 0.0
            self._status.comfort_mode = parser.comfort_mode
            self._status.eco_mode = parser.eco_mode
            self._status.aux_heat = parser.aux_heat
            if not self._status.power:
                self._status.indirect_wind = False
            elif self._status.swing_vertical:
                self._status.indirect_wind = False
            updates.update({
                "power": self._status.power,
                "mode": self._status.mode,
                "fan_speed": self._status.fan_speed,
                "swing_vertical": self._status.swing_vertical,
                "swing_horizontal": self._status.swing_horizontal,
                "target_temperature": self._status.target_temperature,
                "indoor_temperature": self._status.indoor_temperature,
                "outdoor_temperature": self._status.outdoor_temperature,
                "comfort_mode": self._status.comfort_mode,
                "eco_mode": self._status.eco_mode,
                "aux_heat": self._status.aux_heat,
                "indirect_wind": self._status.indirect_wind,
            })
        elif parser.msg_type == 0x4A1:
            self._status.indoor_temperature = parser.indoor_temperature
            if parser.outdoor_temperature != 102.0:
                self._status.outdoor_temperature = parser.outdoor_temperature
            else:
                self._status.outdoor_temperature = 0.0
            updates.update({
                "indoor_temperature":  self._status.indoor_temperature,
                "outdoor_temperature":  self._status.outdoor_temperature
            })
        elif parser.msg_type == 0x5A0:
            self._status.power = parser.power
            self._status.mode = parser.mode
            self._status.fan_speed = parser.fan_speed
            self._status.swing_vertical = parser.swing_vertical
            self._status.swing_horizontal = parser.swing_horizontal
            self._status.target_temperature = parser.target_temperature
            self._status.comfort_mode = parser.comfort_mode
            self._status.eco_mode = parser.eco_mode
            self._status.aux_heat = parser.aux_heat
            if not self._status.power:
                self._status.indirect_wind = False
            elif self._status.swing_vertical:
                self._status.indirect_wind = False
            updates.update({
                "power":  self._status.power,
                "mode":  self._status.mode,
                "fan_speed":  self._status.fan_speed,
                "swing_vertical":  self._status.swing_vertical,
                "swing_horizontal":  self._status.swing_horizontal,
                "target_temperature":  self._status.target_temperature,
                "comfort_mode":  self._status.comfort_mode,
                "eco_mode":  self._status.eco_mode,
                "aux_heat": self._status.aux_heat,
                "indirect_wind": self._status.indirect_wind,
            })
        elif parser.msg_type == 0x5B5 or parser.msg_type == 0x2B0:
            self._status.indirect_wind = parser.indirect_wind
            updates.update({"indirect_wind":  self._status.indirect_wind})
        else:
            _LOGGER.debug(f"Received unknown message from device [{self._device_id}]: {parser}")
        _LOGGER.debug(f"Received message from device [{self._device_id}]: {parser}")
        return updates

    def open(self, start_thread):
        result = False
        _LOGGER.debug(f"Try to connect to device [{self._device_id}]")
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(10)
            self._socket.connect((self._host, self._port))
            _LOGGER.debug(f"Device [{self._device_id}] connected at socket {self._socket}")
            #auth
            if self._protocol == 3:
                self.authenticate()
            _LOGGER.debug(f"Device [{self._device_id}] authenticated")
            self.refresh_status(wait_response=True)
            result = True
        except socket.timeout:
            _LOGGER.debug(f"Device [{self._device_id}] socket connect timed out")
            self._socket.close()
            self._socket = None
        except socket.error as e:
            _LOGGER.debug(f"Device [{self._device_id}] socket connect error {e}")
            self._socket.close()
            self._socket = None
        except AuthException as e:
            _LOGGER.warning(f"Device [{self._device_id}] authentication error {e}")
        except Exception as e:
            _LOGGER.error(f"Device [{self._device_id}] socket connect error {e}")
        if start_thread:
            self._is_run = True
            threading.Thread.start(self)
        return result

    def _close(self):
        if self._socket:
            self._socket.close()
        self._socket = None
        self._buffer = b''

    def close(self, stop_run=False):
        self._is_run = not stop_run
        self._close()

    def authenticate(self):
        request = self._security.encode_8370(
            self._token, MSGTYPE_HANDSHAKE_REQUEST)
        _LOGGER.debug(f"Device [{self._device_id}] Handshaking")
        self._socket.send(request)
        response = self._socket.recv(512)
        if len(response) < 20:
            raise AuthException();
        _LOGGER.debug(f"Device [{self._device_id}] Handshake completed")
        response = response[8: 72]
        self._security.tcp_key(response, self._key)

    def refresh_status(self, wait_response=False):
        cmd = CommandRequest()
        data = cmd.finalize()
        _LOGGER.debug(f"Send message to device [{self._device_id}]: {cmd}")
        msg = PacketBuilder(self._device_id, data).finalize()
        self.send_message(msg)
        if wait_response:
            msg = self._socket.recv(512)
            _LOGGER.debug(f"Device [{self._device_id}] received original message as hex {msg.hex()}")
            msg_len = len(msg)
            if msg_len == 0:
                raise socket.error
            self.process_message(msg)

    @property
    def model(self):
        return self._model

    @property
    def device_id(self):
        return self._device_id

    def get_status(self, attr):
        if hasattr(self._status, attr):
            return self._status.__getattribute__(attr)
        else:
            return None

    def send_heartbeat(self):
        msg = PacketBuilder(self._device_id, bytearray([0x00])).finalize(msg_type=0)
        self.send_message(msg)

    def make_command_set(self):
        cmd = CommandGeneralSet(prompt_tone=self._status.prompt_tone)
        cmd.set_power(self._status.power)
        cmd.set_mode(self._status.mode)
        cmd.set_fan_speed(self._status.fan_speed)
        cmd.set_swing(self._status.swing_vertical, self._status.swing_horizontal)
        cmd.set_target_temperature(self._status.target_temperature)
        cmd.set_comfort_mode(self._status.comfort_mode)
        cmd.set_eco_mode(self._status.eco_mode)
        return cmd

    def set_status(self, cmd: CommandRequest):
        data = cmd.finalize()
        _LOGGER.debug(f"Send message to device [{self._device_id}]: {cmd}")
        msg = PacketBuilder(self._device_id, data).finalize()
        self.send_message(msg)

    def set_prompt_tone(self, prompt_tone: bool):
        self._status.prompt_tone = prompt_tone

    def set_power(self, power: bool):
        cmd = self.make_command_set()
        cmd.set_power(power)
        self.set_status(cmd)

    def set_mode(self, mode: int):
        cmd = self.make_command_set()
        cmd.set_mode(mode)
        if mode is not None:
            if mode > 0:
                cmd.set_power(True)
            else:
                cmd.set_power(False)
        self.set_status(cmd)

    def set_target_temperature(self, temperature: float, mode=None):
        cmd = self.make_command_set()
        cmd.set_target_temperature(temperature)
        if mode is not None:
            if mode > 0:
                cmd.set_power(True)
            else:
                cmd.set_power(False)
            cmd.set_mode(mode)
        self.set_status(cmd)

    def set_swing_vertical(self, swing_vertical):
        cmd = self.make_command_set()
        cmd.set_swing(swing_vertical, self._status.swing_horizontal)
        self.set_status(cmd)

    def set_swing_horizontal(self, swing_horizontal):
        cmd = self.make_command_set()
        cmd.set_swing(self._status.swing_vertical, swing_horizontal)
        self.set_status(cmd)

    def set_swing(self, swing_vertical, swing_horizontal):
        cmd = self.make_command_set()
        cmd.set_swing(swing_vertical, swing_horizontal)
        self.set_status(cmd)

    def set_fan_speed(self, fan_speed):
        if fan_speed == "auto":
            fan_speed = 102
        cmd = self.make_command_set()
        cmd.set_fan_speed(fan_speed)
        self.set_status(cmd)

    def set_comfort_mode(self, comfort_mode):
        cmd = self.make_command_set()
        cmd.set_comfort_mode(comfort_mode)
        self.set_status(cmd)

    def set_eco_mode(self, eco_mode):
        cmd = self.make_command_set()
        cmd.set_eco_mode(eco_mode)
        self.set_status(cmd)

    def set_aux_heat(self, aux_heat):
        cmd = self.make_command_set()
        cmd.set_aux_heat(aux_heat)
        self.set_status(cmd)

    def set_indirect_wind(self, indirect_wind):
        cmd = CommandNewProtocolSet(prompt_tone=self._status.prompt_tone)
        cmd.set_indirect_wind(indirect_wind)
        self.set_status(cmd)

    def add_update(self, update):
        self._updates.append(update)
