import logging
from ...core.device import MiedaDevice

_LOGGER = logging.getLogger(__name__)


class MideaCCDevice(MiedaDevice):
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
        self._temp_fahrenheit = temp_fahrenheit

    def build_query(self):
        raise NotImplementedError

    def process_message(self, msg):
        raise NotImplementedError
