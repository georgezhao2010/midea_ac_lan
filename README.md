# Midea AC LAN
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![Donate](https://img.shields.io/badge/donate-BuyMeCoffee-yellow.svg)](https://www.buymeacoffee.com/georgezhao2010)
[![Stable](https://img.shields.io/github/v/release/georgezhao2010/midea_ac_lan)](https://github.com/georgezhao2010/midea_ac_lan/releases/latest)

English | [简体中文](README_hans.md)

Control your Midea M-Smart appliances via local area network.

- Automated device discover and configuration based Home Assistant config flow UI.
- Extra sensors and switches.
- Synchronize status with the appliance by long TCP connection in time.

This component inspired from the repository at [@mac-zhou](https://github.com/mac-zhou/midea-msmart) which provides similar functionality for Midea air conditioners. This component include verbatim or adapted portions of the code from his great projects.

Thanks also to [@NeoAcheron](https://github.com/NeoAcheron/midea-ac-py).

***Note: Home Assistant 2022.5 or higher requied for this integration***

# Supported brands

![beverly](brands/beverly.png) ![bugu](brands/bugu.png) ![carrier](brands/carrier.png)  ![colmo](brands/colmo.png) ![comfee](brands/comfee.png) ![electrolux](brands/electrolux.png) ![invertor](brands/invertor.png) ![littleswan](brands/littleswan.png) ![midea](brands/midea.png) ![netsu](brands/netsu.png) ![ProBreeze](brands/probreeze.png) ![rotenso](brands/rotenso.png) ![toshiba](brands/toshiba.png) ![vandelo](brands/vandelo.png) ![wahin](brands/wahin.png) 

And more.

# Supported appliances

  Type | Name | Documents
 --- | --- | ---
 A1 | Dehumidifier | [A1.md](doc/A1.md)
 AC | Air Conditioner | [AC.md](doc/AC.md)
 B0 | Microwave Oven | [B0.md](doc/B0.md)
 B1 | Electric Oven | [B1.md](doc/B1.md)
 B6 | Range Hood | [B6.md](doc/B6.md)
 C3 | Heat Pump Wi-Fi Controller | [C3.md](doc/C3.md)
 CA | Refrigerator | [CA.md](doc/CA.md)
 CC | MDV Wi-Fi Controller | [CC.md](doc/CC.md)
 CE | Fresh Air Appliance | [CE.md](doc/CE.md)
 CF | Heat Pump | [CF.md](doc/CF.md)
 DA | Top Load Washer | [DA.md](doc/DA.md)
 DB | Front Load Washer | [DB.md](doc/DB.md)
 DC | Clothes Dryer | [DC.md](doc/DC.md)
 E1 | Dishwasher | [E1.md](doc/E1.md)
 E2 | Electric Water Heater | [E2.md](doc/E2.md)
 E3 | Gas Water Heater | [E3.md](doc/E3.md)
 EA | Electric Rice Cooker | [EA.md](doc/EA.md)
 EC | Electric Pressure Cooker | [EC.md](doc/EC.md)
 ED | Water Drinking Appliance | [ED.md](doc/ED.md)
 FA | Fan | [FA.md](doc/FA.md)
 FB | Electric Heater | [FB.md](doc/FB.md)
 FC | Air Purifier | [FC.md](doc/FC.md)
 FD | Humidifier | [FD.md](doc/FD.md)
 x34 | Sink Dishwasher | [x34.md](doc/x34.md)

# Installation
Search 'Midea AC LAN' in HACS and install, or copy all files in `custom_components/midea_ac_lan` from [Latest Release](https://github.com/georgezhao2010/midea_ac_lan/releases/latest) to your `/custom_components/midea_ac_lan` in Home Assistant manually. 

Restart Home Assistant.

# Configuration
***Note: First, set a static IP address for your appliance in the router, in case the IP address of the appliance changes after set-up.***

After installation, search and add component Midea AC LAN in Home Assistant integrations page.

Or click [![Configuration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=midea_ac_lan)

## Config automatically
This component could auto-discover and list Midea M-Smart appliances in network, select one and add it in. You could repeat the above action to add multiple devices.

***Note: Automatic configuration requires your appliances and your Home Assistant must be in the same sub-network. Otherwise, devices may not be auto-discovered.  Check this by yourself.***

## Config by IP
If auto-discover could not work, you could try to discover the appliance with the specified IP Address.

## Config manually
If you already know following information, you could add the appliance manually.
- Appliance code
- Appliance type (one of [Supported appliances](README.md#supported-appliances))
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

# Support my works 

If you like this integration, why do not you support my works by buying me a coffee?

[![Buy me a coffee](https://www.buymeacoffee.com/assets/img/custom_images/yellow_img.png)](https://www.buymeacoffee.com/georgezhao2010)