---
title: SomeIp 协议详解
top: false
cover: false
toc: true
mathjax: true
date: 2025-08-04 23:17:56
password:
summary:
tags:
- AutomotiveElectronic
categories:
---



# 基本概念

**S**calable Service-**O**riented **M**iddlewar**E** over **IP**

<br/>

## Event

<br/>

## Field

<br/>

## Request/Response Method

<br/>

## Fire&Forget Method

<br/>

# SomeIpHeader

## MessageId

### ServiceId

2 字节，表示当前报文是属于什么服务的

<br/>

### MethodId

2 字节，其最高位为 0 表示的是 method，最高位为 1 表示为 event 或者 notification

<br/>

<br/>

## Length

4 字节，表示从 RequestId 到消息结束的长度。

<br/>

<br/>

## RequestId

### ClientId

2 字节，表示请求的 client 是哪一个，或者说消息来自于哪一个 client

<br/>

### SessionId

2 字节，表示该请求是当前 client 的哪一次请求

<br/>

## ProtocalVersion

1 字节，表示当前 SOME/IP 协议的版本号，默认为 1

<br/>

## InterfaceVersion

1 字节，表示服务接口的版本号

<br/>

## MessageType

1 字节，表示当前的报文类型

<br/>

## ReturnCode

1 字节

<br/>

<br/>

# SomeIpSd

Sd 的报文头同样使用的是 SomeIpHeader，但是其中的部分值是固定的：

- ServiceID 固定为 0xFFFF
- MethodID 固定为 0x8100
- ClientID 一般固定为 0x0000
- SessionID 初始为 0x0001，每发送一次数据后便加 1
- Protocol Version 固定为 0x01
- Interface Version 固定为 0x01
- Message type 固定为 0x02（Notification）
- ReturnCode 固定为 0x00（E_OK）

<br/>

接着就会有一个 1 字节的 Flags，和 3 字节的 reserved。

后续都是 entry 和 option。

<br/>

Find service，意思为服务的使用者想要找到服务的提供者，从而在组播上发出的报文；而对应的提供者在收到了相应的报文之后，会发送 offer service，从而告知服务的使用者，提供者的元信息。

Offer service，目的为服务的提供者通过组播，告知外界自己这个节点，对外提供了什么服务。（可以注意到是周期发送的）

StopOffer service，目的是告知外界当前节点不再提供什么类型的服务了，从而在服务的使用者方，删除对应的 mapping

Subscribe，意思是 event 的使用者需要订阅对应 event 的提供者，而发出的报文。需要注意的是，实际上是以 eventgroup 的形式进行订阅的，而不能只订阅单个 event

Stop subscribe，停止订阅

<br/>

对于 someip-sd 消息而言，可以将其分为 someip header，someip sd header，entries array 以及 options array。

<br/>

<br/>

## Entry

### ServiceEntry

Type：FindService (0x00)、OfferService (0x01)、StopOfferService (0x01)

Index First Option Run：Option Array 中第一个 Option 的索引

Index Second Option Run：Option Array 中第二个 Option 的索引

of opt 1：第一个 Option 使用的选项数

of opt 2：第二个 Option 使用的选项数

Service ID：表示该 Entry 所涉及的服务或服务实例的 Service ID

Instance ID：表示该 Entry 涉及服务实例的 Instance ID，如果包含一个服务的所有服务实例，则设置为 0xFFFF

Major Version：服务的主版本号

TTL：Entry 的生命周期，单位为秒

Minor Version：服务的次版本号

<br/>

### EventGroupEntry

Type：SubscribeEventgroup（0x06）、StopSubscribeEventgroup（0x06）、  SubscribeEventgroupAck（0x07）、SubscribeEventgroupNack（0x07）

Index First Option Run：Option Array 中第一个 Option 的索引

Index Second Option Run：Option Array 中第二个 Option 的索引

of opt 1：第一个 Option 使用的选项数

of opt 2：第二个 Option 使用的选项数

Service ID：表示该 Entry 所涉及的服务或服务实例的 Service ID

Instance ID：表示该 Entry 涉及服务实例的 Instance ID，任何实例的 Instance ID 都不能设置为 0xFFFF（这一点和在 Service Entry 中的不同）

Major Version：服务的主版本号

TTL：Entry 的生命周期，单位为秒

Reserved：应被设置为 0x000

Counter：用于区分同一订阅者的订阅事件组。如果不使用，设置为0x0

Eventgroup ID：事件组 ID

<br/>

<br/>

## Option
