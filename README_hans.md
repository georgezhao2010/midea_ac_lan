# Midea AC LAN
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![Donate](https://img.shields.io/badge/donate-BuyMeCoffee-yellow.svg)](https://www.buymeacoffee.com/georgezhao2010)
[![Stable](https://img.shields.io/github/v/release/georgezhao2010/midea_ac_lan)](https://github.com/georgezhao2010/midea_ac_lan/releases/latest)

[English](https://github.com/georgezhao2010/midea_ac_lan/blob/master/README.md) | 简体中文

通过本地局域网控制你的美的空调

不用额外安装python库，不用写配置文件，可自动完成配置过程

本集成技术来源来自 [@mac-zhou](https://github.com/mac-zhou/midea-msmart)，他的美的midea-msmart提供了类似的功能。 该组件包括来自他的项目中经过改写的部分代码。

同时感谢[@NeoAcheron](https://github.com/NeoAcheron/midea-ac-py)

# 支持设备
- 美的空调 (V2 or V3), type "AC"
- ~美的空调遥控面板, type "CC"~

# 安装
在HACS中搜索'Midea AC LAN'并安装，或者从[Latest release](https://github.com/georgezhao2010/midea_ac_lan/releases/latest)下载最新的Release版本，将其中的`custom_components/midea_ac_lan`放到你的Home Assistant的`custom_components/midea_ac_lan`中。

# 配置
安装过后，到Home Assistant的集成界面搜索添加集成Midea AC LAN。
配置可以选择自动或手动配置

## 自动配置
自动配置会自动搜索网络上的美的空调，并将搜索到的空调列出，选择一台空调执行添加即可。如果需要添加多台空调，多次添加本集成并执行自动配置即可。

**自动配置要求空调必须与HA在同一网段，否则搜索不到设备的，请自行确认这点**

## 手动配置
如果自动配置无法完成，可以尝试手动添加空调设备，手动配置空调需要准备以下信息：
- 设备ID
- IP地址
- 端口(默认为6444)
- 型号(非关键信息, 不知道可以填写Unknown)
- 协议版本(2或者3)
- Token
- Key

如果不知道设备ID/Token/Key这些信息，可以在宿主机中执行以下命令
```
pip3 install msmart
midea-discover
```
***msmart来自于[@mac-zhou](https://github.com/mac-zhou)的[midea-msmart](https://github.com/mac-zhou/midea-msmart)***

## 将空调属性生成传感器及开关实体

配置完成后, 默认将只生成一个climate实体。如果需要将climate的属性生成为扩展的传感器及开关实体，在Midea AC LAN集成卡片上点击'选项'，并选择要生成的传感器及开关(如果你的空调支持该属性)。所有传感器及开关列表见[额外生成实体](#%E9%A2%9D%E5%A4%96%E7%94%9F%E6%88%90%E5%AE%9E%E4%BD%93)

# 功能
## 支持的温控器操作
- 支持目标温度设定
- 支持运行模式设定
- 支持风扇模式设定
- 支持摆风模式设定
- 支持电辅热

## 生成实体
### 默认生成实体
实体ID | 类型 | 备注
--- | --- | ---
climate.{DEVICEID}_climate | Climate | 恒温器实体

### 额外生成实体

EntityID | 类型 | 名称 | 备注
--- | --- | --- | --- 
sensor.{DEVICEID}_indoor_humidity | Sensor | Indoor humidity | 湿度
sensor.{DEVICEID}_indoor_temperature | Sensor | Indoor Temperature | 室内温度
sensor.{DEVICEID}_outdoor_temperature | Sensor | Outdoor Temperature | 室外机温度
switch.{DEVICEID}_aux_heat | Switch | Aux Heating | 电辅热
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
switch.{DEVICEID}_turbo_mode | Switch | Turbo Mode | 强劲模式

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

# 调试
要打开调试日志输出，在configuration.yaml中做如下配置
```
logger:
  default: warn
  logs:
    custom_components.midea_ac_lan: debug
```


