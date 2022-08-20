import logging
import socket
import ifaddr
from ipaddress import IPv4Network
from .security import Security
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

_LOGGER = logging.getLogger(__name__)

BROADCAST_MSG = bytearray([
    0x5a, 0x5a, 0x01, 0x11, 0x48, 0x00, 0x92, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x7f, 0x75, 0xbd, 0x6b, 0x3e, 0x4f, 0x8b, 0x76,
    0x2e, 0x84, 0x9c, 0x6e, 0x57, 0x8d, 0x65, 0x90,
    0x03, 0x6e, 0x9d, 0x43, 0x42, 0xa5, 0x0f, 0x1f,
    0x56, 0x9e, 0xb8, 0xec, 0x91, 0x8e, 0x92, 0xe5
])

DEVICE_INFO_MSG = bytearray([
    0x5a, 0x5a, 0x15, 0x00, 0x00, 0x38, 0x00, 0x04,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x27, 0x33, 0x05,
    0x13, 0x06, 0x14, 0x14, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x03, 0xe8, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0xca, 0x8d, 0x9b, 0xf9, 0xa0, 0x30, 0x1a, 0xe3,
    0xb7, 0xe4, 0x2d, 0x53, 0x49, 0x47, 0x62, 0xbe
])


def discover(discover_type=None, ip_address=None):
    if discover_type is None:
        discover_type = []
    security = Security()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)
    found_devices = {}
    if ip_address is None:
        addrs = enum_all_broadcast()
    else:
        addrs = [ip_address]

    for addr in addrs:
        sock.sendto(BROADCAST_MSG, (addr, 6445))
        sock.sendto(BROADCAST_MSG, (addr, 20086))
    while True:
        try:
            data, addr = sock.recvfrom(512)
            ip = addr[0]
            _LOGGER.debug(f"Received broadcast from {addr}: {data.hex()}")
            if len(data) >= 104 and (data[:2].hex() == "5a5a" or data[8:10].hex() == "5a5a"):
                if data[:2].hex() == "5a5a":
                    protocol = 2
                elif data[:2].hex() == "8370":
                    protocol = 3
                    if data[8:10].hex() == "5a5a":
                        data = data[8:-16]
                else:
                    continue
                device_id = int.from_bytes(bytearray.fromhex(data[20:26].hex()), "little")
                if device_id in found_devices:
                    continue
                encrypt_data = data[40:-16]
                reply = security.aes_decrypt(encrypt_data)
                _LOGGER.debug(f"Declassified reply: {reply.hex()}")
                ssid = reply[41:41 + reply[40]].decode("utf-8")
                device_type = ssid.split("_")[1]
                port = bytes2port(reply[4:8])
                model = reply[20:25].decode("utf-8")
            elif data[:6].hex() == "3c3f786d6c20":
                protocol = 1
                root = ET.fromstring(data.decode(
                    encoding="utf-8", errors="replace"))
                child = root.find("body/device")
                m = child.attrib
                port, sn, device_type = int(m["port"]), m["apc_sn"], str(
                    hex(int(m["apc_type"])))[2:]
                response = get_device_info(ip, int(port))
                device_id = get_id_from_response(response)
                if len(sn) == 32:
                    model = sn[12:17]
                elif len(sn) == 22:
                    model = sn[6:11]
                else:
                    model = ""
            else:
                continue
            device = {
                "device_id": device_id,
                "type": int(device_type, 16),
                "ip_address": ip,
                "port": port,
                "model": model,
                "protocol": protocol
            }
            if len(discover_type) == 0 or device.get("type") in discover_type:
                found_devices[device_id] = device
                _LOGGER.debug(f"Found a supported device: {device}")
            else:
                _LOGGER.debug(f"Found a unsupported device: {device}")
        except socket.timeout:
            break
        except socket.error:
            pass
    return found_devices


def get_id_from_response(response):
    if response[64:-16][:6].hex() == "3c3f786d6c20":
        xml = response[64:-16]
        root = ET.fromstring(xml.decode(encoding="utf-8", errors="replace"))
        child = root.find("smartDevice")
        m = child.attrib
        return int.from_bytes(bytearray.fromhex(m["devId"]), "little")
    else:
        return 0


def bytes2port(paramArrayOfbyte):
    if paramArrayOfbyte is None:
        return 0
    b, i = 0, 0
    while b < 4:
        if b < len(paramArrayOfbyte):
            b1 = paramArrayOfbyte[b] & 0xFF
        else:
            b1 = 0
        i |= b1 << b * 8
        b += 1
    return i


def get_device_info(device_ip, device_port: int):
    response = bytearray(0)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(8)
            device_address = (device_ip, device_port)
            sock.connect(device_address)
            _LOGGER.debug(f"Sending to {device_ip}:{device_port} {DEVICE_INFO_MSG.hex()}")
            sock.sendall(DEVICE_INFO_MSG)
            response = sock.recv(512)
    except socket.timeout:
        _LOGGER.warning(f"Connect the device {device_ip}:{device_port} timed out for 8s. "
                        f"Don't care about a small amount of this. if many maybe not support."
                        )
    except socket.error:
        _LOGGER.warning(f"Can't connect to Device {device_ip}:{device_port}")
    return response


def enum_all_broadcast():
    nets = []
    adapters = ifaddr.get_adapters()
    for adapter in adapters:
        for ip in adapter.ips:
            if ip.is_IPv4 and ip.network_prefix < 32:
                localNet = IPv4Network(f"{ip.ip}/{ip.network_prefix}", strict=False)
                if localNet.is_private and not localNet.is_loopback and not localNet.is_link_local:
                    nets.append(str(localNet.broadcast_address))
    return nets
