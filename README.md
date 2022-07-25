# Midea AC LAN
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![Donate](https://img.shields.io/badge/donate-BuyMeCoffee-yellow.svg)](https://www.buymeacoffee.com/georgezhao2010)
[![Stable](https://img.shields.io/github/v/release/georgezhao2010/midea_ac_lan)](https://github.com/georgezhao2010/midea_ac_lan/releases/latest)

English | [简体中文](https://github.com/georgezhao2010/midea_ac_lan/blob/master/README_hans.md)

Control your Midea air conditioners via local area network.

No extra python libs required.

This component inspired from the repository at [@mac-zhou](https://github.com/mac-zhou/midea-msmart) which provides similar functionality for Midea air conditioners. This component include verbatim or adapted portions of the code from his great projects.

Thanks also to [@NeoAcheron](https://github.com/NeoAcheron/midea-ac-py).

# Supported Devices
- Midea Air Conditioners (V2 or V3), type "AC"
- ~Midea Air Conditioner Control Panels, type "CC"~

# Installtion
Search 'Midea AC LAN' in HACS and install, or copy all files in `custom_components/midea_ac_lan` from [Latest Release](https://github.com/georgezhao2010/midea_ac_lan/releases/latest) to your `/custom_components/midea_ac_lan` in Home Assistant manually. Restart HomeAssistant.

# Configuration
After installation, search and add component Midea AC LAN in HomeAssistant integrations page,
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

Only one cliamate entity will be generated after configration. If you want to make the attributes of climate to extra sensor and switch entities, click CONFIGURE in Midea AC LAN integration card to choose (if your devices supported). All entities listed in [Extra entities](#extra-entities).

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

EntityID | Class | Memo
--- | --- | ---
sensor.{DEVICEID}_indoor_humidity | Sensor | Indoor humidity
switch.{DEVICEID}_indoor_temperature | Sensor | Indoor Temperature
switch.{DEVICEID}_outdoor_temperature | Sensor | Outdoor Temperature
switch.{DEVICEID}_aux_heat | Switches | Aux Heating
switch.{DEVICEID}_breezyless | Switches | Breezyless
switch.{DEVICEID}_comfort_mode | Switches | Comfort Mode
switch.{DEVICEID}_dry | Switches | Dry
switch.{DEVICEID}_eco_mode | Switches | ECO Mode
switch.{DEVICEID}_indirect_wind | Switches | Indirect Wind
switch.{DEVICEID}_natural_wind | Switches | Natural Wind
switch.{DEVICEID}_night_light | Switches | Night Light
switch.{DEVICEID}_prompt_tone | Switches | Prompt Tone
switch.{DEVICEID}_screen_display | Switches | Screen Display
switch.{DEVICEID}_smart_eye | Switches | Smart eye
switch.{DEVICEID}_swing_horizontal | Switches | Swing Horizontal
switch.{DEVICEID}_swing_vertical | Switches | Swing Vertical
switch.{DEVICEID}_turbo_mode | Switches | Turbo Mode

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
