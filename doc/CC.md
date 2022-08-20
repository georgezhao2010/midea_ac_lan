# AC Control Panels
## Features
- Supports target temperature
- Supports run mode
- Supports fan mode
- Supports swing mode
- Supports auxiliary heating

### Supported Run-Modes
- Sleep Mode
- ECO Mode

## Entities
### Default entity
EntityID | Class | Description
--- | --- | ---
climate.{DEVICEID}_climate | climate | Climate entity

### Extra entities

EntityID | Class | Description
--- | --- | ---
sensor.{DEVICEID}_indoor_humidity | sensor | Indoor humidity
switch.{DEVICEID}_aux_heat | switch | Aux Heating
switch.{DEVICEID}_eco_mode | switch | ECO Mode
switch.{DEVICEID}_night_light | switch | Night Light
switch.{DEVICEID}_power | switch | Power
switch.{DEVICEID}_sleep_mode | switch | Sleep Mode
switch.{DEVICEID}_swing | switch | Swing

## Service
following extra service will be made

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

Set the attribute of AC. Service data:

Name | Description
--- | ---
device_id | The Appliance code (Device ID) of appliance
attribute | "aux_heat"<br/>"eco_mode"<br/>"night_light"<br/>"power"<br />"sleep_mode"<br/>"swing"
value | true or false

Example
```
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: eco_mode
  value: true
```