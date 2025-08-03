---
title: Doip 协议详解
top: false
cover: false
toc: true
mathjax: true
date: 2025-08-03 23:46:27
password:
summary:
tags:
- AutomotiveElectronic
categories:
---



# Header

1 字节的版本号，1 字节的版本号取反，2 字节的报文类型，4 字节的报文长度。

其中报文类型为 0000 的诊断报文，是通用 doip 报文头否定响应，所有类型都需要实现的。

<br/>

<br/>

# Tcp type

## 0x0005 路由激活请求

2 字节的 source address，1 字节的 activation type，4 字节的 0000 0000

4 字节的 vm specific，一般是通过配置决定

<br/>

## 0x0006 路由激活响应

2 字节的 target address（一般是指 ecu 的地址），2 字节的 source address（一般是指上位机的诊断地址）

1 字节的 routing activation response code，表示当前路由激活的状态

4 字节的 future standardization use，被标准保留的值，一般为 0000 0000

<br/>

## 0x0007 在线检查请求

不携带任何数据

<br/>

## 0x0008 在线检查响应

2 字节的 diagnostic address

<br/>

## 0x8001 诊断报文

2 字节的 source address，2 字节的 target address，一定字节数量的 uds 报文

<br/>

## 0x8002 诊断肯定响应

2 字节的 source address，2 字节的 target address，1 字节的 ack code

后面可以携带一定字节数量的诊断报文，长度可以通过配置来决定

<br/>

## 0x8003 诊断消极响应

2 字节的 source address，2 字节的 target address，1 字节的 nack code

后面可以携带一定字节数量的诊断报文，长度可以通过配置来决定

<br/>

<br/>

# Udp type

## 0x4001 实体状态请求

不携带任何数据

<br/>

## 0x4002 实体状态响应

1 字节的 node type，1 字节的 最多允许 tcp 连接数量，1 字节的 tcp socket 数量（是指 socket 数，不是已经激活的 router 数量）

<br/>

## 0x4003 诊断电传模式请求

不携带任何数据

<br/>

## 0x4004 诊断电源模式响应

1 字节的 diagnostic power mode

<br/>

## 0x0001 车辆识别请求

不携带任何数据

<br/>

## 0x0002 车辆识别请求（携带 eid）

6 字节的 eid

如果和 ecu 的 eid 不一样，需要回复 nack

<br/>

## 0x0003 车辆识别请求（携带 vin）

17 字节的 vin

如果和 ecu 的 vin 不一样，需要回复 nack

<br/>

## 0x0004 车辆识别响应/车辆声明

17 字节的 vin 码，2 字节的逻辑地址，6 字节的 eid，6 字节的 gid，1 字节的 further action required（都是必选项）

vin/gid sync status 可选，一般是通过配置决定

<br/>

# Header check handler

![](doip_header_check.png)

对应的错误码：

![](doip_header_code.png)



# Diagnostic message check handler

![](doip_diagnostic_message_check.png)

对应的错误码：

![](doip_diagnostic_message_code.png)

<br/>

<br/>

# Routing activation check handler

![](doip_routing_activation_check.png)

对应的错误码：

![](doip_routing_code.png)
