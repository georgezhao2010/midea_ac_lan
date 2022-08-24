# Midea AC LAN
[![hacs_badge](https://img.shields.io/badge/HACS-Default-blue.svg)](https://github.com/hacs/integration)
[![Donate](https://img.shields.io/badge/donate-BuyMeCoffee-blue.svg)](https://www.buymeacoffee.com/georgezhao2010)
[![Stable](https://img.shields.io/github/v/release/georgezhao2010/midea_ac_lan)](https://github.com/georgezhao2010/midea_ac_lan/releases/latest)

[English](https://github.com/georgezhao2010/midea_ac_lan/blob/master/README.md) | 简体中文

通过本地局域网控制你的美的M-Smart设备

- 通过HomeAssistant UI完成设备的自动搜索和配置.
- 生成额外的传感器和开关方便进行设备控制.
- 与设备保持TCP长连接以便实时同步设备状态.

本集成部分技术来源来自 [@mac-zhou](https://github.com/mac-zhou/midea-msmart)，他的美的midea-msmart提供了类似的功能。 该组件包括来自他的项目中经过改写的部分代码。

同时感谢[@NeoAcheron](https://github.com/NeoAcheron/midea-ac-py)

# 已支持的设备

 类型 | 名称 |文档
 --- | --- | ---
 AC | 空调器 | [AC_hans.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/AC_hans.md)
 CC | 中央空调86控制面板 | [CC_hans.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/CC_hans.md)
 DA | 波轮洗衣机 | [DA_hans.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/DA_hans.md)
 DB | 滚筒洗衣机 | [DB_hans.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/DB_hans.md)
 DC | 干衣机 | [DC_hans.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/DC_hans.md)
 E1 | 洗碗机 | [E1_hans.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/E1_hans.md)
 E2 | 电热水器 | [E2_hans.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/E2_hans.md)
 E3 | 燃气热水器 | [E3_hans.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/E3_hans.md)

# 安装
在HACS中搜索'Midea AC LAN'并安装，或者从[Latest release](https://github.com/georgezhao2010/midea_ac_lan/releases/latest)下载最新的Release版本，将其中的`custom_components/midea_ac_lan`放到你的HomeAssistant的`custom_components/midea_ac_lan`中。

重启HomeAssistant

# 配置
安装之后，在HomeAssistant的集成界面搜索添加集成Midea AC LAN, 如果需要添加多台设备，多次添加本集成并执行自动配置即可。

或者直接点击 [![Configuration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=midea_ac_lan)

## 自动配置
自动配置会自动搜索网络上的美的M-Smart设备，并将搜索到的空调列出，选择一台空调执行添加即可。

**自动配置要求设备必须与HA在同一网段，否则搜索不到设备的，请自行确认这点**

## 指定IP地址配置
如果自动配置无法完成，可以尝试通过指定IP地址的方式搜索设备并进行配置。

## 手动配置
如果之前你已经通过其它集成手工配置过设备, 并知道以下信息, 也可以进行手动配置
- 设备ID
- 设备类型 ([已支持的设备](https://github.com/georgezhao2010/midea_ac_lan/blob/master/README_hans.md#%E5%B7%B2%E6%94%AF%E6%8C%81%E7%9A%84%E8%AE%BE%E5%A4%87)之一)
- IP地址
- 端口(默认为6444)
- 协议版本
- Token
- Key


## 额外的传感器及开关实体

配置完成后, 默认将只生成一个主要实体(比如climate实体)。如果需要其它属性生成为扩展的传感器及开关实体，在Midea AC LAN集成卡片上点击'选项'，并选择要生成的传感器及开关(如果你的空调支持该属性)。


# 调试
要打开调试日志输出，在configuration.yaml中做如下配置
```
logger:
  default: warn
  logs:
    custom_components.midea_ac_lan: debug
```

# 可能有用的东西
- [Lovelace simple thermostat card](https://github.com/nervetattoo/simple-thermostat)
- [Water Heater Card for Lovelace](https://github.com/rsnodgrass/water-heater-card)
