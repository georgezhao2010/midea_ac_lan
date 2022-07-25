# Midea AC LAN
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![Donate](https://img.shields.io/badge/donate-BuyMeCoffee-yellow.svg)](https://www.buymeacoffee.com/georgezhao2010)
[![Stable](https://img.shields.io/github/v/release/georgezhao2010/midea_ac_lan)](https://github.com/georgezhao2010/midea_ac_lan/releases/latest)

English | [简体中文](README_hans.md)

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
EntityID | Class | Description
--- | --- | ---
climate.{DEVICEID}_climate | Climate | Climate entity

### Extra entities

EntityID | Class | Description
--- | --- | ---
sensor.{DEVICEID}_indoor_humidity | Sensor | Indoor humidity
sensor.{DEVICEID}_indoor_temperature | Sensor | Indoor Temperature
sensor.{DEVICEID}_outdoor_temperature | Sensor | Outdoor Temperature
switch.{DEVICEID}_aux_heat | switch | Aux Heating
switch.{DEVICEID}_breezyless | switch | Breezyless
switch.{DEVICEID}_comfort_mode | switch | Comfort Mode
switch.{DEVICEID}_dry | switch | Dry
switch.{DEVICEID}_eco_mode | switch | ECO Mode
switch.{DEVICEID}_indirect_wind | switch | Indirect Wind
switch.{DEVICEID}_natural_wind | switch | Natural Wind
switch.{DEVICEID}_night_light | switch | Night Light
switch.{DEVICEID}_prompt_tone | switch | Prompt Tone
switch.{DEVICEID}_screen_display | switch | Screen Display
switch.{DEVICEID}_smart_eye | switch | Smart eye
switch.{DEVICEID}_swing_horizontal | switch | Swing Horizontal
switch.{DEVICEID}_swing_vertical | switch | Swing Vertical
switch.{DEVICEID}_turbo_mode | switch | Turbo Mode

## Sevices
following extra services will be made

### midea_ac_lan.set_fan_speed
Set fan speed of AC fan. Service data:
Name | Description
--- | ---
entity_id | The entity_id of cliamte entity.
fan_speed | Range 1 to 100 or auto

Example
```
service: midea_ac_lan.set_fan_speed
data:
  entity_id: climate.XXXXXXXXXXXX_climate
  fan_speed: auto
```

### midea_ac_lan.set_attribute
Set the attribute of AC. Service data:
Name | Description
--- | ---
entity_id | The entity_id of cliamte entity.
attribute | "aux_heat"<br/>"breezyless"<br/>"comfort_mode"<br/>"dry"<br/>"eco_mode"<br/>"indirect_wind"<br/>"natural_wind"<br/>"night_light"<br/>"prompt_tone"<br/>"screen_display"<br/>"smart_eye"<br/>"swing_horizontal"<br/>"swing_vertical"<br/>"turbo_mode"
value | true or false

Example
```
service: midea_ac_lan.set_attribute
data:
  entity_id: climate.XXXXXXXXXXXX_climate
  attribute: eco_mode
  value: true
```

# Debug

Turn on the debug log out，config in configuration.yaml
```
logger:
  default: warn
  logs:
    custom_components.midea_ac_lan: debug
```
