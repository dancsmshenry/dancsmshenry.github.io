---
title: UDS 协议详解
top: false
cover: false
toc: true
mathjax: true
date: 2024-07-21 14:59:47
password:
summary:
tags:
- AutomotiveElectronic
categories:
---

# 序

对于 `UDS` 协议，没法剥离出一个完全原子的概念出来理解，很多概念之间是相互穿插着的。

所以私以为一种比较好的理解思路便是，一股脑的介绍完所有的概念，

然后再通过一个简单的服务请求，或是 `DTC` 的报告，将这些概念逐个逐个的进行穿插和联系。

（TODO：后续可以画两个图，分别将  `DCM` 和 `DEM` 的概念串联起来；实名 diss 一下公司的某讲师，一上来就把各种服务的参数怼新人的脸上，不知道的以为是在期末考试划重点。。。）

<br/>

# 子服务

一个 Bit 有 8 个 b，其中的后 7 个 b 表示子服务的 id，而第 8 个 b 表示是否抑制肯定响应位。

抑制肯定响应位的含义有两层，第一层是如果当前需要回复的是消极响应，那么无论如何都需要回复出去；

第二层是，只有需要回复的是积极响应，并且没有发送过 0x78 的报文（也就是 p2 没有超时），那么则不需要回复该积极响应，否则都要回复。

<br/>

# 积极响应与消极响应

<br/>

# 常见的定时器

<br/>

## p2

<br/>

## p2*

<br/>

## s3

<br/>

# DataIdentifier

<br/>

# RoutineIdentifier

<br/>

# Session

<br/>

# SecurityLevel

<br/>

# DiagnosticTroubleCode

<br/>

# DiagnosticTroubleCodeStatus

| Bit  | Name                               | Description                                                  |
| ---- | ---------------------------------- | ------------------------------------------------------------ |
| Bit0 | TestFailed                         | 表示 DTC 最近一次报告的结果是否为 Failed。<br/>当最近一次报告的结果为 Failed 时，需要将当前 Bit 置为 1；<br/>当最近一次报告的结果为 Passed、DEM 模块首次初始化、或者 `ClearDiagnosticInformation` 时，需要将当前 Bit 置为 0（老化成功并不会将当前 Bit 置为 0） |
| Bit1 | TestFailedThisOperationCycle       | 表示 DTC 在当前的操作循环中，是否报告过 Failed。<br/>在当前操作循环中，只要报告了 Failed，就需要将当前 Bit 置为 1；<br/>当重启操作循环、DEM 模块初始化，或者 `ClearDiagnosticInformation` 时，需要将当前 Bit 置为 0 |
| Bit2 | PendingDTC                         | 表示 DTC 在当前的操作循环，以及上一个操作循环中，是否报告过 Failed。<br/>当报告 Failed 时，需要将当前 Bit 置为 1；<br/>当此时的操作循环结束，并且在这个操作循环中没有报告过 Failed（Bit1 和 Bit6 都为 0）、或者 DEM 首次初始化、或者 `ClearDiagnosticInformation` 时，需要将当前 Bit 置为 0 |
| Bit3 | ConfirmedDTC                       | 表示 DTC 经历了一定次数的操作循环，并且在这些操作循环中都报告过 Failed 时，需要将当前 Bit 置为 1<br/>当 DTC 老化完成，或是 DEM 模块首次初始化，或是当前的数据因为存储的 overflow 而被移除，或是 `ClearDiagnosticInformation` 时，需要将当前 Bit 置为 0 |
| Bit4 | TestnotCompletedSinceLastClear     | 表示自从上一次 clear 之后，是否有报告过 Passed 或者 Failed。<br/>当报告 Failed 或者 Passed 时，需要将当前 Bit 置为 0；<br/>当 `ClearDiagnosticInformation` 或者 DEM 模块初始化时，需要将当前 Bit 置为 1；<br/>需要注意的是，下游 dtc 报告的 preFailed 或者 prePassed 并不算是一次完整的报告 |
| Bit5 | TestFailedSinceLastClear           | 表示自从上一次 clear，当前的 DTC 是否有报告过 Failed。<br/>当报告 Failed 时，需要将当前 Bit 置为 1；<br/>当 `ClearDiagnosticInformation` 或者 DEM 模块初始化，或者老化成功，或者因为 overflow 将数据删除了，需要将当前 Bit 置为 0 |
| Bit6 | TestNotCompletedThisOperationCycle | 表示在当前的操作循环中，是否没报告过 Failed 或者 Passed。<br/>当报告 Failed 或者 Passed 时，需要将当前 Bit 置为 0；<br/>当重启操作循环、DEM 模块初始化，或者 `clearDiagnosticInformation` 时，需要将当前 Bit 置为 1 |
| Bit7 | WarningIndicator                   | 初始值为 0；当配置了 indicator，Bit3 变为 1（此时 Bit0 也一定为 1），并且也符合主机厂或者供应商的需求时，将当前 Bit 置为 1<br/>当 healing 结束，0x14 服务，或者一些主机厂自定义的条件满足时，将当前 Bit 置为 0 |

<br/>

对于有 dtc，当报告 failed 时需要将 bit7 置为 0 的 dtc 而言，有以下的状态位变化：

|                      | bit7 | bit6 | bit5 | bit4 | bit3 | bit2 | bit1 | bit0 | Result |
| -------------------- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ------ |
| 初始状态             | 0    | 1    | 0    | 1    | 0    | 0    | 0    | 0    | 0x50   |
| 初始化->failed       | 0    | 0    | 1    | 0    | 1    | 1    | 1    | 1    | 0x2F   |
| failed->重启操作循环 | 0    | 1    | 1    | 0    | 1    | 1    | 0    | 1    | 0x6D   |
| failed->重启操作循环 | 0    | 1    | 1    | 0    | 1    | 0    | 0    | 1    | 0x69   |

<br/>

对于有 dtc，当报告 failed 时需要将 bit7 置为 1 的 dtc 而言，有以下的状态位变化：

