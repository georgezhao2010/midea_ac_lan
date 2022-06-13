# Midea AC LAN
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

English | [简体中文](https://github.com/georgezhao2010/midea_ac_lan/blob/master/README_hans.md)

Control your Midea air conditioners via local area network.

This component inspired from the repository at [@mac-zhou](https://github.com/mac-zhou/midea-msmart) which provides similar functionality for Midea air conditioners. This component include verbatim or adapted portions of the code from his great projects.

Thanks also to [@NeoAcheron](https://github.com/NeoAcheron/midea-ac-py).

# Installtion
Use HACS and Install as a custom repository, or copy all files in `custom_components/midea_ac_lan` from [Latest Release](https://github.com/georgezhao2010/midea_ac_lan/releases/latest) to your `/custom_components/midea_ac_lan` in Home Assistant manually. Restart HomeAssistant.

# Configuration
After installation, search and add component Midea AC LAN in HomeAssistant integrations page,
If component can not found any devices, you can specify the IP address to add the device.

## Config automatically
This component could auto-discover and list Midea M-Smart AC devices in network, select one and add it in. You could repeat the above action to add multiple devices.

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

***msmart from [midea-msmart](https://github.com/mac-zhou/midea-msmart) of @mac-zhou (https://github.com/mac-zhou)***

## Make attributes as sensor and switch entities
If you selected this item, the following attributes would be made as sensor and switch entities and be displayed on HomeAssistant's frontend UI and easy use for Siri via HomeKit component.
- Sensor of outdoor temperature 
- Switch of comfort mode
- Switch of ECO mode
- Switch of indirect wind
- Switch of horizontal swing
- Switch of vertical swing
- Switch of prompt tone

# Features
## Climate features
- Supports target temperature
- Supports run mode
- Supports fan mode
- Supports swing mode
- Supports auxiliary heating

## Entities
### Default entity
EntityID | Class | Memo
--- | --- | ---
climate.{DEVICEID}_climate | climate | Climate entity

### Extra entities
If you selected `Make attributes as sensor and switch entities`, It will make following extra sensor and switch entitys

EntityID | Class | Memo
--- | --- | ---
sensor.{DEVICEID}_outdoor_temperature | sensor | Sensor of outdoor temperature
switch.{DEVICEID}_comfort_mode | switch | Switch of comfort mode
switch.{DEVICEID}_eco_mode | switch | Switch of ECO mode
switch.{DEVICEID}_indirect_wind | switch | Switch of indirect wind
switch.{DEVICEID}_swing_horizontal | switch | Switch of horizontal swing
switch.{DEVICEID}_swing_vertical | switch | Switch of vertical swing
switch.{DEVICEID}_prompt_tone | switch | Switch of prompt tone

## Sevices
following ectra services will be made

Services | Function | Params
--- | --- |--- 
midea_ac_lan.set_fan_speed | Set the fan speed | entity_id, fan_speed (range from 1 to 100 or "auto")
midea_ac_lan.set_comfort_mode | Turn on/off comfort mode | entity_id, comfort_mode (ture/false)
midea_ac_lan.set_eco_mode | Turn on/off ECO mode | entity_id, eco_mode (ture/false)
midea_ac_lan.set_indirect_wind | Turn on/off indirect wind | entity_id, indirect_wind (ture/false)
midea_ac_lan.set_prompt_tone | Turn on/off prompt tone | entity_id, prompt_tone (ture/false)

# Debug

Turn on the debug log out，config in configuration.yaml
```
logger:
  default: warn
  logs:
    custom_components.midea_ac_lan: debug
```



