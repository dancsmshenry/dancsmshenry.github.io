---
title: The Google File System
top: false
cover: false
toc: true
mathjax: true
date: 2022-10-24 12:21:59
password:
summary:
tags:
- Paper
- Distributed
categories:
---







gfs为google内部的文件系统，其开源实现为hdfs，大数据领域标准的开源实现

GFS是一个存储非结构化数据的存储系统，和bigtable（列存储，存储结构化数据，关系模型，表结构）是相对应的

GFS只存储数据，不关心数据的结构和内容是什么；GFS里面只存储字节码，不关心具体的数据是什么 

可能我们只是需要顺序的读取文件的数据，并不需要什么额外的操作

某些场景下，就是不需要sql去对数据进行查看，单纯的只是想要对数据进行读取

而GFS是很多组件的基础，比如说HBASE等kv数据库，它们的底层就是GFS

三种结构：列存储，结构化数据，文件系统存储非结构化数据

# 简介

大规模可拓展容错的分布式文件系统

大规模：TB级的文件大小

拓展：10台能够存入1TB，100台能够存入10TB，水平拓展

容错：100台机器，坏了30台机器，剩下的70台照样能够提供服务，外界无感知，系统内部的错误不会被传播出去

能够运行在廉价的服务器上（有磁盘有网络，就能够运行在上面；或者是虚拟机，只要有磁盘网络即可）

因此这种能够运行在廉价服务器上的系统，极大的降低了研发成本

任何技术的演进都需要极大的降低成本（无论时间还是金钱）研发成本，服务器的成本开销

<br/>

google发现，很多时候业务的需求都是在文件的末尾追加数据（9成以上的需求），也有随机读写的情况，但很少

极少数有删除修改的需求；大部分都是顺序的将数据写到文件中

如果能够支持高性能的顺序写和顺序读的话，就可以cover掉90%的需求

因此支持在文件的尾部数据进行写入（也正是这一需求，导致了api设计上的变化）

而一般的随机写和随机读也是支持的，但不保证性能上的可靠，同时对于随机写也不能保证一致性

而该系统是多机的，所以势必遇到分布式的一致性问题（可能会读取到脏数据，被删除的数据，也可能读到多个客户端读取写入时的脏数据，反正就是会读到不符合预期的数据）

但是会保证最终的一致性，即每个数据至少会被写入到一个副本中

但GFS降低了一致性的预期

<br/>

<br/>

<br/>



# 设计概述

## 需求分析

运行在普通的机器上，机器的失效是常态（全失败和全正常的概率都是很低的，因此至少出现一台机器失败的概率就会很高）

大文件是普遍存在的（九成九的都是大文件，十几兆的几百兆的都有；存储列表信息），小文件也是存在的（比如一些id的存储）（大文件是主导的）

大规模的顺序读写是普遍存在的，但是随机读写也是存在的

也存在多个生产者对同一个大文件进行顺序写的操作

**吞吐优先于延迟**：使用该系统的业务方大部分不是和在线系统相关联的，而是离线分析类型的系统，不会对计算的响应时间有所要求，而是对吞吐量有所要求：因为数据量很大，所以希望在单位时间内处理大量的数据，即把网络带宽打满

而对于延迟，对单个请求的处理速度和处理时间是没有要求的，所以不是那么的在乎延迟，反而更在会一次性能处理多少的数据，即吞吐

比如说有一百个任务，会强调在多少时间内完成所有任务，而不是完成单个任务需要多少时间

因此针对的是离线系统，而不是在线系统

更加注重一秒钟能够处理到底多少个数据，而不再会处理单个数据需要多少秒

并不是说延迟不重要了，而是认为能够把网络的吞吐量给打满，每秒处理更多的数据，这是比单个延迟更加重要的事情

<br/>

<br/>

## 接口设计

需要像linux系统一样，是可以分层组织目录的

对文件的操作，增加数据，删除数据，打开文件，关闭文件，读写文件，顺序读，尾部追加数据（弱化了对文件api的操作）

还可以获取一些文件的元数据

快照：拷贝

<br/>

<br/>

<br/>

# Master节点的操作

整个GFS分为组件，master和chunk等几个组件

其中chunk节点主要是用来存储数据的，因此很多核心逻辑都是master节点实现的

比如说master节点需要执行所有的名称空间操作，管理整个系统里所有chunk的副本

能够决定chunk的存储位置，负责新的chunk和它副本

协调各种各样的系统活动以保证Chunk被完全复制， 在所有的 Chunk服务器之间的进⾏负载均衡，回收不再使⽤的存储空间