|                      | bit7 | bit6 | bit5 | bit4 | bit3 | bit2 | bit1 | bit0 | Result |
| -------------------- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ------ |
| 初始状态             | 0    | 1    | 0    | 1    | 0    | 0    | 0    | 0    | 0x50   |
| 初始化->failed       | 1    | 0    | 1    | 0    | 1    | 1    | 1    | 1    | 0xAF   |
| failed->重启操作循环 | 1    | 1    | 1    | 0    | 1    | 1    | 0    | 1    | 0xED   |
| failed->重启操作循环 | 0    | 1    | 1    | 0    | 1    | 0    | 0    | 1    | 0xE9   |

<br/>

<br/>

<br/>

# Aging 与 Healing

二者的区别就在于，对于一些 dtc 而言，需要在报告 failed 之后，将 bit7 置位为 1，并在一定的操作循环之后，才将其置为 0。

（注：此处先不考虑 dtc 在这期间报告 passed 的情况，因为存在一些厂商要求报告 passed 之后，将 bit7 置为 0）

因此，将上述流程，描述为 healing，也就是愈合。

<br/>

而在经过了 healing 之后，距离能够自主的通过操作循环的重启，将相关的故障信息清楚的流程，称之为 aging，也就是老化。

（注：此处先不考虑 dtc 在这期间报告 failed 的情况）

<br/>

<br/>

<br/>

# Snapshot

在发生了故障时，存储一些重要的信息。

从实现上来看，就是读取某些 did 的信息，并存储在非易失性存储介质中。

<br/>

<br/>

<br/>

# ExtendedData

常用的几个内置 DataElement 都是 `std::uint8` 类型的（除了 FDC10），达到 255 之后都不会继续增加。

| Name                                | Condition                                                    | ClearCondition                                   |
| ----------------------------------- | ------------------------------------------------------------ | ------------------------------------------------ |
| OCC1<br/>（CyclesSinceLastFailed）  | 报告 failed 之后的**每次**操作循环重启都 +1<br/>也就是每次操作循环重启时，如果此时 bit1 为 1 并且 OCC1 为零，<br/>或者 OCC1 不为 0 并且 bit1 为 0，才 + 1<br/> | 1. 0x14 服务<br/>2. 老化成功<br/>3. 上报 failed  |
| OCC3<br/>（CyclesSinceFirstFailed） | **首次**报告 failed 之后的**每次**操作循环重启都 +1<br/>也就是每次操作循环重启时，如果此时 bit1 为 1，<br/>或者 OCC3 不为 0，才 +1 | 1. 0x14 服务<br/>2. 老化成功                     |
| OCC4<br/>（FailedCycles）           | 当前操作循环**首次**报告 failed 之后，就 +1<br/>也就是当 bit1 从 0 变为 1 时，才 + 1 | 1. 0x14 服务<br/>2. 老化成功                     |
| FDC10                               | 当报告 failed 之后，变为 127<br/>当报告 passed 之后，变为 -128 | 1. 0x14 服务<br/>2. 老化成功<br/>3. 操作循环重启 |

<br/>

在 uds 侧的 dtc，confirmed 的 threshold 一般都是 1。

<br/>

OCC1 与老化计数的关系：假设老化计数配的为 10，那么当 occ1 变为 11 的那一刻，才会彻底清除故障信息

<br/>

注：实际上存在一些内置 dataelement 来做拓展数据的，但目前没有看到厂商用过（或许是因为本质上，是可以归纳为快照数据的）

<br/>

<br/>

<br/>

# 0x10

在 UDS 的规范中，定义了会话状态的概念。会话状态可以简单的理解为是当前的 ECU 处于某种会话模式下。

会话模式的作用，主要是为了限制服务的使用。比如说在做诊断应用的设计的时候，可以指定某个服务必须要在某些指定的会话状态下执行。其中 0x10 服务便是用来切换会话的。

根据 14229 的规范，0x10 的 request message 格式为：

| 数值位 | 参数名字 | 可选值    | 是否为必选项 |
| ------ | -------- | --------- | ------------ |
| #1     | 服务 id  | 0x10      | 是           |
| #2, #3 | 会话 id  | 0x00-0xFF | 是           |

会话可由用户自行在工具中配置，但规范规定了一些固有的会话类型：

| 会话 id | 会话名                        |
| ------- | ----------------------------- |
| 0x01    | defaultSession                |
| 0x02    | ProgrammingSession            |
| 0x03    | extendedDiagnosticSession     |
| 0x04    | safetySystemDiagnosticSession |

关于会话模式，有以下几点是需要注意了解的：

1. 在一般的情况下， ECU 一上电，都是处于**默认会话**
2. 在 ECU 中会维护一个名为 S3 的定时器，假如当前 ECU 的会话状态不是默认会话，那么就会启用该定时器。一旦有新的请求，便会刷新该定时器。如果在定时器到时的时候，依旧没有新的请求，那么 ECU 就会自动将会话切换到默认会话下
3. 在 UDS 的概念中定义了定时器 `p2` 和 `p2 *`。当一条服务从刚开始处理，到 p2 定时器超时，这个期间，如果服务还没有处理完，则需要给外部的诊断仪或者脚本发送 0x78 的报文，告知对方当前的服务超时了，后续还会将响应发来。紧接着就会启动 `p2*`的定时器，在 `p2*` 的定时器超时后，又会接着发送 0x78 的报文 （其中 p2 定时器的单位是 **1ms**，`p2*` 定时器的单位是 **10ms**）

<br/>

根据 14229 的规范，0x10 的 positive response message 格式为：

| 数值位 | 参数名字                  | 可选值        | 是否为必选项 |
| ------ | ------------------------- | ------------- | ------------ |
| #1     | 服务 id + positive 偏移量 | 0x50          | 是           |
| #2, #3 | 会话 id                   | 0x00-0xFF     | 是           |
| #4, #5 | p2 server 定时器          | 0x0000-0xFFFF | 是           |
| #6, #7 | p2* server 定时器         | 0x0000-0xFFFF | 是           |

<br/>

<br/>

<br/>

# 0x11

该服务从字面意思上理解，就是用来重启 ECU 的。而重启有不同的类型，具体的重启类型可以参见子服务。

规范中并没有定义在发送了 0x11 的 positive response 之后，到真正重启之间，ECU 的行为。但推荐在这个期间 ECU 不要解说任何的 request 或是发送任何的 response。

