"""Tests for XC1MessageBody decoupled analysis methods."""
import sys
import os
import importlib.util
import types

_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_midea = os.path.join(_root, "custom_components", "midea_ac_lan", "midea")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# Load dependencies in order
_crc8 = _load("_midea_crc8", os.path.join(_midea, "core", "crc8.py"))
_core = _load("_midea_core_msg", os.path.join(_midea, "core", "message.py"))

# Build a thin fake package so relative imports inside ac/message.py resolve
_pkg_midea = types.ModuleType("_midea_pkg")
_pkg_midea_core = types.ModuleType("_midea_pkg.core")
_pkg_midea_core.message = _core
_pkg_midea_core.crc8 = _crc8
for _attr in dir(_core):
    setattr(_pkg_midea_core, _attr, getattr(_core, _attr))
_pkg_midea.core = _pkg_midea_core
sys.modules["_midea_pkg"] = _pkg_midea
sys.modules["_midea_pkg.core"] = _pkg_midea_core
sys.modules["_midea_pkg.core.message"] = _core
sys.modules["_midea_pkg.core.crc8"] = _crc8

# Read ac/message.py source and replace relative imports
_ac_path = os.path.join(_midea, "devices", "ac", "message.py")
with open(_ac_path) as _f:
    _src = _f.read()
_src = _src.replace("from ...core.message import", "from _midea_pkg.core.message import")
_src = _src.replace("from ...core.crc8 import", "from _midea_pkg.core.crc8 import")

_ac_mod = types.ModuleType("_midea_ac_message")
exec(compile(_src, _ac_path, "exec"), _ac_mod.__dict__)
XC1MessageBody = _ac_mod.XC1MessageBody


def _make_body(total_bytes, current_bytes, power_bytes):
    body = bytearray(20)
    body[3] = 0x44
    body[4], body[5], body[6], body[7] = total_bytes
    body[12], body[13], body[14], body[15] = current_bytes
    body[16], body[17], body[18] = power_bytes
    return bytes(body)


class TestXC1MessageBodyLegacy:
    def test_legacy_default_method3(self):
        body = _make_body((0x01, 0x02, 0x03, 0x04), (0x05, 0x06, 0x07, 0x08), (0x0A, 0x0B, 0x0C))
        msg = XC1MessageBody(body)
        assert msg.total_energy_consumption == float(1 * 1000000 + 2 * 10000 + 3 * 100 + 4) / 100
        assert msg.current_energy_consumption == float(5 * 1000000 + 6 * 10000 + 7 * 100 + 8) / 100
        assert msg.realtime_power == float(10 * 10000 + 11 * 100 + 12) / 10

    def test_legacy_explicit_single_method(self):
        body = _make_body((0x01, 0x02, 0x03, 0x04), (0x05, 0x06, 0x07, 0x08), (0x0A, 0x0B, 0x0C))
        msg = XC1MessageBody(body, power_analysis_method=2)
        assert msg.total_energy_consumption == float((1 << 32) + (2 << 16) + (3 << 8) + 4) / 10
        assert msg.realtime_power == float((10 << 16) + (11 << 8) + 12) / 10


class TestXC1MessageBodySeparateMethods:
    def test_power2_consumption3(self):
        body = _make_body((0x01, 0x02, 0x03, 0x04), (0x05, 0x06, 0x07, 0x08), (0x0A, 0x0B, 0x0C))
        msg = XC1MessageBody(body, power_analysis_method=2, consumption_analysis_method=3)
        assert msg.total_energy_consumption == float(1 * 1000000 + 2 * 10000 + 3 * 100 + 4) / 100
        assert msg.current_energy_consumption == float(5 * 1000000 + 6 * 10000 + 7 * 100 + 8) / 100
        assert msg.realtime_power == float((10 << 16) + (11 << 8) + 12) / 10

    def test_power3_consumption2(self):
        body = _make_body((0x01, 0x02, 0x03, 0x04), (0x05, 0x06, 0x07, 0x08), (0x0A, 0x0B, 0x0C))
        msg = XC1MessageBody(body, power_analysis_method=3, consumption_analysis_method=2)
        assert msg.total_energy_consumption == float((1 << 32) + (2 << 16) + (3 << 8) + 4) / 10
        assert msg.realtime_power == float(10 * 10000 + 11 * 100 + 12) / 10

    def test_consumption_none_inherits_power_method(self):
        body = _make_body((0x01, 0x02, 0x03, 0x04), (0x05, 0x06, 0x07, 0x08), (0x0A, 0x0B, 0x0C))
        msg_none = XC1MessageBody(body, power_analysis_method=2, consumption_analysis_method=None)
        msg_legacy = XC1MessageBody(body, power_analysis_method=2)
        assert msg_none.total_energy_consumption == msg_legacy.total_energy_consumption
        assert msg_none.realtime_power == msg_legacy.realtime_power
