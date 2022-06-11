# Midea AC LAN
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

[English](https://github.com/georgezhao2010/midea_ac_lan/blob/master/README.md) | 简体中文

通过本地局域网控制你的美的空调

# 安装
使用HACS以自定义存储库方式安装，或者从[Latest release](https://github.com/georgezhao2010/midea_ac_lan/releases/latest)下载最新的Release版本，将其中的`custom_components/midea_ac_lan`放到你的Home Assistant的`custom_components/midea_ac_lan`中。

# 配置
安装过后，到Home Assistant的集成界面添加集成。
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
msmart来自于[@mac-zhou](https://github.com/mac-zhou)的[midea-msmart](https://github.com/mac-zhou/midea-msmart)

## 将空调属性生成开关及传感器实体
如果选择了此选项，空调的一些属性将额外生成开关及传感器的实体，便于直接配置在HomeAssistant面板上进行操作
