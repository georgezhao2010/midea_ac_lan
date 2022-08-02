# Features
## Climate features
- Supports target temperature
- Supports run mode
- Supports fan mode
- Supports swing mode
- Supports preset mode
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
switch.{DEVICEID}_boost_mode | switch | Boost Mode
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


## Services
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