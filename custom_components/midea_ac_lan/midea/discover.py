import logging
import socket
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


def discover():
    security = Security()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError:
        # Will be raised when executed in Windows. Safe to ignore.
        pass
    sock.settimeout(5)
    found_devices = {}
    for i in range(2):
        try:
            sock.sendto(BROADCAST_MSG, ("255.255.255.255", 6445))
            sock.sendto(BROADCAST_MSG, ("255.255.255.255", 20086))
            while True:
                data, addr = sock.recvfrom(512)
                ip = addr[0]
                if len(data) >= 104 and (data[:2].hex() == "5a5a" or data[8:10].hex() == "5a5a"):
                    if data[:2].hex() == "5a5a":
                        protocol = 2
                    elif data[:2].hex() == "8370":
                        protocol = 3
                        if data[8:10].hex() == "5a5a":
                            data = data[8:-16]
                    else:
                        continue
                    device_id = int.from_bytes(bytes.fromhex(data[20:26].hex()), "little")
                    if device_id in found_devices:
                        continue
                    encrypt_data = data[40:-16]
                    reply = security.aes_decrypt(encrypt_data)
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
                if device_type.lower() != "ac":
                    continue
                device = {
                    "id": device_id,
                    "ip": ip,
                    "port": port,
                    "model": model,
                    "protocol": protocol
                }
                found_devices[device_id] = device

        except socket.timeout:
            continue
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
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(8)

    try:
        # Connect the Device
        device_address = (device_ip, device_port)
        sock.connect(device_address)

        # Send data
        _LOGGER.debug(f"Sending to {device_ip}:{device_port} {DEVICE_INFO_MSG.hex()}")
        sock.sendall(DEVICE_INFO_MSG)

        # Received data
        response = sock.recv(512)
    except socket.error:
        _LOGGER.info(f"Could't connect with Device {device_ip}:{device_port}")
        return bytearray(0)
    except socket.timeout:
        _LOGGER.info(f"Connect the device {device_ip}:{device_port} timed out for 8s. "
                     f"don't care about a small amount of this. if many maybe not support."
                     )
        return bytearray(0)
    finally:
        sock.close()
    _LOGGER.debug("Received from {}:{} {}".format(
        device_ip, device_port, response.hex()))
    return response
