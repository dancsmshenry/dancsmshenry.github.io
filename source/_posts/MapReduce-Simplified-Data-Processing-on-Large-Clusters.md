---
title: 'MapReduce: Simplified Data Processing on Large Clusters'
top: false
cover: false
toc: true
mathjax: true
date: 2022-10-23 10:43:04
password:
summary:
tags:
- Paper
- Distributed
categories:
---





# mapreduce的背景

随着业务的增长，待处理的数据集越来越多，单机无法在规定时间内对海量数据进行处理

因此需要同时使用多台机器对数据进行处理

而大规模的数据处理，需要同时应对**多机并行协同，网络通信，处理错误，提高执行效率**等问题

但这些问题会严重的降低开发效率（业务的处理方不仅需要对原有业务进行分析处理，还需要对基础架构出现的问题进行维护），耗时耗力

因此**Jeff Dean**设计了一种新的编程模型 **MapReduce**

是为了编写在普通机器上运行的大规模并行数据处理程序而抽象出来的编程模型

为解决**多机并行协同，网络通信，处理错误，提高执行效率** 等通用性问题的一个编程框架

<br/>

<br/>

<br/>

# mapreduce的定义

![](map和reduce.png)

最早来自于对Lisp语言中map/reduce原语的借鉴

经过谷歌大量重复的编写数据处理类的程序，发现所有数据处理的程序都有类似的过程：

> 将一组输入的数据应用map函数返回一个k/v对的结构作为中间数据集，并将具有相同key的数据输入到一个reduce函数中执行，最终返回处理后的结果。

这种计算框架的优点是非常利于并行化：`map`的过程可以同时在多个机器上运行，`reduce`的过程也是一样

所有的依赖和协调的过程都被隐藏于`map`与`reduce`函数的数据分发之间（`reduce`需要的数据，需要先经过`map`过程）

有一点细节：**map和reduce都是可以各自并行执行，但reduce执行的前提条件是所有的map函数执行完毕**

<br/>

但`mapreduce`想要落地，就必须要考虑工程上的永恒问题：**可用性**与**性能**

大规模的机器失效是一种必然现象，因此不能因为某个`map`任务的失效而导致整体的崩溃

所以对于大规模分布式程序来说 能够应对局部性失败的容错性与性能同等重要

这是一个必要的问题，**分布式的容错性本质上就是如何在不可靠的硬件之上构建可靠的软件**

<br/>

简而言之，一个成熟的工业级实现`MapReduce`就是一个**利用普通机器组成的大规模计算集群进行并行的,高容错,高性能的数据处理函数框架**

<br/>

<br/>

<br/>

# mapreduce的应用场景

**分布式Grep**（分布式正则匹配），**URL访问频次统计**，**倒转Web链接图**，**每个主机的关键词向量**，**倒排索引**，**分布式排序**

<br/>

<br/>

<br/>

# mapreduce的实现

![](mapreduce的实现.svg)

步骤一：将用户给定的数据文件按照一定的大小切分为M块（每块的大小从16MB到64MB，用户可自定义大小）

- 然后`MapReduce`库会在集群的若干台机器上启动程序的多个副本
- `MapReduce`库的各个副本有一个特殊的节点——主节点，其它的则为工作节点
- 主节点用于将任务分配个各个工作节点

步骤二：被分配`map`任务的工作节点读取对应的输入区块内容

- 从输入数据中读取kv对，并传给map函数
- 由map函数生成的kv对都缓存在内存中

步骤三：缓存在内存中的数据会被周期性的由划分函数分成R块，并被写入本地磁盘

- 数据在本地磁盘的位置会被传回给主节点
- 后续主节点会将这些位置再传给reduce工作节点

步骤四：map任务完成后，reduce工作节点通过主节点获取了数据的位置后，会调用RPC去磁盘读取对应数据

- 当reduce工作节点读取完数据后，会将这些数据按key值进行排序，这样相同key值的kv对就会被排列在一起
  - 为啥要排序：因为Reduce操作的本质就是对相同的key聚合为一个list，再传入给reduce函数去执行，为了实现这种聚合，就需要将数据排序
- 如果数据太多了，就需要外部排序

步骤五：reduce工作节点遍历排序好的中间数据，并将遇到的每个中间key和与它关联的一组中间value传递给用户的reduce函数

- reduce函数会将输出写入由reduce划分过程划分出来的最终输出文件的末尾

步骤六：当所有的map和reduce任务都完成后，主节点唤醒用户程序

<br/>

工程实现上的一些细节

主节点会维护多个数据结构，会存储记录每个map和reduce任务的状态（空闲、处理中、完成），和每台工作机器的ID（对应非空闲的任务）

同时，主节点是将map任务产生的中间文件的位置传递给reduce任务的通道，所以需要存储每个已完成的map任务产生的R个中间文件的位置和大小

map节点的任务：读取kv对，执行map函数，输出kv对

reduce节点的任务：先将kv对按照k值进行排序，并相同k值的value聚合为list，再交给reduce函数去执行，最后输出kv对

<br/>

<br/>

<br/>

# mapreduce的容错

假设一台机器发生故障的概率为0.001，现在有一万台机器，那么这一万台机器同时正常工作的概率为$$0.999^{1000}$$