根据 14229 的规范，0x11 的 request message 格式为：

| 数值位 | 参数名字  | 可选值    | 是否为必选项 |
| ------ | --------- | --------- | ------------ |
| #1     | 服务 id   | 0x11      | 是           |
| #2     | 子服务 id | 0x00-0xFF | 是           |

而其中具体的子服务，在 14229 的规范中，有定为以下几种：

| 子服务 id | 含义                                                         |
| --------- | ------------------------------------------------------------ |
| 0x01      | HardReset，硬件复位，模拟通常在服务器与其电源断开后执行的通电/启动顺序。简单的理解为就是整个 ECU 重启了。有可能会导致易失性存储和非易失性存储失效 |
| 0x02      | keyOffOnReset，点火循环复位，模拟关机顺序（即中断开关电源）。有点类似于驾驶员用钥匙给汽车关闭后又重新点火的过程。其中非易失性存储将会被保存，易失性存储会被重置 |
| 0x03      | softReset，软复位，简单理解就是将应用程序重启                |
| 0x04      | enableRapidPowerShutDown，适用于非点火供电而仅为电池供电的ECU。因此，关机会迫使睡眠模式关闭，而不是关闭电源。睡眠意味着关闭电源，但仍准备唤醒（电池供电）。子功能的目的是减少在点火开关进入关闭位置后的ECU的备用时间。 |
| 0x05      | disableRapidPowerShutDown，关闭 0x04 服务                    |

<br/>

根据 14229 的规范，0x11 的 positive response message 格式为：

| 数值位 | 参数名字                  | 可选值    | 是否为必选项                     |
| ------ | ------------------------- | --------- | -------------------------------- |
| #1     | 服务 id + positive 偏移量 | 0x51      | 是                               |
| #2     | 子服务 id                 | 0x00-0x7F | 是                               |
| #3     | powerDownTime             | 0x00-0xFF | 当子服务为 0x04 的时候才会有该项 |

<br/>

<br/>

<br/>

# 0x27

该服务是用来解锁安全等级的。安全等级和会话等级是类似的概念，都是用来限制服务需要在指定的环境下执行。但与会话等级不同的是，会话等级一问一答便可以切换会话，而安全等级则需要先请求安全种子，计算key，比较key，之后再判断是否可以解锁安全等级。

0x27 是带有子服务的 UDS 服务，其中子服务为 0x01-0x41 之间的奇数的，都是 requestSeed 请求种子的服务；子服务为 0x02-0x42 之间的偶数的，都是 sendKey 发送 key 值。

其实，这里的子服务是一一对应的。比如说 子服务id 为 0x01 的 requestSeed 服务，那么就需要对应子服务id 为 0x02 的 sendkey 服务，即 requestSeed 的子服务 id，是其对应的

<br/>

根据 14229 的规范，0x27 的 request message ，其中子服务为 requestSeed 的报文结构为：

| 数值位  | 参数名字  | 可选值                   | 是否为必选项 |
| ------- | --------- | ------------------------ | ------------ |
| #1      | 服务 id   | 0x27                     | 是           |
| #2      | 子服务 id | 0x01,0x03,0x05,0x07-0x7D | 是           |
| #3...#n | 具体数据  | 0x00-0xFF                | 否           |

<br/>

根据 14229 的规范，0x27 的 request message ，其中子服务为 sendKey 的报文结构为：

| 数值位  | 参数名字    | 可选值                   | 是否为必选项 |
| ------- | ----------- | ------------------------ | ------------ |
| #1      | 服务 id     | 0x27                     | 是           |
| #2      | 子服务 id   | 0x02,0x04,0x06,0x08-0x7E | 是           |
| #3...#n | securityKey | 0x00-0xFF                | 是           |

<br/>

根据 14229 的规范，0x27 的子服务 requestSeed 的 positive response message 格式为：

| 数值位  | 参数名字                  | 可选值                   | 是否为必选项 |
| ------- | ------------------------- | ------------------------ | ------------ |
| #1      | 服务 id + positive 偏移量 | 0x67                     | 是           |
| #2      | 子服务 id                 | 0x01,0x03,0x05,0x07-0x7D | 是           |
| #3...#n | securitySeed              | 0x00-0xFF                | 是           |

<br/>

根据 14229 的规范，0x27 的子服务 sendKey 的 positive response message 格式为：

| 数值位 | 参数名字                  | 可选值                   | 是否为必选项 |
| ------ | ------------------------- | ------------------------ | ------------ |
| #1     | 服务 id + positive 偏移量 | 0x67                     | 是           |
| #2     | 子服务 id                 | 0x02,0x04,0x06,0x08-0x7E | 是           |

<br/>

<br/>

<br/>

# 0x28

0x28 服务是用来打开或者关闭某类报文信息的发送和接收功能。

根据 14229 的规范，0x28 的 request message 的报文结构如下所示。

| 数值位 | 参数名字                    | 可选值    | 是否为必选项                                                 |
| ------ | --------------------------- | --------- | ------------------------------------------------------------ |
| #1     | 服务 id                     | 0x28      | 是                                                           |
| #2     | 子服务 id                   | 0x00-0xFF | 是                                                           |
| #3     | communicationType，消息类型 | 0x00-0xFF | 是                                                           |
| #4     | nodeIdentificationNumber    | 0x00-0xFF | 否，当 communicationType 是 04 或者 05 的失火，才需要填写该参数 |
| #5     | nodeIdentificationNumber    | 0x00-0xFF | 否，当 communicationType 是 04 或者 05 的失火，才需要填写该参数 |

根据 14229 的规范，目前支持的 subfunction 有：

| 子服务 id | 含义                                                         |
| --------- | ------------------------------------------------------------ |
| 0x00      | enableRxAndTx，启用对某种消息的发送和接收                    |
| 0x01      | enableRxAndDisableTx，启用对某种消息的接受，禁用对某种消息的发送 |
| 0x02      | disableRxAndEnableTx，禁用对某种消息的接收，启用对某种消息的发送 |
| 0x03      | disableRxAndTx，禁用对某种消息的接收和发送                   |
| 0x04      | enableRxAndDisableTxWithEnhancedAddressInformation，表示寻址总选需要切换到诊断调度模式 |
| 0x05      | enableRxAndTxWithEnhancedAddressInformation，表示寻址总线需要切换到应用程序调度模式 |

