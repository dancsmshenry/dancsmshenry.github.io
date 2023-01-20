---
title: CMU 15-445 21-Introduction To Distributed Databases
top: false
cover: false
toc: true
mathjax: true
date: 2022-12-19 21:07:48
password:
summary:
tags:
- Database
- CMU 15-445
categories:

---



# Parallel vs Distributed

并行数据库和分布式数据库的区别

<br/>

## Parallel DBMS

多个节点在物理上是放在一起的（比如说是放在同一个机房中）

物理节点之间是通过高速的局域网连接的

节点之间的通信消耗是很小的，可以忽略不计的（光纤连接的）

比如说Oracle数据库集群之类的并行数据库集群

<br/>

<br/>

## Distributed DBMS

多个节点在物理上不是放在一起的（存在一定距离，比如说一个在亚洲，另一个在欧洲）

节点之间是通过公网连接的

节点之间的通信的消耗是不可忽略的

<br/>

针对单节点DBMS中的一些组件，是可以复用到distributed DBMS中的

比如说SQL的优化查询，分布式事务的并发控制，以及分布式数据库的日志及恢复

<br/>

<br/>

因此，当说到分布式数据库的时候，要分清到底是哪一种类型的DBMS

<br/>

<br/>

<br/>

# System architecture

在分布式DBMS中，可以指定CPU可以直接访问哪些共享资源

而指定的共享资源的范围，则直接影响CPU之间的协调、以及如何在DBMS中检索数据

<br/>

## Shared memory

<img src="shared memory.png" style="zoom:150%;" />

<br/>

CPU之间的分布式，即CPU之间通过network进行通信

而各个CPU都共享同一块内存和磁盘

每一个DBMS都知道对方的存在

如果CPU需要通过网络才能够操作内存的话，那么内存的优点就没有了

分布式数据库用的少，几乎没有

主要用在服务器上，即多路服务器（比如四路服务器，总共就有四个CPU，中间通过高速总线相连）

或超级计算器，多个核通过高速网络连接

<br/>

<br/>

## Shared disk

<img src="shared disk.png" style="zoom:150%;" />

<br/>

<img src="shared disk_02.png" style="zoom:150%;" />

CPU和内存打包，单体之间用网络通信

节点间共享磁盘资源

<br/>

优点：存算分离，计算能力和存储能力解耦（计算能力差加CPU，存储能力差加磁盘），无论存储还是计算都可以单独扩容

缺点：缓存一致性（即内存的同步）

- A节点更新了数据，但是没有实时刷盘，只是在本地的内存更新了，而B节点此时需要访问数据，那么就出现问题了
- 或者说，A节点将数据更新到了磁盘上，但是其他节点的缓存并没有更新，就会造成数据的不一致

<br/>

运用的非常广泛（主要是现在的数据库都开始走向云化，存算分离有利于扩容）

<img src="shared disk_01.png" style="zoom:150%;" />

<br/>

<br/>

## Shared nothing

<img src="shared nothing.png" style="zoom:150%;" />

<br/>

<img src="shared nothing_01.png" style="zoom:150%;" />

每一个DBMS都有自己的CPU、内存、硬盘

DBMS的节点之间只通过网络进行通信

<br/>

优点：能够获得更好的性能（因为硬盘也是在本地，所以访问性能更快）

缺点：

- 数据的一致性更难处理

- 没有办法独立的扩容（因为数据的存储和计算都是在同一个节点上；比如说新加一个硬盘，会导致数据重新分布）

<br/>

也有不少的平台使用这种架构

<img src="shared nothing_02.png" style="zoom:150%;" />

<br/>

<br/>

<br/>

# Design issues

一些设计上的问题：

应用应该如何查找数据？（应用应该向哪一个节点请求数据）

分布式DBMS如何执行查询？（如何执行SQL）

- Push query to data
- Pull data to query

分布式DBMS如何保证数据的一致性和正确性？

<br/>

<br/>

## Homogenous Nodes

均匀、一致的节点

集群中的每个节点的设计、职责、任务、运行逻辑、角色都是一样的（只是负责的数据不同）

<br/>

<br/>

## Heterogenous Nodes

每个节点的角色是不一样的

节点之间不是平等关系，允许一个节点管理多个其他节点

<br/>

比如mongodb

当查询到Router节点的时候，Router节点会向Config Server节点获取具体数据的信息，然后再到指定的区域进行查询

<img src="heterogenous architecture.png" style="zoom:150%;" />

<br/>

<br/>

## Data transparency

数据透明，即用户是不需要了解数据具体的物理位置，或是数据是如何分区的（或是数据副本的情况）

理想情况下，用户使用分布式DBMS和单节点DBMS应该是一样的

<br/>

<br/>

<br/>

# Partitioning schemes

因为数据都是分布在不同的数据节点上的

因此DBMS需要在每个分区上执行查询操作，将结果组合在一起才是最终答案

<br/>

<br/>

## Naive table partitioning

理想情况下，每个节点都有足够的空间来存放整张数据表

