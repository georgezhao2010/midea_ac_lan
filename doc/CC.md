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
switch.{DEVICEID}_aux_heat | switch | Aux Heating
switch.{DEVICEID}_eco_mode | switch | ECO Mode
switch.{DEVICEID}_night_light | switch | Night Light
switch.{DEVICEID}_sleep_mode | switch | Sleep Mode
switch.{DEVICEID}_swing | switch | Swing

## Service
following extra service will be made

### midea_ac_lan.set_attribute
Set the attribute of AC. Service data:

Name | Description
--- | ---
entity_id | The entity_id of cliamte entity.
attribute | "aux_heat"<br/>"eco_mode"<br/>"night_light"<br/>"sleep_mode"<br/>"swing"
value | true or false

Example
```
service: midea_ac_lan.set_attribute
data:
  entity_id: climate.XXXXXXXXXXXX_climate
  attribute: eco_mode
  value: true
```