而对于 communicationType，具体在 14229 中表 B.1 中有详细的赘述，更多细节可以关注 ISO 14229 的规范。

<br/>

根据 14229 的规范，0x28 的 positive response message 格式为：

| 数值位 | 参数名字                  | 可选值    | 是否为必选项 |
| ------ | ------------------------- | --------- | ------------ |
| #1     | 服务 id + positive 偏移量 | 0x68      | 是           |
| #2     | 子服务 id                 | 0x00-0x7F | 是           |

<br/>

<br/>

<br/>

# 0x29

认证主要分为 APCE 和 ACR，a 核上的协议栈一般只支持 APCE。

APCE 的全称 Authentication with PKI Certificate Exchange，又分为单向认证和双向认证

ACR 的全称 Authentication with Challenge-Response

<br/>

按照 14229 的规范，支持的子服务如下所示：

| 子服务名称                                | 作用                                       |
| ----------------------------------------- | ------------------------------------------ |
| 0x00 deAuthenticate                       | 主动结束认证状态                           |
| 0x01 verifyCertificateUnidirectional      | 单向认证（为 APCE 下的子服务）             |
| 0x02 verifyCertificateBidirectional       | 双向认证（为 APCE 下的子服务）             |
| 0x03 proofOfOwnership                     | 所有权证明（为 APCE 下的子服务）           |
| 0x04 transmitCertificate                  | 传输证书（为 APCE 下的子服务）             |
| 0x05 requestChallengeForAuthentication    | （为 ACR 下的子服务）                      |
| 0x06 verifyProofOfOwnershipUnidirectional | （为 ACR 下的子服务）                      |
| 0x07 verifyProofOfOwnershipBidirectional  | （为 ACR 下的子服务）                      |
| 0x08 authenticationConfiguration          | 表示当前协议栈支持的认证，是 APCE 还是 ACR |



单向认证：

0x01 服务，传递 client certificate 和 client challenge；server 回复 server challenge 和 server ephemeral public key

再使用 0x03 服务，传递 client proofOfOwnershipClient 和 client ephemeral public key；server 回复 SessionKeyInfo

<br/>

<br/>

<br/>

# 0x3E

该服务适用于保持外部的 client（上位机或是诊断脚本）与诊断 server 之间的活跃状态。而在实际的作用中，更多的是为了保持当前诊断会话的状态。（因为我们知道 s3 timer 如果在这个时间内都没有新的连接进入，那么就会导致会话切换回默认会话状态）

根据 14229 的规范，0x3E 的 request message 的报文结构如下所示。

| 数值位 | 参数名字  | 可选值    | 是否为必选项 |
| ------ | --------- | --------- | ------------ |
| #1     | 服务 id   | 0x3E      | 是           |
| #2     | 子服务 id | 0x00/0x80 | 是           |

注：在子服务 id 中，其中的 Bit7，也就是第八位，当为 0 的时候，表示为需要发送肯定响应，而为1的时候，则需要抑制肯定响应

根据 14229 的规范，目前支持的 subfunction 有

| 子服务 id | 含义            |
| --------- | --------------- |
| 0x00      | zeroSubFunction |

<br/>

根据 14229 的规范，0x3E 的 positive response message 格式为：

| 数值位 | 参数名字                  | 可选值 | 是否为必选项 |
| ------ | ------------------------- | ------ | ------------ |
| #1     | 服务 id + positive 偏移量 | 0x7E   | 是           |
| #2     | 子服务 id                 | 0x00   | 是           |

<br/>

<br/>

<br/>

# 0x85

该服务用于表示是否开启 DEM 模块的报告。需要注意的是，按照 14229 的规范，如果切换到了默认会话，是需要开启 DEM 模块的报告的

根据 14229 的规范，0x85 的 request message 的报文结构如下所示。

| 数值位 | 参数名字  | 可选值    | 是否为必选项 |
| ------ | --------- | --------- | ------------ |
| #1     | 服务 id   | 0x85      | 是           |
| #2     | 子服务 id | 0x01/0x02 | 是           |

<br/>

根据 14229 的规范，0x85 的 positive response message 格式为：

| 数值位 | 参数名字                  | 可选值    | 是否为必选项 |
| ------ | ------------------------- | --------- | ------------ |
| #1     | 服务 id + positive 偏移量 | 0xC5      | 是           |
| #2     | 子服务 id                 | 0x01/0x02 | 是           |

<br/>

<br/>

<br/>

# 0x86

TODO：很少看到有客户使用这个服务，后续需要用到的时候，再进行深入的了解。

<br/>

<br/>

<br/>

# 0x22

该服务是用来读取一个或者多个 did 对应的数据的。did 的全程是 dataIdentifier，它是由一个 `uint16` 和一连串二进制数据组成的，可以简单的理解为键值对的关系。此处的 `uint16` 为 did 号。

而读取 did 的这个服务，可以理解是，外部的诊断仪传入 did 号，诊断 server 便根据报文中的 did 号，返回对应的数据。

根据 14229 的规范，0x22 的 request message 的报文结构如下所示。

| 数值位      | 参数名字 | 可选值    | 是否为必选项                                 |
| ----------- | -------- | --------- | -------------------------------------------- |
| #1          | 服务 id  | 0x22      | 是                                           |
| #2,#3       | did      | 0x00-0xFF | 是（每次 22 服务的请求中，至少要有一个 did） |
| .. #n-1，#n | did      | 0x00-0xFF | 否                                           |

<br/>

根据 14229 的规范，0x22 的 response message 的报文结构如下所示。