因此可以将整张数据表分配给单个节点

而比较理想的查询是，对数据的查询不跨节点，并且访问模式是统一的

<img src="naive table partitioning.png" style="zoom:150%;" />

<br/>

这种方法的缺点是，如果某个表实在是太大了，可能一个节点的容量装不下

而如果某个表又太小了，单独存在一个节点中又有点浪费

<br/>

<br/>

## Horizontal partitioning

水平分区

将一个表的数据水平分开，分配到不同的节点上

比如说可以以某一列作为水平分区的标准（比如下图便是对某一列的值进行hash，取hash值进行分区）

<img src="horizontal partitioning.png" style="zoom:150%;" />

<br/>

<br/>

水平分区下，最友好的查询便是查询谓词中包含分区的那一列数据

垂直分区（竖着切分数据，将数据切分为两张表）的情况在分布式数据库中是用的比较少的

<br/>

水平分区面临的问题：

- 如果查询不是按照分区来的列进行查找的话，就会造成每个节点的数据都要遍历一遍（比如分区是按照age列分的，但是查找却是按照name进行查找的）
- 或者说，想要添加一个新的数据节点，扩容上复杂度会很高

所以基于上述的扩容问题，提出了一致性hash算法（consistent hashing）

<br/>

<br/>

### Consistent hashing

一致性hash算法

比如说hash值在0-P1之间的数据，就会存储在P1节点，以此类推

<img src="consistene hashing_01.png" style="zoom:150%;" />

<br/>

<br/>

如果此时需要新添加一个数据节点，比如P4

那么就需要将P3中，归属于P2-P4范围的数据移动到P4中（这种扩容后的代价小于此前扩容的代价）

<img src="consistene hashing_02.png" style="zoom:150%;" />

<br/>

<br/>

同时，在这种算法下，还可以指定数据的副本数量

比如说这里执行数据的副本数量要为3，那么P1上的数据就需要复制到P6和P2上面

<img src="consistene hashing_03.png" style="zoom: 150%;" />

<br/>

<br/>

## Logical partitioning

逻辑分区，一般是`shared disk`架构

数据都存储在一个统一的Storage中

每个节点本身不存储数据，而是指定需要处理的数据分区

比如下图中的上面节点，处理的就是id=1和id=2的数据

下面的节点处理的就是id=3和id=4的数据

<img src="logical partitioning.png" style="zoom:150%;" />

<br/>

<br/>

## Physical partitioning

物理分区，一般是`shared nothing`架构

数据的存储和计算查询都是在同一个节点上

<img src="physical partitioning.png" style="zoom:150%;" />

<br/>

<br/>

<br/>

# Single-node vs distributed

在单节点的情况下，数据都是在本地操作的，并发控制的处理都是在本节点上，方便处理

而分布式DBMS的情况下，事务的处理需要跨多个节点（对一个节点上的数据进行操作，别的节点是不知道的；需要非常昂贵的代价去处理）

因此，如果我们的系统需要在多节点上处理分布式事务，就需要一种多节点并发控制协议去协调

<br/>

而在分布式的情况下，有以下两种处理的方式：集中式的和非集中式的

<br/>

## Centralized coordinator

用Coordinator来管理数据是否可以读取

应用的每次commit request都是向Coordinator请求，同时Coordinator上会记录数据的状态（比如读锁写锁等）

这种方案用的比较少（因为它本质上还是一个单节点的DBMS，存在性能上的缺陷）

<img src="centralized coordinator.png" style="zoom:150%;" />

<br/>

后续演化为了中间件模式

<img src="centralized coordinator_01.png" style="zoom:150%;" />

<br/>

<br/>

## Decentralized coordinator

分散式的布局

应用会向分区中的其中某个节点发出请求，首先接收到该节点请求的节点会变为此次事务的`Master Node`

<img src="coordinator_01.png" style="zoom:150%;" />

<br/>

然后`Master Node`会给予应用反馈，应用就可以去其他节点的位置对数据进行操作

<img src="coordinator_02.png" style="zoom:150%;" />

<br/>

操作完毕后就会去Master Node上进行commit

Master Node会检查事务数据是否可以提交

<img src="decentralized coordinator.png" style="zoom:150%;" />

<br/>

<br/>

<br/>

# Distributed concurrency control

分布式的并发控制是需要多个事务在多个节点上同时并发

当然，单节点的并发控制也是可以移植到分布式系统中的

<br/>

但是，这在分布式中会有以下几个挑战：

副本数据节点的同步

网络通信上的开销

节点的容错（事务执行到一半时，节点崩溃该如何处理）

时钟偏移（系统时钟在不同的节点中是不同步的）

<br/>

<br/>

## Distributed 2PL

在分布式的情况下，因为不能够实时同步事务管理的信息（比如锁的情况），导致管理上出现问题

比如说这里的2PL，事务的锁的信息是不能够实时同步的

可能会导致各自一方都认为自己是正确的，但是最后数据汇总的时候又会出现问题

<img src="distributed 2PL.png" style="zoom:150%;" />



