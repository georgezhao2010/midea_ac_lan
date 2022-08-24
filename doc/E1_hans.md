# 干衣机

## 生成实体
### 无默认实体

### 额外生成实体

EntityID | 类型 | 名称 | 描述 
--- | --- | --- | ---
binary_sensor.{DEVICEID}_door | Door | 门状态 
binary_sensor.{DEVICEID}_rinse_aid | Rinse Aid Shortage | 漂洗剂不足 
binary_sensor.{DEVICEID}_salt | Salt Shortage | 软水盐不足
sensor.{DEVICEID}_progress | sensor | Progress | 当前程序
sensor.{DEVICEID}_status | sensor | Status | 状态
sensor.{DEVICEID}_time_remaining | sensor | Time Remaining | 剩余时间
switch.{DEVICEID}_power | switch | Power | 电源开关

## 服务
生成以下扩展服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置洗碗机属性, 服务数据:

名称 | 描述
--- | ---
device_id | 设备的编号(Device ID)
attribute | "power"
value | true 或 false

示例
```
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```