| 数值位                | 参数名字                      | 可选值    | 是否为必选项                                 |
| --------------------- | ----------------------------- | --------- | -------------------------------------------- |
| #1                    | 服务 id + positive 偏移量     | 0x62      | 是                                           |
| #2,#3                 | did                           | 0x00-0xFF | 是（每次 22 服务的请求中，至少要有一个 did） |
| #4..#(k-1)+4          | Did record，为 did 对应的数据 | 0x00-0xFF | 是（did 对应的数据至少为一个字节）           |
| #n-(0-1)-2,#n-(o-1)-1 | did                           | 0x00-0xFF | 否（至少有一个 did 可读就可以了）            |
| #n-(o-1)..#n          | Did record，为did对应的数据   | 0x00-0xFF | 否（至少有一个 did 可读就可以了）            |

<br/>

<br/>

<br/>

# 0x2A

该服务允许外部的诊断仪发送周期性读取一个或是多个 did 的请求。

在 14229 的规范中，每次 2A 服务传入的 did 数据只包含低两位。其中的高两位固定为 0xF2。

根据 14229 的规范，0x2A 的 request message 的报文结构如下所示。

| 数值位 | 参数名字                         | 可选值    | 是否为必选项                                                 |
| ------ | -------------------------------- | --------- | ------------------------------------------------------------ |
| #1     | 服务 id                          | 0x2A      | 是                                                           |
| #2     | transmissionMode，表示传输的速率 | 0x00-0xFF | 是                                                           |
| #3     | periodicDataIdentifier           | 0x00-0xFF | 否（可以传入任意数量的 did；如果 transmissionMode 为 stopSending，且后续没有 did 存在时，则表示 client 需要将所有的定时读取的 did 都给取消） |

<br/>

根据 14229 的规范，0x2A 的 response message 的报文结构如下所示。

| 数值位 | 参数名字                  | 可选值 | 是否为必选项 |
| ------ | ------------------------- | ------ | ------------ |
| #1     | 服务 id + positive 偏移量 | 0x6A   | 是           |

而周期性返回数据的报文结构如下所示。

| 数值位   | 参数名字                      | 可选值    | 是否为必选项                       |
| -------- | ----------------------------- | --------- | ---------------------------------- |
| #1       | periodicDataIdentifier        | 0x00-0xFF | 是                                 |
| #2..#k+2 | Did record，为 did 对应的数据 | 0x00-0xFF | 是（did 对应的数据至少为一个字节） |

<br/>

<br/>

<br/>

# 0x2C

对于 did 而言，在工具界面配置了当前支持哪些 did，但是存在一种名为 dynamic define by identifier 的 did。这种 did 在工具界面配置，说当前支持这种类型的 did，但是它具体的组成需要由 0x2c 服务来定义。

比如说，已有 did1，did2，did3。其中 did3 是动态 did，那么通过 2c 服务指定，did3 是由 did1 的前四位，加上 did2 的中间四位组成的。

注：在 autosar ap 的规范中，仅支持子服务 id 为 0x01 和 0x03 这两个子服务

根据 14229 的规范，0x2C 的 request message ，子服务为 0x01 的报文结构如下所示。

| 数值位    | 参数名字                                              | 可选值                   | 是否为必选项                |
| --------- | ----------------------------------------------------- | ------------------------ | --------------------------- |
| #1        | 服务 id                                               | 0x2C                     | 是                          |
| #2        | SubFunction                                           | 0x01(defineByIdentifier) | 是                          |
| #3,#4     | dynamicallyDefinedDataIdentifier                      | 0xF2/0xF3，0x00-0xFF     | 是                          |
| #5,#6     | sourceDataIdentifier，表示源 did                      | 0x00-0xFF                | 是（至少要由一个 did 组成） |
| #7        | positionInSourceDataRecord，表示在源头 did 上的偏移量 | 0x01-0xFF                | 是（至少要由一个 did 组成） |
| #8        | memorySize                                            | 0x01-0xFF                | 是（至少要由一个 did 组成） |
| #n-3,#n-2 | sourceDataIdentifier，表示源 did                      | 0x00-0xFF                | 否                          |
| #n-1      | positionInSourceDataRecord，表示在源头 did 上的偏移量 | 0x01-0xFF                | 否                          |
| #n        | memorySize                                            | 0x01-0xFF                | 否                          |

根据 14229 的规范，0x2C 的 request message ，子服务为 0x03 的报文结构如下所示。

| 数值位 | 参数名字                         | 可选值                                      | 是否为必选项                                                 |
| ------ | -------------------------------- | ------------------------------------------- | ------------------------------------------------------------ |
| #1     | 服务 id                          | 0x2C                                        | 是                                                           |
| #2     | SubFunction                      | 0x03(clearDynamicallyDefinedDataIdentifier) | 是                                                           |
| #3,#4  | dynamicallyDefinedDataIdentifier | 0xF2/0xF3，0x00-0xFF                        | 否（如果没有该项，则表示需要清除所有的 ddid；否则则表示删除某个具体的 ddid） |

<br/>

根据 14229 的规范，0x2C 的 response message 的报文结构如下所示。

| 数值位 | 参数名字                         | 可选值               | 是否为必选项                                                 |
| ------ | -------------------------------- | -------------------- | ------------------------------------------------------------ |
| #1     | 服务 id + positive 偏移量        | 0x6C                 | 是                                                           |
| #2     | subfunction                      | 0x00-0x7F            | 是                                                           |
| #3,#4  | dynamicallyDefinedDataIdentifier | 0xF2/0xF3，0x00-0xFF | 否（如果 request 中有 ddid，那么就需要填写此参数，否则则不需要） |

<br/>

<br/>

<br/>

# 0x2E

该服务是用来写 did 对应的数据的。而对于动态定义的 did 来说，是不能够写入的。

根据 14229 的规范，0x2E 的 request message 的报文结构如下所示。

| 数值位   | 参数名字       | 可选值    | 是否为必选项         |
| -------- | -------------- | --------- | -------------------- |
| #1       | 服务 id        | 0x2E      | 是                   |
| #2,#3    | dataIdentifier | 0x00-0xFF | 是                   |
| #4..#m+3 | dataRecord     | 0x00-0xFF | 是，最少应为一个字节 |

<br/>

根据 14229 的规范，0x2E 的 response message 的报文结构如下所示。

| 数值位 | 参数名字                  | 可选值    | 是否为必选项 |
| ------ | ------------------------- | --------- | ------------ |
| #1     | 服务 id + positive 偏移量 | 0x6E      | 是           |
| #2,#3  | dataIdentifier            | 0x00-0xFF | 是           |

