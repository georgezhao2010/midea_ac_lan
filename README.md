# Midea AC LAN
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![Donate](https://img.shields.io/badge/donate-BuyMeCoffee-yellow.svg)](https://www.buymeacoffee.com/georgezhao2010)
[![Stable](https://img.shields.io/github/v/release/georgezhao2010/midea_ac_lan)](https://github.com/georgezhao2010/midea_ac_lan/releases/latest)

English | [简体中文](README_hans.md)

Control your Midea devices via local area network.

- Automated device discover and configuration based HA config flow UI.
- Extra sensors and swithes.
- Synchronize status with the device by long TCP connection in time.

This component inspired from the repository at [@mac-zhou](https://github.com/mac-zhou/midea-msmart) which provides similar functionality for Midea air conditioners. This component include verbatim or adapted portions of the code from his great projects.

Thanks also to [@NeoAcheron](https://github.com/NeoAcheron/midea-ac-py).

# Supported Devices

 Name | Type | Documents
 --- | --- | ---
 Air Conditioners | AC | [AC.md](doc/AC.md)
 AC Control Panels | CC | [CC.md](doc/CC.md)
 Electric Water Heater | E2 | not supported yet

# Installtion
Search 'Midea AC LAN' in HACS and install, or copy all files in `custom_components/midea_ac_lan` from [Latest Release](https://github.com/georgezhao2010/midea_ac_lan/releases/latest) to your `/custom_components/midea_ac_lan` in Home Assistant manually. Restart HomeAssistant.

# Configuration
After installation, search anad add component Midea AC LAN in HomeAssistant integrations page,
If component can not found any devices, you can specify the IP address to add the device.

## Config automatically
This component could auto-discover and list Midea M-Smart AC devices in network, select one and add it in. You could repeat the above action to add multiple devices.

**Automatic configuration requires your air-conditioners and your Home Assistant must be in the same sub-network. Otherwise, devices cannot be auto-discovered.  Check this by yourself.**

## Config manually
If auto-discover could not work, you could add the device(s) manually with the following information.
- Device ID
- IP address
- Port (defualt 6444)
- Model (optional, default "unknown")
- Protocol version (2 or 3)
- Token
- Key

If ID/Token/key information was unknown, you could run the following commands in host.
```
pip3 install msmart
midea-discover
```

***msmart from [midea-msmart](https://github.com/mac-zhou/midea-msmart) of [@mac-zhou](https://github.com/mac-zhou)***

## Make attributes as sensors and switches

Only one main entity (e.g. climate entity) will be generated after configuration. If you want to make other attributes to extra sensor and switch entities, click CONFIGURE in Midea AC LAN integration card to choose (if your devices supported).

# Debug

Turn on the debug log out，config in configuration.yaml
```
logger:
  default: warn
  logs:
    custom_components.midea_ac_lan: debug
```
