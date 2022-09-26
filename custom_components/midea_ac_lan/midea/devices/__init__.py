from importlib import import_module


def device_selector(
    name: str,
    device_id: int,
    device_type: int,
    ip_address: str,
    port: int,
    token: str,
    key: str,
    protocol: int,
    model: str,
    customize: str
):
    try:

        if device_type < 0xA0:
            device_path = f".{'x%02x' % device_type}.device"
        else:
            device_path = f".{'%02x' % device_type}.device"
        module = import_module(device_path, __package__)
        device = module.MideaAppliance(
            name=name,
            device_id=device_id,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            customize=customize
        )
    except ModuleNotFoundError:
        device = None
    return device
