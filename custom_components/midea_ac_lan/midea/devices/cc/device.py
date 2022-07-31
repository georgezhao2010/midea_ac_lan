import logging
from ...core.device import MiedaDevice
from .message import (
    MessageQuery,
    MessageSetNormal,
    MessageCCResponse
)
from enum import Enum

_LOGGER = logging.getLogger(__name__)


class DeviceProperties(Enum):
    power = "power"
    mode = "mode"
    target_temperature = "target_temperature"
    fan_speed = "fan_speed"

    eco_mode = "eco_mode"
    sleep_mode = "sleep_mode"
    night_light = "night_light"
    # ventilation = "ventilation"
    aux_heat = "aux_heat"
    swing = "swing"

    temperature_precision = "temperature_precision"
    fan_speed_level = "fan_speed_level"
    indoor_temperature = "indoor_temperature"

    aux_heat_status = "aux_heat_status"
    auto_aux_heat_running = "_auto_aux_heat_running"


class MideaCCDevice(MiedaDevice):
    def __init__(
            self,
            device_id: int,
            host: str,
            port: int,
            token: str,
            key: str,
            protocol: int,
            model: str
    ):
        super().__init__(
            device_id=device_id,
            device_type=0xCC,
            host=host,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._power = False
        self._mode = 1
        self._target_temperature = 26.0
        self._fan_speed = 0x80
        self._sleep_mode = False
        self._eco_mode = False
        self._night_light = False
        self._ventilation = False
        self._aux_heat_status = 0
        self._auto_aux_heat_running = False
        self._swing = False
        self._fan_speed_level = True
        self._indoor_temperature = 20.0
        self._temperature_precision = 1

    def build_query(self):
        return [MessageQuery()]

    def process_message(self, msg):
        message = MessageCCResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in DeviceProperties.__members__:
            if hasattr(message, status):
                setattr(self, "_" + status, getattr(message, status))
                new_status[status] = getattr(message, status)
        self._available = True
        new_status["available"] = True
        self.update_all(new_status)

    def make_message_set(self):
        message = MessageSetNormal()
        message.power = self.power
        message.mode = self.mode
        message.target_temperature = self.target_temperature
        message.fan_speed = self.fan_speed
        message.eco_mode = self.eco_mode
        message.sleep_mode = self.sleep_mode
        message.night_light = self.night_light
        message.ventilation = self.ventilation
        message.aux_heat_status = self._aux_heat_status
        message.auto_aux_heat_running = self._auto_aux_heat_running
        message.swing = self.swing
        return message

    @property
    def power(self):
        return self._power

    @power.setter
    def power(self, power):
        message = self.make_message_set()
        message.power = power
        self.build_send(message)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        message = self.make_message_set()
        message.power = True
        message.mode = mode
        self.build_send(message)

    @property
    def target_temperature(self):
        return self._target_temperature

    @target_temperature.setter
    def target_temperature(self, target_temperature):
        message = self.make_message_set()
        message.target_temperature = target_temperature
        self.build_send(message)

    def set_target_temperature(self, target_temperature, mode):
        message = self.make_message_set()
        message.target_temperature = target_temperature
        if mode is not None:
            message.power = True
            message.mode = mode
        self.build_send(message)

    @property
    def fan_speed(self):
        return self._fan_speed

    @fan_speed.setter
    def fan_speed(self, fan_speed):
        message = self.make_message_set()
        message.fan_speed = fan_speed
        self.build_send(message)

    @property
    def eco_mode(self):
        return self._eco_mode

    @eco_mode.setter
    def eco_mode(self, eco_mode):
        message = self.make_message_set()
        message.eco_mode = eco_mode
        if eco_mode:
            message.sleep_mode = False
        self.build_send(message)

    @property
    def sleep_mode(self):
        return self._sleep_mode

    @sleep_mode.setter
    def sleep_mode(self, sleep_mode):
        message = self.make_message_set()
        message.sleep_mode = sleep_mode
        if sleep_mode:
            message.eco_mode = False
        self.build_send(message)

    @property
    def night_light(self):
        return self._night_light

    @night_light.setter
    def night_light(self, night_light):
        message = self.make_message_set()
        message.night_light = night_light
        self.build_send(message)

    @property
    def ventilation(self):
        return self._ventilation

    @ventilation.setter
    def ventilation(self, ventilation):
        message = self.make_message_set()
        message.ventilation = ventilation
        self.build_send(message)

    @property
    def aux_heat(self):
        return self._aux_heat_status == 1 or self._auto_aux_heat_running

    @aux_heat.setter
    def aux_heat(self, aux_heat):
        message = self.make_message_set()
        if aux_heat:
            message.aux_heat_status = 1
        else:
            message.aux_heat_status = 2
        self.build_send(message)

    @property
    def swing(self):
        return self._swing

    @swing.setter
    def swing(self, swing):
        message = self.make_message_set()
        message.swing = swing
        self.build_send(message)

    @property
    def fan_speed_level(self):
        return self._fan_speed_level

    @property
    def temperature_precision(self):
        return self._temperature_precision

    @property
    def indoor_temperature(self):
        return self._indoor_temperature


class MideaAppliance(MideaCCDevice):
    pass