即0.00004517335，所以非常需要对机器的故障进行容错处理

## map节点的容错

主节点通过周期性的ping-pong心跳机制感知map节点的状态，如果心跳超时认为节点失败

并将当前worker上的map task传递给其他worker节点完成，同时记录已经完成的任务的状态

<br/>

## reduce节点的容错

reduce产出的文件是一个持久性的文件，存在副作用（**不是很明白有啥副作用**）

因此每次reduce被重新分配后要重命名一个新的文件，防止与损坏的文件冲突

<br/>

## 主节点的容错

对于任务执行的元数据产生的中间态可以保持在一个恢复点文件中

当节点崩溃重启后，可以从最近的一个恢复点重新执行mapreduce任务（有点类似mysql中的checkpoint机制）

<br/>

## 其他容错

所有的持久化操作都会有一定程度上的副作用

- 比如写入数据写到一半，任务失败，然后重写数据，会导致数据的冗余写入
- 同时可能会误判任务失败；主节点开启了一个新任务执行，同时存在两个任务写同一个文件

解决方案：

保证map与reduce产生的文件在执行过程中先存储在临时文件中（以时间戳命名）

等到提交文件时，将其原子的重命名为最终文件（linux 内核中 重命名操作是有原子性的保证的）

<br/>

<br/>

<br/>

# mapreduce的优化和技巧

## 利用局部性原理

分布式系统中网络带宽非常昂贵，因此需要尽量减少数据在网络中的传输

因此，可以将map任务分配给那些本地就有输入文件的机器节点上，减少数据的传输

同时利用流处理思想优化shuffle过程：

- 当一个map任务完成后通知main进程后，main进程立即通知reduce任务拉取其中一份文件
- 而不必等到所有map任务全部执行完毕后进行网络传输，以此提高了并行性

<br/>

## 任务的粒度

应该配置多少个任务执行map和reduce？

一些经验性的配置是：

- map任务通常为输入文件总大小除以64M的值（这源于底层的分布式文件系统是以64m为一个chuck进行存储的，即GFS）
- reduce的数量通常是map任务的一半
- 同时，为了发挥机器本身的多核特性，一台机器上可以指定多个map和reduce任务来执行，通常是任务总数的百分之一

<br/>

## 备用任务

可能出现长尾延迟的情况，即某些任务执行的时间过长，从而拖累整个任务的执行时长

解决办法：

- 当仅剩下1%的任务时，可以启动备用任务，即同时在两个节点上执行相同的任务
- 这样只要其中一个先返回即可结束整个任务，同时释放未完成的任务所占用的资源

<br/>

## 划分函数

一般对于数据的划分，都是按照key的值进行划分排序到对应的中间文件中

而从工程经验上看，完全可以根据具体的业务需求进行划分

比如说可以将一个主机下的文件划分到一起，或是相关的定制划分方法

<br/>

## 顺序保证

有时我们需要支持对数据文件按key进行随机访问，或者有序输出，并且为了减少reduce任务的负担

输出的每个map任务的中间文件都是保证按key递增有序的

<br/>

## 合并函数

map后得到的同一种key的kv对会有很多，比如说词频统计中，某些谓词的频率就很高

解决办法：预处理，在shuffle之前对其进行一次reduce操作，将这种<are,1>进行合并变为<are,100000>，减少需要传输数据的大小节省网络带宽

<br/>

## 输入和输出类型

有时map 、reduce 函数的输入类型并不是纯文本的，这种情况下如果能输入输出结构化类型是一种理想的情况

这需要在map、reduce函数之前实现一个类型适配器的组件，同时也可以实现read接口

不仅仅从文件中读取数据，也可以从数据库等数据源来读取

<br/>

## 略过坏记录

可能数据集中有错误的记录，因此我们的mapreduce框架就需要跳过这些错误，并捕获执行时的异常

每个map任务要捕获异常，通过安装信号的方式，在程序退出之前执行安装的信息函数把执行到的文件的行号offset等信息发送给主节点。

主节点在下次调度的时候，将这些offset处的记录作为黑名单列表传递给新的map任务，执行时会对此处的记录跳过执行

<br/>

## 本地执行

为了方便调试对应的mapreduce程序，mapreduce提供单机多进程的实现可以有效的进行本地debug发现问题

<br/>

## 状态信息

分布式系统的可观测性尤为重要,  通过在ping-pong过程中将每个worker节点的工作状态进行上报，存储在main进程中

并提供可访问的网页来展示系统运行的信息，从而实现可解释性

<br/>

## 计数器

如何在map reduce的处理进行埋点统计？以实现用户自定义的指标监控?  

需要创建一个原子计数器的对象，由用户在map 和 reduce的函数中在发生某些事件时对其进行累加

并通过ping-pong的心跳中将数据携带回main进程累加进去，但要注意每次消息的幂等性来保证不会导致重复累加或者少累加了计数的情况

<br/>

<br/>

<br/>

# reference

https://hardcore.feishu.cn/docs/doccnxwr1i2y3Ak3WXmFlWLaCbh

https://hardcore.feishu.cn/docs/doccn1XcAYOjDLG7PtY3DIh0q4d#
