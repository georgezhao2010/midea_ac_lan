# 燃气热水器
## 特性
- 支持温度设定

## 生成实体
### 默认生成实体
实体ID | 类型 | 描述
--- | --- | ---
water_heater.{DEVICEID}_water_heater | water_heater | 热水器实体

### 额外生成实体

EntityID | Class | Description | 描述
--- | --- | --- | --- 
binary_sensor.{DEVICEID}_burning_state | binary_sensor | Burning State | 燃烧状态
binary_sensor.{DEVICEID}_protection | binary_sensor | Protection | 安全防护
sensor.{DEVICEID}_current_temperature | sensor | Current Temperature | 温度
switch.{DEVICEID}_power | switch | Power | 电源开关
switch.{DEVICEID}_smart_volume | switch | Smart Volume | 智能变容
switch.{DEVICEID}_zero_cold_water | switch | Zero Cold Water | 零冷水
switch.{DEVICEID}_zero_cold_pulse | switch | Zero Cold Water (Pulse) | 零冷水(点动)

## 服务
生成以下扩展服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置热水器属性, 服务数据:

名称 | 描述
--- | ---
device_id | 设备的编号(Device ID)
attribute | "energy_saving"<br/>"power"<br />"smart_volume"<br/>"zero_cold_water"<br/>"zero_clod_pulse"
value | true or false

示例
```
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: smart_volume
  value: true
```