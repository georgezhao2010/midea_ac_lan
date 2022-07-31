# Midea AC LAN
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![Donate](https://img.shields.io/badge/donate-BuyMeCoffee-yellow.svg)](https://www.buymeacoffee.com/georgezhao2010)
[![Stable](https://img.shields.io/github/v/release/georgezhao2010/midea_ac_lan)](https://github.com/georgezhao2010/midea_ac_lan/releases/latest)

[English](README.md) | 简体中文

通过本地局域网控制你的美的设备

- 通过HomeAssistant UI完成设备的自动搜索和配置.
- 生成额外的传感器和开关方便进行设备控制.
- 与设备保持TCP长连接以便实时同步设备状态.

本集成部分技术来源来自 [@mac-zhou](https://github.com/mac-zhou/midea-msmart)，他的美的midea-msmart提供了类似的功能。 该组件包括来自他的项目中经过改写的部分代码。

同时感谢[@NeoAcheron](https://github.com/NeoAcheron/midea-ac-py)

# 支持的设备

 名称 | 类型 | 文档
 --- | --- | ---
 空调器 | AC | [AC_hans.md](doc/AC.md)
 中央空调86控制面板 | CC | [CC_hans.md](doc/CC.md)
 电热水器 | E2 | 尚不支持

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

## 将属性生成传感器及开关实体

配置完成后, 默认将只生成一个climate实体。如果需要将climate的属性生成为扩展的传感器及开关实体，在Midea AC LAN集成卡片上点击'选项'，并选择要生成的传感器及开关(如果你的空调支持该属性)。


# 调试
要打开调试日志输出，在configuration.yaml中做如下配置
```
logger:
  default: warn
  logs:
    custom_components.midea_ac_lan: debug
```


