# 功能
## 支持的温控器操作
- 支持目标温度设定
- 支持运行模式设定
- 支持风扇模式设定
- 支持摆风模式设定
- 支持预设模式设定
- 支持电辅热

## 生成实体
### 默认生成实体
实体ID | 类型 | 描述
--- | --- | ---
climate.{DEVICEID}_climate | Climate | 恒温器实体

### 额外生成实体

EntityID | 类型 | 名称 | 描述
--- | --- | --- | --- 
sensor.{DEVICEID}_indoor_humidity | Sensor | Indoor humidity | 湿度
sensor.{DEVICEID}_indoor_temperature | Sensor | Indoor Temperature | 室内温度
sensor.{DEVICEID}_outdoor_temperature | Sensor | Outdoor Temperature | 室外机温度
switch.{DEVICEID}_aux_heat | Switch | Aux Heating | 电辅热
switch.{DEVICEID}_boost_mode | Switch | Boost Mode | 强劲模式
switch.{DEVICEID}_breezyless | Switch | Breezyless | 无风感
switch.{DEVICEID}_comfort_mode | Switch | Comfort Mode | 舒省模式
switch.{DEVICEID}_dry | Switch | Dry | 干燥
switch.{DEVICEID}_eco_mode | Switch | ECO Mode | ECO模式
switch.{DEVICEID}_indirect_wind | Switch | Indirect Wind | 防直吹
switch.{DEVICEID}_natural_wind | Switch | Natural Wind | 自然风
switch.{DEVICEID}_night_light | Switch | Night Light | 夜灯
switch.{DEVICEID}_prompt_tone | Switch | Prompt Tone | 提示音
switch.{DEVICEID}_screen_display | Switch | Screen Display | 屏幕显示
switch.{DEVICEID}_smart_eye | Switch | Smart eye | 智慧眼
switch.{DEVICEID}_swing_horizontal | Switch | Swing Horizontal | 水平摆风
switch.{DEVICEID}_swing_vertical | Switch | Swing Vertical | 垂直摆风

## 服务
生成以下扩展服务

### midea_ac_lan.set_fan_speed
设置空调风速, 服务数据:

名称 | 描述
--- | ---
entity_id | Cliamte实体的entity_id.
fan_speed | 范围为1-100, 或者auto

示例
```
service: midea_ac_lan.set_fan_speed
data:
  entity_id: climate.XXXXXXXXXXXX_climate
  fan_speed: auto
```

### midea_ac_lan.set_attribute
设置空调属性, 服务数据:

名称 | 描述
--- | ---
entity_id | Cliamte实体的entity_id.
attribute | "aux_heat"<br/>"breezyless"<br/>"comfort_mode"<br/>"dry"<br/>"eco_mode"<br/>"indirect_wind"<br/>"natural_wind"<br/>"night_light"<br/>"prompt_tone"<br/>"screen_display"<br/>"smart_eye"<br/>"swing_horizontal"<br/>"swing_vertical"<br/>"turbo_mode"
value | true 或 false

示例
```
service: midea_ac_lan.set_attribute
data:
  entity_id: climate.XXXXXXXXXXXX_climate
  attribute: eco_mode
  value: true
```