## 名称空间管理和锁

类似linux下的文件目录，一个一个文件夹进行嵌套，类似数状结构；可以组成一个path

需要支持并发操作，因此需要对路径节点上读锁，对文件节点上写锁

文件目录被组织成一个多叉树

可以创建和删除文件夹，移动文件夹

用同一个map，key存放目录名，value存放子目录

<br/>

<br/>

## 副本的位置

如何规划不同副本到底应该存放在哪个机房

在磁盘利用率低、最近创建次数、放置距离三者的权衡

<br/>

<br/>

## 创建，重新复制，重新负载均衡

<br/>

<br/>

## 垃圾回收

如果一个副本写入失败了，master会继续让chunk写入副本数据

但是之前写入失败了的数据，是不会被删除掉的（因为GFS为了写入性能的提高，只进行写入追加的操作，不进行删除操作）

因此就会存在垃圾文件

另一方面，磁盘也可能出现损坏的情况，比如说寄存器的零和一发生了跳变，导致数据丢失，造成了副本的失效

<br/>

<br/>

<br/>

# 容错与诊断

一方面是运行的时候保证可用性

另一方面是如果运行的时候失效了，运维的时候进行服务诊断

三个方面解释高可用：（这也是运行时的可用性）

<br/>

方面一：快速恢复（如果集群不可用了，可以在短时间内恢复集群）

其实就是检查点的快速重启

一般来说很多chunkserver的状态信息都是维护在master节点上的，如果master节点挂了，就会造成系统上信息的丢失

而master都是讲数据存储到内存中的

为了进程崩溃或者内存失效，也会去写一个类似redolog的操作日志，到磁盘上，是以紧追加的形式写上去的

比如一般信息的更新，租约的更新等等的信息，都会更新到日志上

同时，不仅要把redolog写到本地磁盘，还要发送给多台其他的机器（影子机器，副本服务器）

而日志会逐渐变多，导致状态恢复的时候需要大量的时间

同时，你比如说在一年内做的数据日志就有100GB，难道还需要从头对这100GB的日志进行恢复操作吗，这是很浪费时间精力的

因此可以参考redis的RDB机制，实现一个写时复制：fork一个新的进程，将此时的数据以一种序列化的机制写入到磁盘中，得到一种快速恢复的快照

然后就可以把这个检查点之间的数据日志全部给删除了

这样的话，master节点的恢复，只需要找到最近的checkpoint节点，并执行后面对应的日志，即可快速恢复

因此又有了checkpoint机制

<br/>

方面二：冗余存储（如果副本丢失了，那么可以通过多余的副本对数据进行恢复）

chunk节点的复制之前说过了

而master节点的复制，master之间存在主从关系

比如说可能存在主master会挂掉，这个时候就需要副master升为主master节点

所以副master需要同步主master节点的数据

<br/>

方面三：数据完整性（能够侦擦到数据中字节级别上的错误；一般通过checksum进行判断）

读写数据的时候都会去校验一下当前数据计算得到的校验和，与checksum是否一致

大概机制：每次写入数据的时候，会将数据按照一定的大小，比如64kb或是128kb的大小，对写入的数据计算一个校验和，并存储起来

而每次读取数据的时候，就会将读取到的数据先算一个校验和，再与已有的校验和进行比较，看看是否相同，

如果不相同，就会给客户端报错

这样做的目的就是，看看在这个存储的过程中，底层的存储介质是否会损坏具体的数据内容，从而保证GFS的可靠性

另一个方面（诊断工具）：

能够打印各类rpc的日志

<br/>

<br/>

<br/>

# 结论与反思

GFS更像是一个技术文档

如果我们想要在工作中推进我们的工作的话，需要做的一点就是

一上来不要先看代码，而是要做数据分析，观察已有系统中是否有尚未解决的问题

通过监控指标，发现已有的问题，从数据指标中发现问题

把问题的痛点给列出来以后，再基于这些痛点

给出一些假设（比如说GFS一上来就说组件的失效是一种常态，所以要更加注重容错）

比如说我要做的事情，就是用于服务哪些场景的，说明具体的场景

说明系统的定位，以及当前改进的意义

紧接着是设计系统的接口，需要从用户的角度来分析如何使用这些接口以及使用场景

再者就是剖析系统中的每个组件，深入解决每个组件中的问题，分析已有的问题

这些事情都做好以后，就需要做数据分析，将前后的指标进行对比

最后总结与回顾

<br/>

<br/>

<br/>

# reference

https://www.bilibili.com/video/BV1rw411R7rH/