<br/>

<br/>

<br/>

# 0x14

clearDiagnosticInformation，该服务是用于删除一个或者多个 DTC 对应的数据。当完全删除 DTC 对应的数据，或者不存在对应 DTC 时，需要返回积极响应，如果在 server 中存在多份 DTC 的数据（比如说可能存在备份的情况），那么同样也要将其删除。

根据 14229 的规范，0x14 的 request message 的报文结构如下所示。

| 数值位   | 参数名字         | 可选值    | 是否为必选项               |
| -------- | ---------------- | --------- | -------------------------- |
| #1       | 服务 id          | 0x14      | 是                         |
| #2,#3,#4 | groupOfDTC       | 0x00-0xFF | 是                         |
| #5       | Memory selection | 0x00-0xFF | 否（为用户自定义的内存序） |

<br/>

根据 14229 的规范，0x14 的 response message 的报文结构如下所示。

| 数值位 | 参数名字                  | 可选值 | 是否为必选项 |
| ------ | ------------------------- | ------ | ------------ |
| #1     | 服务 id + positive 偏移量 | 0x54   | 是           |

<br/>

<br/>

<br/>

# 0x19

readDTCInformation，该服务是用于读取处于某个状态的所有 DTC 对应的数据。

根据 14229 的规范以及 autosar ap 的规范，目前支持的 subfunction 有

| 子服务 id | 含义                                                         |
| --------- | ------------------------------------------------------------ |
| 0x14      | reportDTCFaultDetectionCounter，不需要传入数据，返回当前所有处于 preFailed 的 DTC |
| 0x17      | reportUserDefMemoryByStatusMask                              |
| 0x18      | reportUserDefMemoryDTCSnapshotRecordByDTCNumber              |
| 0x19      | reportUserDefMemoryDTCExtDataRecordByDTCNumber               |

<br/>

## 19 01

reportNumberOfDTCByStatusMask，给定一个状态掩码，返回符合这个状态掩码的 dtc 个数。

其中每个 dtc 的 status 与这个掩码进行 & 操作，都不为 0

| **数值位** | **参数名字**    | 可选值    |
| ---------- | --------------- | --------- |
| 1          | 服务 id         | 0x19      |
| 2          | 子服务 id       | 0x01      |
| 3          | Dtc status mask | 0x00-0xFF |

<br/>

## 19 02

reportDTCByStatusMask，给定一个状态掩码，返回一个 dtc status 的合集。

其中每个 dtc 的 status 与这个掩码进行 & 操作，都不为 0

| **数值位** | **参数名字**    | 可选值    |
| ---------- | --------------- | --------- |
| 1          | 服务 id         | 0x19      |
| 2          | 子服务 id       | 0x02      |
| 3          | Dtc status mask | 0x00-0xFF |

<br/>

## 19 03

reportDTCSnapshotIdentification，返回所有 dtc 的快照数据，返回的数据逻辑为 dtc code + freeze data。

| **数值位** | **参数名字** | 可选值 |
| ---------- | ------------ | ------ |
| 1          | 服务 id      | 0x19   |
| 2          | 子服务 id    | 0x03   |

<br/>

## 19 04 

reportDTCSnapshotRecordByDTCNumber，用于读取某一个 dtc 的某一个快照数据（需要传入快照号），其中当快照号 id 为 ff 的时候，是读取所有的快照数据。

| **数值位** | **参数名字**                      | 可选值    |
| ---------- | --------------------------------- | --------- |
| 1          | 服务 id                           | 0x19      |
| 2          | 子服务 id                         | 0x04      |
| 3，4，5    | Dtc number，表示需要读取的 dtc 号 | 0x00-0xFF |
| 6          | 快照号 id                         | 0x00-0xFF |

<br/>

## 19 06 

reportDTCExtDataRecordByDTCNumber，用于读取某一个 dtc 的某一个拓展数据（需要传入拓展数据号），其中当拓展数据 id 为 ff 的时候，是读取所有的拓展数据。

| **数值位** | **参数名字**                      | 可选值    |
| ---------- | --------------------------------- | --------- |
| 1          | 服务 id                           | 0x19      |
| 2          | 子服务 id                         | 0x06      |
| 3，4，5    | Dtc number，表示需要读取的 dtc 号 | 0x00-0xFF |
| 6          | 拓展数据号 id                     | 0x00-0xFF |

<br/>

## 19 07

reportNumberOfDTCBySeverityMaskRecord，回一个符合条件的 dtc 数。

其中 dtc 的 status 要和 statusmask 做位运算（&）后不为 0，

dtc 的 severitymask 要和 severitymask 做位运算（&）后不为 0。

| **数值位** | **参数名字**    | 可选值    |
| ---------- | --------------- | --------- |
| 1          | 服务 id         | 0x19      |
| 2          | 子服务 id       | 0x07      |
| 3          | DTCSeverityMask | 0x00-0xFF |
| 4          | DTCStatusMask   | 0x00-0xFF |

<br/>

## 19 0a 

reportSupportedDTC，用于读取当前支持的所有 dtc。

| **数值位** | **参数名字** | 可选值 |
| ---------- | ------------ | ------ |
| 1          | 服务 id      | 0x19   |
| 2          | 子服务 id    | 0x0a   |

<br/>

<br/>

<br/>

# 0x31

该服务的全称为 routineControl。在介绍这个服务之前需要介绍 routineIdentifier，为一个 uint16 的值，表示某一个 routine。

而服务 routineControl 表示的是外部的诊断仪或是脚本，想让诊断 server（或是 ECU）执行一段此前已经定义好了的代码逻辑，比如常见的擦除内存，重置或是修改某个参数等。

如果从常见的网络模型上看，可以简单的立即为 routine 就是某个函数，当传入 0x31 0x01 的时候，就是让程序执行某段代码；当传入 0x31 0x02 的时候，就是让程序停止执行某段代码；当传入 0x31 0x03 的时候，就是获取这段代码执行结果的返回值。

根据 14229 的规范，0x31 的 request message 的报文结构如下所示。

