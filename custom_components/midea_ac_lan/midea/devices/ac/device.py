import logging
from .message import (
    MessageQuery,
    MessageNewProtocolQuery,
    MessageACResponse,
    MessageGeneralSet,
    MessageNewProtocolSet
)
from ...core.device import MiedaDevice
from enum import Enum

_LOGGER = logging.getLogger(__name__)


class DeviceProperties(Enum):
    power = "power"
    mode = "mode"
    target_temperature = "target_temperature"
    fan_speed = "fan_speed"

    swing_vertical = "swing_vertical"
    swing_horizontal = "swing_horizontal"
    strong_mode = "strong_mode"
    smart_eye = "smart_eye"
    dry = "dry"
    eco_mode = "eco_mode"
    aux_heat = "aux_heat"
    sleep_mode = "sleep_mode"
    turbo_mode = "turbo_mode"
    night_light = "night_light"
    natural_wind = "natural_wind"
    temp_fahrenheit = "temp_fahrenheit"
    comfort_mode = "comfort_mode"

    indoor_temperature = "indoor_temperature"
    outdoor_temperature = "outdoor_temperature"

    indirect_wind = "indirect_wind"
    indoor_humidity = "indoor_humidity"
    breezyless = "breezyless"


class MideaACDevice(MiedaDevice):
    def __init__(self,
                 device_id: int,
                 device_type: int,
                 host: str,
                 port: int,
                 token: str,
                 key: str,
                 protocol: int,
                 model: str,
                 temp_fahrenheit):
        super().__init__(device_id=device_id,
                         device_type=device_type,
                         host=host,
                         port=port,
                         token=token,
                         key=key,
                         protocol=protocol,
                         model=model)

        self._prompt_tone = True
        self._power = False
        self._mode = 0
        self._target_temperature = 20.0
        self._fan_speed = 102
        self._swing_vertical = False
        self._swing_horizontal = False
        self._strong_mode = False
        self._smart_eye = False
        self._dry = False
        self._eco_mode = False
        self._aux_heat = False
        self._sleep_mode = False
        self._turbo_mode = False
        self._night_light = False
        self._natural_wind = False
        self._temp_fahrenheit = temp_fahrenheit
        self._indoor_temperature = 0.0
        self._outdoor_temperature = 0.0
        self._breezyless = False
        self._indoor_humidity = 0.0
        self._indirect_wind = False
        self._comfort_mode = False

    def build_query(self):
        return [MessageQuery(), MessageNewProtocolQuery()]

    def process_message(self, msg):
        message = MessageACResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in DeviceProperties.__members__:
            if hasattr(message, status):
                setattr(self, "_" + status, getattr(message, status))
                new_status[status] = getattr(message, status)
        if ("power" in new_status and not self._power) or \
                ("swing_vertical" in new_status and self._swing_vertical):
            self._indirect_wind = False
            new_status["indirect_wind"] = False
        self._available = True
        new_status["available"] = True
        _LOGGER.debug(f"[{self._device_id}] Status update: {new_status}")
        self.update_all(new_status)

    def make_message_set(self):
        message = MessageGeneralSet()
        message.power = self.power
        message.prompt_tone = self.prompt_tone
        message.mode = self.mode
        message.target_temperature = self.target_temperature
        message.fan_speed = self.fan_speed
        message.swing_vertical = self.swing_vertical
        message.swing_horizontal = self.swing_horizontal
        message.strong_mode = self._strong_mode
        message.smart_eye = self._smart_eye
        message.dry = self._dry
        message.eco_mode = self.eco_mode
        message.aux_heat = self.aux_heat
        message.sleep_mode = self._sleep_mode
        message.turbo_mode = self._turbo_mode
        message.night_light = self._night_light
        message.natural_wind = self._natural_wind
        message.temp_fahrenheit = self.temp_fahrenheit
        # message.lcd_display = True
        message.comfort_mode = self.comfort_mode
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
    def prompt_tone(self):
        return self._prompt_tone

    @prompt_tone.setter
    def prompt_tone(self, prompt_tone):
        self._prompt_tone = prompt_tone
        self.update_all({"prompt_tone": prompt_tone})

    @property
    def swing_vertical(self):
        return self._swing_vertical

    @swing_vertical.setter
    def swing_vertical(self, swing_vertical):
        message = self.make_message_set()
        message.swing_vertical = swing_vertical
        self.build_send(message)

    @property
    def swing_horizontal(self):
        return self._swing_horizontal

    @swing_horizontal.setter
    def swing_horizontal(self, swing_horizontal):
        message = self.make_message_set()
        message.swing_horizontal = swing_horizontal
        self.build_send(message)

    def set_swing(self, swing_vertical, swing_horizontal):
        message = self.make_message_set()
        message.swing_vertical = swing_vertical
        message.swing_horizontal = swing_horizontal
        self.build_send(message)

    @property
    def strong_mode(self):
        return self._strong_mode

    @strong_mode.setter
    def strong_mode(self, strong_mode):
        message = self.make_message_set()
        message.strong_mode = strong_mode
        self.build_send(message)

    @property
    def smart_eye(self):
        return self._smart_eye

    @smart_eye.setter
    def smart_eye(self, smart_eye):
        message = self.make_message_set()
        message.smart_eye = smart_eye
        self.build_send(message)

    @property
    def dry(self):
        return self._dry

    @dry.setter
    def dry(self, dry):
        message = self.make_message_set()
        message.dry = dry
        self.build_send(message)

    @property
    def eco_mode(self):
        return self._eco_mode

    @eco_mode.setter
    def eco_mode(self, eco_mode):
        message = self.make_message_set()
        message.eco_mode = eco_mode
        self.build_send(message)

    @property
    def aux_heat(self):
        return self._aux_heat

    @aux_heat.setter
    def aux_heat(self, aux_heat):
        message = self.make_message_set()
        message.aux_heat = aux_heat
        self.build_send(message)

    @property
    def sleep_mode(self):
        return self._sleep_mode

    @sleep_mode.setter
    def sleep_mode(self, sleep_mode):
        message = self.make_message_set()
        message.sleep_mode = sleep_mode
        self.build_send(message)

    @property
    def turbo_mode(self):
        return self._turbo_mode

    @turbo_mode.setter
    def turbo_mode(self, turbo_mode):
        message = self.make_message_set()
        message.turbo_mode = turbo_mode
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
    def natural_wind(self):
        return self._natural_wind

    @natural_wind.setter
    def natural_wind(self, natural_wind):
        message = self.make_message_set()
        message.natural_wind = natural_wind
        self.build_send(message)

    @property
    def temp_fahrenheit(self):
        return self._temp_fahrenheit

    @property
    def comfort_mode(self):
        return self._comfort_mode

    @comfort_mode.setter
    def comfort_mode(self, comfort_mode):
        message = self.make_message_set()
        message.comfort_mode = comfort_mode
        self.build_send(message)

    @property
    def indoor_temperature(self):
        return self._indoor_temperature

    @property
    def outdoor_temperature(self):
        return self._outdoor_temperature

    @property
    def indirect_wind(self):
        return self._indirect_wind

    @indirect_wind.setter
    def indirect_wind(self, indirect_wind):
        message = MessageNewProtocolSet()
        message.indirect_wind = indirect_wind
        message.prompt_tone = self.prompt_tone
        self.build_send(message)

    @property
    def breezyless(self):
        return self._breezyless

    @breezyless.setter
    def breezyless(self, breezyless):
        message = MessageNewProtocolSet()
        message.breezyless = breezyless
        message.prompt_tone = self.prompt_tone
        self.build_send(message)

    @property
    def indoor_humidity(self):
        return self._breezyless

    @property
    def attributes(self):
        ret = {}
        for status in DeviceProperties.__members__:
            if hasattr(self, status):
                ret[status] = getattr(self, status)

        return ret
