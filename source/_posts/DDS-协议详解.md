---
title: DDS 协议详解
top: false
cover: false
toc: true
date: 2025-12-21 12:49:02
password:
summary:
tags:
- AutomotiveElectronic

---





# RTPS





## Message module

<br/>

![header](out/message_header.svg)

![submessage_header](out/message_submessage_header.svg)

<br/>

![infosource](out/message_infosource.svg)

![inforeply](out/message_inforeply.svg)

![infodestination](out/message_infodestination.svg)

![infotimestamp](out/message_infotimestamp.svg)

<br/>

![heartbeat](out/message_heartbeat.svg)

![heartbeatfrag](out/message_heartbeatfrag.svg)

<br/>

![nackfrag](out/message_nackfrag.svg)

![acknack](out/message_acknack.svg)

<br/>

![datafrag](out/message_datafrag.svg)

![data](out/message_data.svg)

<br/>

![gap](out/message_gap.svg)



<br/>

<br/>

## Qos

user_data，字符串类型，用于传递一些信息（比如网络绑定的 service name 等），用于 domain，participant，datareader 和 datawriter

topic_data，字符串类型，用于传递一些信息，用于 topic

group_data，字符串类型，用于传递一些信息，用于 publisher 和 subscriber

durability，枚举类型，表示是否需要对收到的 change 进行 cache，可选值有 volatile（不 cache），transient_local，transient（在内存 cache） 和 persistent（持久化存储），用于 topic，datareader 和 datawriter

Deadline，数值类型，表示 endpoint 预期在一定的时间内需要收到对端的消息，如果没有收到，就会调用 onrequesteddeadlinemissed（周期性）

latency_budget，数值类型，表示 writer 的消息，到 reader，允许的最大时延（如果超过了，会怎样，规范没有说）

Ownership，表示是否允许多个 writer 写入同一个 topic，同时多个 writer 有优先级的区分

liveliness，保活机制，表示是在哪些范畴之间的