| 数值位 | 参数名字                   | 可选值    | 是否为必选项                     |
| ------ | -------------------------- | --------- | -------------------------------- |
| #1     | 服务 id                    | 0x31      | 是                               |
| #2     | subFuntcion                | 0x00-0xFF | 是                               |
| #3,#4  | routineIdentifier          | 0x00-0xFF | 是                               |
| #5..#n | routineControlOptionRecord | 0x00-0xFF | 否（该部分的内容由用户自行定义） |

根据 14229 的规范，目前支持的 subfunction 有

| 子服务 id | 含义                                                         |
| --------- | ------------------------------------------------------------ |
| 0x01      | startRoutine，该服务是用于启动某个 routine                   |
| 0x02      | stopRoutine，该服务是用于停止某个 routine                    |
| 0x03      | requestRoutineResults，该服务是用于获取某个 routine 运行得到的结果 |

<br/>

根据 14229 的规范，0x31 的 response message 的报文结构如下所示。

| 数值位  | 参数名字                           | 可选值    | 是否为必选项                           |
| ------- | ---------------------------------- | --------- | -------------------------------------- |
| #1      | 服务 id + positive 偏移量          | 0x71      | 是                                     |
| #2      | routineControlType，为对应的子服务 | 0x00-0x7F | 是                                     |
| #3,#4   | routineIdentifier                  | 0x00-0xFF | 是                                     |
| #5      | routineInfo                        | 0x00-0xFF | 否（该参数由不同的协议及车厂共同实现） |
| #6...#n | routineStatusRecord                | 0x00-0xFF | 否                                     |

<br/>

<br/>

<br/>

# 0x34

服务名为 requestDownload。此处需要注意的是，UDS 提供了服务用于数据的传输，而在具体数据的传输上，是需要先告知当前的数据流走向的。

requestDownload 表示数据是从 client 传输到 server 上，即上位机传输给 ECU。

根据 14229 的规范，0x34 的 request message 的报文结构如下所示。

| 数值位       | 参数名字                         | 可选值    | 是否为必选项             |
| ------------ | -------------------------------- | --------- | ------------------------ |
| #1           | 服务 id                          | 0x34      | 是                       |
| #2           | dataFormatIdentifier             | 0x00-0xFF | 是                       |
| #3           | addressAndLengthFormatIdentifier | 0x00-0xFF | 是                       |
| #4..#(m-1)+4 | memoryAddress                    | 0x00-0xFF | 是（最少需要有一个字节） |
| #n-(k-1)..#n | memorySize                       | 0x00-0xFF | 是（最少需要有一个字节） |

**dataFormatIdentifier** 需要分为两部分理解：

- Bit7-4 表示数据的压缩方法

- Bit3-0 表示数据的加密方法

如果为 0x00，则表示传输的数据既不需要加密，也不需要压缩。具体的压缩和加密方法，由主机厂自行定义。

<br/>

**adderssAndLengthFormatIdentifier** 也需要分两部分来理解：

- Bit7-4 表示的是 memorySize 所需的字节数

- Bit3-0 表示的是 memoryAddress 所需的字节数

<br/>

**memoryAddress** 表示的是当前的数据具体要写在哪一个内存地址开始的位置。

<br/>

**memorySize** 表示传输数据块的大小。

ECU 需要使用该参数进行判断，最后返回给用户每次可以传输数据的最大大小，如果用户使用了数据压缩，那么此处的大小是压缩前还是压缩后的，需要厂商自行决定。

<br/>

根据 14229 的规范，0x34 的 response message 的报文结构如下所示。

| 数值位 | 参数名字                  | 可选值    | 是否为必选项 |
| ------ | ------------------------- | --------- | ------------ |
| #1     | 服务 id + positive 偏移量 | 0x74      | 是           |
| #2     | lengthFormatIdentifier    | 0x00-0xF0 | 是           |
| #3,#n  | maxNumberOfBlockLength    | 0x00-0xFF | 是           |

**lengthFormatIdentifier** 需要分为两部分理解：

- Bit7-4 表示后续 maxNumberOfBlockLength 的长度

- Bit3-0 为 0，具体的内容为 ISO 保留

<br/>

**maxNumberOfBlockLength** 表示后续的 0x36（transferData）需要传输数据内容的大小最大为多少。

<br/>

<br/>

<br/>

# 0x35

服务名为 requestUpload。此处需要注意的是，UDS 提供了服务用于数据的传输，而在具体数据的传输上，是需要先告知当前的数据流走向的。

requestUpload 表示数据是从 server 传输到 client 上，即从 ECU 传输给上位机。

根据 14229 的规范，0x35 的 request message 的报文结构如下所示。

| 数值位       | 参数名字                         | 可选值    | 是否为必选项             |
| ------------ | -------------------------------- | --------- | ------------------------ |
| #1           | 服务 id                          | 0x35      | 是                       |
| #2           | dataFormatIdentifier             | 0x00-0xFF | 是                       |
| #3           | addressAndLengthFormatIdentifier | 0x00-0xFF | 是                       |
| #4..#(m-1)+4 | memoryAddress                    | 0x00-0xFF | 是（最少需要有一个字节） |
| #n-(k-1)..#n | memorySize                       | 0x00-0xFF | 是（最少需要有一个字节） |

其中关于 `dataFormatIdentifier`，`addressAndLengthFormatIdentifier`，`memoryAddress`，`memorySize` 的描述，

可以完全参见`0x34`中的描述。

<br/>

根据 14229 的规范，0x35 的 response message 的报文结构如下所示。

| 数值位 | 参数名字                  | 可选值    | 是否为必选项 |
| ------ | ------------------------- | --------- | ------------ |
| #1     | 服务 id + positive 偏移量 | 0x75      | 是           |
| #2     | lengthFormatIdentifier    | 0x00-0xF0 | 是           |
| #3,#n  | maxNumberOfBlockLength    | 0x00-0xFF | 是           |

lengthFormatIdentifier 需要分为两部分理解：

- Bit7-4 表示后续 maxNumberOfBlockLength 的长度

- Bit3-0 为 0，具体的内容为 ISO 保留

