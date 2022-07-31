# 功能
## 支持的温控器操作
- 支持目标温度设定
- 支持运行模式设定
- 支持风扇模式设定
- 支持摆风模式设定
- 支持电辅热

## 生成实体
### 默认生成实体
实体ID | 类型 | 描述
--- | --- | ---
climate.{DEVICEID}_climate | Climate | 恒温器实体

### 额外生成实体

EntityID | 类型 | 名称 | 描述
--- | --- | --- | --- 
sensor.{DEVICEID}_indoor_temperature | Sensor | Indoor Temperature | 室内温度
switch.{DEVICEID}_aux_heat | Switch | Aux Heating | 电辅热
switch.{DEVICEID}_eco_mode | Switch | ECO Mode | ECO模式
switch.{DEVICEID}_night_light | Switch | Night Light | 夜灯
switch.{DEVICEID}_sleep_mode | Switch | Sleep Mode | 睡眠模式
switch.{DEVICEID}_swing | Switch | Swing | 垂直摆风

## 服务
生成以下扩展服务

### midea_ac_lan.set_attribute
设置空调属性, 服务数据:

名称 | 描述
--- | ---
entity_id | The entity_id of cliamte entity.
attribute | "aux_heat"<br/>"eco_mode"<br/>"night_light"<br/>"sleep_mode"<br/>"swing"
value | true or false

示例
```
service: midea_ac_lan.set_attribute
data:
  entity_id: climate.XXXXXXXXXXXX_climate
  attribute: eco_mode
  value: true
```