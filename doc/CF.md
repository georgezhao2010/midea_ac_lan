# Heat Bump
## Features
- Supports target temperature
- Supports run mode

## Entities
### Default entity
| EntityID                   | Class   | Description    |
|----------------------------|---------|----------------|
| climate.{DEVICEID}_climate | climate | Climate entity |

### Extra entities

| EntityID                              | Class  | Description         |
|---------------------------------------|--------|---------------------|
| sensor.{DEVICEID}_current_temperature | sensor | Current Temperature |
| switch.{DEVICEID}_power               | switch | Power               |

## Service


### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                 |
|-----------|---------------------------------------------|
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "power"                   |
| value     | true or false                               |