而 maxNumberOfBlockLength 则表示后续的 0x36（transferData）需要传输数据内容的大小最大为多少。

<br/>

<br/>

<br/>

# 0x36

在介绍完了 0x34 和 0x35 这两个服务之后，可以发现这两个服务都是用来表示后续具体传输数据流的走向，而具体数据的传输，就是用服务 0x36 进行传输的

根据 14229 的规范，0x36 的 request message 的报文结构如下所示。

| 数值位 | 参数名字                       | 可选值    | 是否为必选项                                           |
| ------ | ------------------------------ | --------- | ------------------------------------------------------ |
| #1     | 服务 id                        | 0x36      | 是                                                     |
| #2     | blockSequenceCounter           | 0x00-0xFF | 是                                                     |
| #3..#n | transferRequestParameterRecord | 0x00-0xFF | 否（如果此时是 0x34 对应的数据传输，就必须要有该参数） |

blockSequenceCounter 是从 01 开始计数的，是用来计算当前已经传输数据的大小的。该值是为了保证数据的顺序及完整性传输。

如果循环至 0xFF，则会回到 0x00。

<br/>

根据 14229 的规范，0x36 的 response message 的报文结构如下所示。

| 数值位 | 参数名字                        | 可选值    | 是否为必选项                                           |
| ------ | ------------------------------- | --------- | ------------------------------------------------------ |
| #1     | 服务 id + positive 偏移量       | 0x76      | 是                                                     |
| #2     | blockSequenceCounter            | 0x00-0xFF | 是                                                     |
| #3,#n  | transferResponseParameterRecord | 0x00-0xFF | 否（如果此时是 0x35 对应的数据传输，就必须要有该参数） |

<br/>

<br/>

<br/>

# 0x37

requestTransferExit 是用于表示当前数据传输的终止的。

根据 14229 的规范，0x37 的 request message 的报文结构如下所示。

| 数值位 | 参数名字                       | 可选值    | 是否为必选项           |
| ------ | ------------------------------ | --------- | ---------------------- |
| #1     | 服务 id                        | 0x37      | 是                     |
| #2..#n | transferRequestParameterRecord | 0x00-0xFF | 否（为用户自定义数据） |

<br/>

根据 14229 的规范，0x37 的 response message 的报文结构如下所示。

| 数值位 | 参数名字                        | 可选值    | 是否为必选项           |
| ------ | ------------------------------- | --------- | ---------------------- |
| #1     | 服务 id + positive 偏移量       | 0x77      | 是                     |
| #2..#n | transferResponseParameterRecord | 0x00-0xFF | 否（为用户自定义数据） |

<br/>

<br/>

<br/>

# 0x38

RequestFileTransfer，该服务是用来传输文件或者文件夹。

根据 14229 的规范，0x38 的 request message 的报文结构如下所示：

| 数值位              | 参数名字                | 可选值    | 是否为必选项                        |
| ------------------- | ----------------------- | --------- | ----------------------------------- |
| #1                  | 服务 id                 | 0x38      | 是                                  |
| #2                  | modeOfOperation         | 0x01-0x06 | 是（表示当前对文件处理的操作）      |
| #3,#4               | filePathAndNameLength   | 0x00-0xFF | 是                                  |
| #5...#5+n-1         | filePathAndName         | 0x00-0xFF | 是（文件路径和名字至少为一个字节）  |
| #5+n                | dataFormatIdentifier    | 0x00-0xFF | 否（与具体的 modeOfOperation 有关） |
| #5+n+1              | fileSizeParameterLength | 0x00-0xFF | 否（与具体的 modeOfOperation 有关） |
| #5+n+2..#5+n+2+k-1  | fileSizeUnCompressed    | 0x00-0xFF | 否（与具体的 modeOfOperation 有关） |
| #5+n+2+k..#5+n+1+2k | fileSizeCompressed      | 0x00-0xFF | 否（与具体的 modeOfOperation 有关） |

<br/>

<br/>

根据 14229 的规范，0x38 的 request message 的报文结构如下所示：

| 数值位                | 参数名字                            | 可选值    | 是否为必选项                   |
| --------------------- | ----------------------------------- | --------- | ------------------------------ |
| #1                    | 服务 id + positive 偏移量           | 0x78      | 是                             |
| #2                    | modeOfOperation                     | 0x01-0x06 | 是（表示当前对文件处理的操作） |
| #3                    | lengthFormatIdentifier              | 0x00-0xFF | 否                             |
| #4...#4+m-1           | maxNumberOfBlockLength              | 0x00-0xFF | 否                             |
| #4+m                  | dataFormatIdentifier                | 0x00-0xFF | 否                             |
| #4+m+1..#4+m+2        | fileSizeOrDirInfoParameterlength    | 0x00-0xFF | 否                             |
| #4+m+3..#4+m+3+k-1    | fileSizeUncompressedOrDirInfoLength | 0x00-0xFF | 否                             |
| #4+m+3+k..#4+m+3+2k-1 | fileSizeCompressed                  | 0x00-0xFF | 否                             |

**filePathAndNameLength** 表示的是后续文件路径及名字的长度

<br/>

**filePathAndName** 表示后续的文件路径和名字（如果当前的 modeOfOperation 是 0x05 readDir，那么此处就应该是文件夹）

<br/>

**dataFormatIdentifier** 的具体功能，需参考此前的赘述（如果当前的 modeOfOperation 是 0x02 或者 0x05，那么则不应该有该参数）

<br/>

**fileSizeParameterLength**（或者 **fileSizeOrDirInfoParameterlength**） 记录了后续 `fileSizeUncompressed`（`fileSizeCompressed` 的大小也一样） 的大小（如果当前的 modeOfOperation 是 0x02，0x04，0x05，则不应该有该参数）

<br/>

**fileSizeUncompressed** 表示当前文件未压缩的长度（如果当前的 modeOfOperation 是 0x02，0x04，0x05，则不应该有该参数）

<br/>

**fileSizeCompressed** 表示当前文件被压缩的长度（如果当前的 modeOfOperation 是 0x02，0x04，0x05，则不应该有该参数），如果传输的文件未被压缩，那么值应该和 fileSizeUncompressed 相等
