# Air Conditioners
## Features
- Supports target temperature
- Supports run mode
- Supports fan mode
- Supports swing mode
- Supports preset mode
- Supports auxiliary heating

### Supported Run-Modes
- Comfort Mode
- ECO Mode
- Boost Mode

## Entities
### Default entity
EntityID | Class | Description
--- | --- | ---
climate.{DEVICEID}_climate | climate | Climate entity

### Extra entities

EntityID | Class | Description
--- | --- | ---
sensor.{DEVICEID}_full_dust | binary_sensor | Full of Dust
sensor.{DEVICEID}_indoor_humidity | sensor | Indoor humidity
sensor.{DEVICEID}_indoor_temperature | sensor | Indoor Temperature
sensor.{DEVICEID}_outdoor_temperature | sensor | Outdoor Temperature
sensor.{DEVICEID}_total_energy_consumption | sensor | Total Energy Consumption
sensor.{DEVICEID}_current_energy_consumption | sensor | Current Energy Consumption
sensor.{DEVICEID}_realtime_power | sensor | Realtime Power
switch.{DEVICEID}_aux_heat | switch | Aux Heating
switch.{DEVICEID}_boost_mode | switch | Boost Mode
switch.{DEVICEID}_breezeless | switch | Breezeless
switch.{DEVICEID}_comfort_mode | switch | Comfort Mode
switch.{DEVICEID}_dry | switch | Dry
switch.{DEVICEID}_eco_mode | switch | ECO Mode
switch.{DEVICEID}_indirect_wind | switch | Indirect Wind
switch.{DEVICEID}_natural_wind | switch | Natural Wind
switch.{DEVICEID}_prompt_tone | switch | Prompt Tone
switch.{DEVICEID}_power | switch | Power
switch.{DEVICEID}_screen_display | switch | Screen Display
switch.{DEVICEID}_screen_display_2 | switch | Screen Display (in new-protocol)
switch.{DEVICEID}_smart_eye | switch | Smart Eye
switch.{DEVICEID}_swing_horizontal | switch | Swing Horizontal
switch.{DEVICEID}_swing_vertical | switch | Swing Vertical


## Services
following extra services will be made

### midea_ac_lan.set_ac_fan_speed

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_ac_fan_speed)

Set fan speed of AC fan. Service data:

Name | Description
--- | ---
device_id | The Appliance code (Device ID) of appliance
fan_speed | Range 1 to 100 or auto

Example
```
service: midea_ac_lan.set_fan_speed
data:
  device_id: XXXXXXXXXXXX
  fan_speed: auto
```

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

Set the attribute of AC. Service data:

Name | Description
--- | ---
device_id | The Appliance code (Device ID) of appliance
attribute | "aux_heat"<br/>"breezeless"<br/>"comfort_mode"<br/>"dry"<br/>"eco_mode"<br/>"indirect_wind"<br/>"natural_wind"<br/>"prompt_tone"<br/>"power"<br/>"screen_display"<br/>"screen_display_2"<br/>"smart_eye"<br/>"swing_horizontal"<br/>"swing_vertical"<br/>"turbo_mode"
value | true or false

Example
```
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: eco_mode
  value: true
```