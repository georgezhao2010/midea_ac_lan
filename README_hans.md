# Midea AC LAN
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
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

如果选择了此选项，空调的以下属性将额外生成传感器及开关的实体，便于直接配置在HomeAssistant面板上进行操作或者通过HomeKit让Siri控制这些开关
- 室外机温度传感器
- 舒省模式开关
- 节能模式开关
- 防直吹开关
- 水平摆风开关
- 垂直摆风开关
- 操作提示音开关

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
climate.{DEVICEID}_climate | climate | 恒温器实体

### 额外生成实体
如果选择将空调属性生成开关及传感器实体, 将额外生成以下传感器及开关实体

实体ID | 类型 | 备注
--- | --- | ---
sensor.{DEVICEID}_outdoor_temperature | sensor | 室外机温度
switch.{DEVICEID}_comfort_mode | switch | 舒省模式开关
switch.{DEVICEID}_eco_mode | switch | 节能模式开关
switch.{DEVICEID}_indirect_wind | switch | 防直吹开关
switch.{DEVICEID}_swing_horizontal | switch | 水平摆风开关
switch.{DEVICEID}_swing_vertical | switch | 垂直摆风开关
switch.{DEVICEID}_prompt_tone | switch | 提示音开关

## 服务
除climate原有服务外, 还生成以下服务

服务 | 作用 |参数 
--- | --- |--- 
midea_ac_lan.set_fan_speed | 精细设置风扇风速 | entity_id, fan_speed (1-100数字或者"auto")
midea_ac_lan.set_comfort_mode | 打开或关闭舒省模式 | entity_id, comfort_mode (ture 或 false)
midea_ac_lan.set_eco_mode | 打开或关闭节能模式 | entity_id, eco_mode (ture 或 false)
midea_ac_lan.set_indirect_wind | 打开或关闭防直吹 | entity_id, indirect_wind (ture 或 false)
midea_ac_lan.set_prompt_tone | 打开或关闭提示音 | entity_id, prompt_tone (ture 或 false)

# 调试
要打开调试日志输出，在configuration.yaml中做如下配置
```
logger:
  default: warn
  logs:
    custom_components.midea_ac_lan: debug
```


