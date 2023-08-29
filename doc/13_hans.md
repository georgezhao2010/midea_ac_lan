# 智能灯
## 特性
- 支持亮度调节
- 支持色温调节
- 支持灯效(场景)调节

## 自定义

设置灯的以开尔文表示的色温范围 (默认为[2700, 6500]).

```
{"color_temp_range_kelvin": [2000, 6800]}
```

## 实体
### 默认实体
| 实体ID                   | 类型 | 描述  |
|------------------------|-------|-----|
| light.{DEVICEID}_light | light | 灯实体 |

### Extra entities

| 实体ID                        | 类型     | 名称          | 描述   |
|-----------------------------|--------|-------------|------|
| switch.{DEVICEID}_delay_off | switch | Delayed Off | 延迟关闭 |
| select.{DEVICEID}_effect    | select | Effects     | 效果   |


## 服务
生成以下扩展服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性, 服务数据:

| 名称        | 描述               |
|-----------|------------------|
| device_id | 设备的编号(Device ID) |
| attribute | "delay_off"      |
| value     | true or false    |


| 名称        | 描述                                                           |
|-----------|--------------------------------------------------------------|
| device_id | 设备的编号(Device ID)                                             |
| attribute | "effect"                                                     |
| value     | "Living"</br>"Reading"</br>"Mildly"</br>"Cinema"</br>"Night" |

示例
```
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: eco_mode
  value: true
```

```
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: effect
  value: "Reading"
```
