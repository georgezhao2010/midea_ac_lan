"""Tests for XC1MessageBody decoupled analysis methods."""
from custom_components.midea_ac_lan.midea.devices.ac.message import XC1MessageBody


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
