# Heat Pump Water Heater

## Features
- Supports target temperature

## Customize

Set the temperature step of water heater (1 by default).

```
{"temperature_step": 0.5}
```

## Entities
### Default entity
| EntityID                             | Class        | Description         |
|--------------------------------------|--------------|---------------------|
| water_heater.{DEVICEID}_water_heater | water_heater | Water heater entity |

### Extra entities

| EntityID                                     | Class             | Description            |
|----------------------------------------------|-------------------|------------------------|
| sensor.{DEVICEID}_compressor_temperature     | sensor            | Compressor Temperature |
| sensor.{DEVICEID}_condenser_temperature      | sensor            | Condenser Temperature  |
| sensor.{DEVICEID}_outdoor_temperature        | sensor            | Outdoor Temperature    |
| binary_sensor.{DEVICEID}_outdoor_temperature | compressor_status | Compressor Status      |
| switch.{DEVICEID}_power                      | switch            | Power                  |
| switch.{DEVICEID}_aux_heating                | switch            | Aux Heating            |

## Services
following extra service will be made

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                 |
|-----------|---------------------------------------------|
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "power"</br>"aux_heating"                   |
| value     | true or false                               |

Example
```
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: false
```