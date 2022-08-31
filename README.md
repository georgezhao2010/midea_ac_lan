# Midea AC LAN
[![hacs_badge](https://img.shields.io/badge/HACS-Default-blue.svg)](https://github.com/hacs/integration)
[![Donate](https://img.shields.io/badge/donate-BuyMeCoffee-blue.svg)](https://www.buymeacoffee.com/georgezhao2010)
[![Stable](https://img.shields.io/github/v/release/georgezhao2010/midea_ac_lan)](https://github.com/georgezhao2010/midea_ac_lan/releases/latest)

English | [简体中文](https://github.com/georgezhao2010/midea_ac_lan/blob/master/README_hans.md)

Control your Midea M-Smart appliances via local area network.

- Automated device discover and configuration based HA config flow UI.
- Extra sensors and switches.
- Synchronize status with the appliance by long TCP connection in time.

This component inspired from the repository at [@mac-zhou](https://github.com/mac-zhou/midea-msmart) which provides similar functionality for Midea air conditioners. This component include verbatim or adapted portions of the code from his great projects.

Thanks also to [@NeoAcheron](https://github.com/NeoAcheron/midea-ac-py).

# Supported Appliances

  Type | Name | Documents
 --- | --- | ---
 AC | Air Conditioners | [AC.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/AC.md)
 CA | Refrigerators | [CA.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/CA.md)
 CC | MDV Wi-Fi Controllers | [CC.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/CC.md)
 CF | Heat Pumps | [CF.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/CF.md)
 DA | Top Load Washers | [DA.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/DA.md)
 DB | Front Load Washers | [DB.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/DB.md)
 DC | Clothes Dryers | [DC.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/DC.md)
 E1 | Dishwashers | [E1.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/E1.md)
 E2 | Electric Water Heaters | [E2.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/E2.md)
 E3 | Gas Water Heaters |  [E3.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/E3.md)

# Installation
Search 'Midea AC LAN' in HACS and install, or copy all files in `custom_components/midea_ac_lan` from [Latest Release](https://github.com/georgezhao2010/midea_ac_lan/releases/latest) to your `/custom_components/midea_ac_lan` in HomeAssistant manually. 

Restart HomeAssistant.

# Configuration
After installation, search and add component Midea AC LAN in HomeAssistant integrations page.

Or click [![Configuration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=midea_ac_lan)

## Config automatically
This component could auto-discover and list Midea M-Smart appliances in network, select one and add it in. You could repeat the above action to add multiple devices.

**Automatic configuration requires your appliances and your Home Assistant must be in the same sub-network. Otherwise, devices may not be auto-discovered.  Check this by yourself.**

## Config by IP
If auto-discover could not work, you could try to discover the appliance with the specified IP Address.

## Config manually
If you already know following information, you could add the appliance manually.
- Appliance code
- Appliance type (one of [Supported appliances](https://github.com/georgezhao2010/midea_ac_lan/blob/master/README.md#supported-appliances))
- IP address
- Port (default 6444)
- Protocol version
- Token
- Key


## Extra sensor and switch entities

Only one main entity (e.g. climate entity) will be generated after configuration. If you want to make the attributes to extra sensor and switch entities, click CONFIGURE in Midea AC LAN integration card to choose (if your devices supported).

# Debug

Turn on the debug log out，config in configuration.yaml
```
logger:
  default: warn
  logs:
    custom_components.midea_ac_lan: debug
```

# Helpful things
- [Lovelace simple thermostat card](https://github.com/nervetattoo/simple-thermostat)
- [Water Heater Card for Lovelace](https://github.com/rsnodgrass/water-heater-card)
