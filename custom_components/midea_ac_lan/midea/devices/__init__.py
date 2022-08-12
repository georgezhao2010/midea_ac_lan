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
    model: str
):
    try:
        module = import_module(f".{'%02x' % device_type}.device", __package__)
        device = module.MideaAppliance(
            name=name,
            device_id=device_id,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
    except ModuleNotFoundError:
        device = None
    return device
