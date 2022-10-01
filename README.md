# Midea AC LAN
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![Donate](https://img.shields.io/badge/donate-BuyMeCoffee-yellow.svg)](https://www.buymeacoffee.com/georgezhao2010)
[![Stable](https://img.shields.io/github/v/release/georgezhao2010/midea_ac_lan)](https://github.com/georgezhao2010/midea_ac_lan/releases/latest)

English | [简体中文](https://github.com/georgezhao2010/midea_ac_lan/blob/master/README_hans.md)

Control your Midea M-Smart appliances via local area network.

- Automated device discover and configuration based HA config flow UI.
- Extra sensors and switches.
- Synchronize status with the appliance by long TCP connection in time.

This component inspired from the repository at [@mac-zhou](https://github.com/mac-zhou/midea-msmart) which provides similar functionality for Midea air conditioners. This component include verbatim or adapted portions of the code from his great projects.

Thanks also to [@NeoAcheron](https://github.com/NeoAcheron/midea-ac-py).

***Note: HomeAssistant 2022.5 or higher requied for this integration***

# Supported brands

![beverly](https://github.com/georgezhao2010/midea_ac_lan/blob/master/brands/beverly.png) ![bugu](https://github.com/georgezhao2010/midea_ac_lan/blob/master/brands/bugu.png) ![carrier](https://github.com/georgezhao2010/midea_ac_lan/blob/master/brands/carrier.png)  ![colmo](https://github.com/georgezhao2010/midea_ac_lan/blob/master/brands/colmo.png) ![comfee](https://github.com/georgezhao2010/midea_ac_lan/blob/master/brands/comfee.png) ![electrolux](https://github.com/georgezhao2010/midea_ac_lan/blob/master/brands/electrolux.png) ![invertor](https://github.com/georgezhao2010/midea_ac_lan/blob/master/brands/invertor.png) ![littleswan](https://github.com/georgezhao2010/midea_ac_lan/blob/master/brands/littleswan.png) ![midea](https://github.com/georgezhao2010/midea_ac_lan/blob/master/brands/midea.png) ![netsu](https://github.com/georgezhao2010/midea_ac_lan/blob/master/brands/netsu.png) ![rotenso](https://github.com/georgezhao2010/midea_ac_lan/blob/master/brands/rotenso.png) ![toshiba](https://github.com/georgezhao2010/midea_ac_lan/blob/master/brands/toshiba.png) ![vandelo](https://github.com/georgezhao2010/midea_ac_lan/blob/master/brands/vandelo.png) ![wahin](https://github.com/georgezhao2010/midea_ac_lan/blob/master/brands/wahin.png)

And more.

# Supported appliances

  Type | Name | Documents
 --- | --- | ---
 A1 | Dehumidifier | [A1.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/A1.md)
 AC | Air Conditioner | [AC.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/AC.md)
 B6 | Range Hood | [B6.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/B6.md)
 C3 | Heat Pump Wi-Fi Controller | [C3.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/C3.md)
 CA | Refrigerator | [CA.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/CA.md)
 CC | MDV Wi-Fi Controller | [CC.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/CC.md)
 CE | Fresh Air Appliance | [CE.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/CE.md)
 CF | Heat Pump | [CF.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/CF.md)
 DA | Top Load Washer | [DA.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/DA.md)
 DB | Front Load Washer | [DB.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/DB.md)
 DC | Clothes Dryer | [DC.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/DC.md)
 E1 | Dishwasher | [E1.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/E1.md)
 E2 | Electric Water Heater | [E2.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/E2.md)
 E3 | Gas Water Heater | [E3.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/E3.md)
 EA | Electric Rice Cooker | [EA.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/EA.md)
 EC | Electric Pressure Cooker | [EC.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/EC.md)
 ED | Water Purifier | [ED.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/ED.md)
 FA | Fan | [FA.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/FA.md)
 FB | Electric Heater | [FB.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/FB.md)
 FC | Air Purifier | [FC.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/FC.md)
 FD | Humidifier | [FD.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/FD.md)

# Installation
Search 'Midea AC LAN' in HACS and install, or copy all files in `custom_components/midea_ac_lan` from [Latest Release](https://github.com/georgezhao2010/midea_ac_lan/releases/latest) to your `/custom_components/midea_ac_lan` in HomeAssistant manually. 

Restart HomeAssistant.

# Configuration
After installation, search and add component Midea AC LAN in HomeAssistant integrations page.

Or click [![Configuration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=midea_ac_lan)

## Config automatically
This component could auto-discover and list Midea M-Smart appliances in network, select one and add it in. You could repeat the above action to add multiple devices.

***Note: Automatic configuration requires your appliances and your Home Assistant must be in the same sub-network. Otherwise, devices may not be auto-discovered.  Check this by yourself.***

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

## Customize
Some appliance need more settings (like fan), your can set the customize parameters in JSON format, see the documentation of appliance get more information.

# Debug

Turn on the debug log out，config in configuration.yaml
```
logger:
  default: warn
  logs:
    custom_components.midea_ac_lan: debug
```