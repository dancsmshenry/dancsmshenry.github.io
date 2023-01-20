---
title: CMU 15-445 23-Distributed OLAP Databases
top: false
cover: false
toc: true
mathjax: true
date: 2022-12-19 21:08:31
password:
summary:
tags:
- Database
- CMU 15-445
categories:

---



# Decision support systems

决策支持型数据库

分析当前的数据，以便对未来公司的发展做预计，帮助公司做商业决策

在这种AP型的数据库中，数据（表）的结构分为以下两种：`star schema`和`snowflake schema`

<br/>

## Star schema

星型结构，一张主表被若干张维度表包围

数据的每一个维度都可以抽象出一张表，然后和主表的外键相连（不同维度之间没有关联）

<img src="/medias/23-Distributed-OLAP-Databases\star schema.png" style="zoom:150%;" />

<br/>

优点：查询时更加迅速（相比Snowflake schema，因为不会造成过多表的join）

<br/>

缺点：造成**数据的冗杂**

可能每个同种类型的产品，都有相同的字段，如果对于每个产品都需要写入这个相同的字段，就会造成数据的冗余

- 解决方案：用一个新的数据表记录每个类型的产品，然后用一个外键与其相连，以此减少数据的冗余

<br/>

造成**数据类型不一致**

比如说针对产品属于哪一种类型，有些人可能会写入低端，而有些人可能会写入low，导致数据类型的不统一

- 解决方案：和上面一样，用一个新的数据表记录，再用外键连接

<br/>

<br/>

## Snowflake schema

雪花模型是在基于星型模型之上拓展来的，每一个维度可以再扩散出更多的维度，根据维度的层级拆分成颗粒度不同的多张表

<img src="/medias/23-Distributed-OLAP-Databases\snowflake schema.png" style="zoom:150%;" />

<br/>

优点：减少维度表的数据量；占用更少的存储空间（不需要存储冗余的数据）

<br/>

缺点：需要额外维护更多的维度表（导致join的查询上需要多表连接，查询效率低下）

<br/>

<br/>

<br/>

# Execution Models

<br/>

## Push query to data

将查询发送给带有数据的节点（`shared nothing架构`）

数据节点尽量在本地对数据进行一些过滤的操作，最后再将结果合并统一

数据在哪儿，就将查询发送到对应的节点上

<br/>

比如说这里的查询，会将查询的操作传给每一个有对应数据的节点上

<img src="/medias/23-Distributed-OLAP-Databases\push query to data.png" style="zoom:150%;" />

<br/>

<br/>

## Pull data to query

将数据传输到需要执行查询的节点上（`shared disked架构`）

节点需要什么数据，就拉取什么数据进行查询

<br/>

每一个节点需要查询的范围不同，因此节点向Storage拉去的数据也都各不相同

<img src="/medias/23-Distributed-OLAP-Databases\pull data to query_01.png" style="zoom:150%;" />

<br/>

<br/>

## Observation

从其他节点获取的数据和DBMS查询的中间临时结果都存储在缓冲池中

但是如果发生了崩溃，中间临时结果则会丢失

那么DBMS该如何处理这种情况呢？

<br/>

<br/>

## Query fault tolerance

在大部分的`share nothing`架构的分布式OLAP中，都是假定执行期间事务是不会失败的

- 因为一旦有一个节点失败了，那么整个查询都会失败，此时只需要重新查询即可

<br/>

因此，可以让DBMS在查询执行的过程中保留中间结果的快照，以便在节点崩溃的时候进行恢复

<br/>

例如下面的查询，会将临时查询得到的数据存储在Storage中

<img src="/medias/23-Distributed-OLAP-Databases\query fault tolerance_01.png" style="zoom:150%;" />

<br/>

那么即使后面该节点崩溃了，其他节点也可以去Storage上读取中间结果，而不用从头再开始查一次

<img src="/medias/23-Distributed-OLAP-Databases\query fault tolerance_02.png" style="zoom:150%;" />

<br/>

一般来说用这种方式的数据库比较少

这种机制有点像Flink中的checkpoint

<br/>

<br/>

<br/>

# Query Planning

在分布式OLTP的场景下，查询语句并不复杂，中间数据并不多，涉及到的数据量也不多，不需要太多的如何进行查询计划

但是在分布式OLAP的场景下，长时间海量的查询，多表查询，再加上数据的不同分布，需要考虑如何进行数据的查询

<br/>

此前在单节点的DBMS中的一些查询优化，依然适用于分布式环境：

- 谓词下推
- 数据的早物化或晚物化
- join顺序的排序

<br/>

而分布式情况下，更加困难的是：

- 数据都存放在不同的节点上
- 同时还要考虑网络传输的成本

<br/>

## Physical operators

将SQL的语句转化为物理查询计划，即若干个查询算子

然后将查询算子拆分为几个小节，让不同的节点去执行

是最多DBMS使用的方法

<br/>

<br/>

## SQL

将SQL语句，从字符串的角度切分为不同的节点

然后让不同的节点去执行（不同的节点对SQL语句进行解析和优化）

基本上没有DBMS使用这种方法

<img src="/medias/23-Distributed-OLAP-Databases\SQL.png" style="zoom:150%;" />

<br/>

<br/>

## Observation

其实，分布式的join查询效率高度依赖于数据表的分区情况

因此，分布式OLAP的查询计划，需要根据数据的不同分区，进行不同的处理

<br/>

最简单的方法就是将整张表的数据都放到同一个节点，然后执行join操作

但，一方面这会导致分布式DBMS失去并行性

而另一方面，大量数据在网络中传输，开销巨大的同时，传输效率也会降低

<br/>

<br/>

<br/>

# Distributed Join Algorithms

分布式OLAT的join算法

比如说要连接表R和表S的数据，那么DBMS需要做的

是基于当前节点已有的数据，将当前节点中可以进行join的部分进行join（而不再是像此前，将所有的数据都集中进行join）

<br/>

当相应的数据元组到达了同一个节点上，就可以使用此前单机DBMS中的join算法了

<br/>

下面列举两个表（表R和表S）进行join的情况：

需要执行的SQL：`SELECT *FROM R JOIN S ON R.id = S.id`

<br/>

<br/>

## Scenario 01

表R的数据是根据id（目标列；查询列）进行分区的，而表S的数据是每个节点都有表S中所有的数据（即每个节点都有表S的副本）

<img src="/medias/23-Distributed-OLAP-Databases\scenario 01_01.png" style="zoom:150%;" />

<br/>

这种情况下的join是比较简单的，因为只需要在每个节点中

将每个节点所持有的R表的数据和S表的数据进行join，得到结果

然后再将每个节点的结果汇总在一起，便是查询的最终结果

<img src="/medias/23-Distributed-OLAP-Databases\scenario 01_02.png" style="zoom:150%;" />

<br/>

<br/>

## Scenario 02

表R和表S的数据都是按照id（目标列；查询列）进行分区的，并且分区的数据范围都是相同的

<img src="/medias/23-Distributed-OLAP-Databases\scenario 02_01.png" style="zoom:150%;" />

<br/>

只需要在每个节点上完成join的操作，最后汇总在一起就是最终结果

<img src="/medias/23-Distributed-OLAP-Databases\scenario 02_02.png" style="zoom:150%;" />

PS：如果每个分区的数据范围是不一致的话，对于每个节点的join

就需要强制将对应范围内的数据预先复制一份到本地，然后再进行操作

<br/>

<br/>

## Scenario 03

表R的数据是按照id（目标列；查询列）进行分区的，而表S的数据则是按照Val（非查询列）进行分区的

<img src="/medias/23-Distributed-OLAP-Databases\scenario 03_01.png" style="zoom:150%;" />

<br/>

此时对于每个节点的join操作，都需要从其他节点的位置，获取整个表S的副本

然后再进行操作，最后将结果汇总

<img src="/medias/23-Distributed-OLAP-Databases\scenario 03_02.png" style="zoom:150%;" />

<br/>

<br/>

## Scenario 04

表S和表R都不按照id（目标列；查询列）进行分区

<img src="/medias/23-Distributed-OLAP-Databases\scenario 04_01.png" style="zoom:150%;" />

<br/>

这种情况是最麻烦的，需要转化为Scenario 01的情况

对于每个节点，都需要先指定当前节点需要处理的数据

比如节点1需要处理id在1-100范围内的数据，节点2需要处理id在101-200范围内的数据

然后将划分好范围内的数据，迁移到指定的节点上

然后变化为Scenario 01的情况

<img src="/medias/23-Distributed-OLAP-Databases\scenario 04_02.png" style="zoom:150%;" />

<br/>

<br/>

## Semi-join

半连接（查询的结果只需要左表上的数据列）

很朴素的思路：检测左半边的数据是否可以和右半边的数据进行连接；如果可以，就保留左半边的数据

例子：`SELECT R.id FROM R JOIN S ON R.id = S.id WHERE R.id IS NOT NULL`

<br/>

有些DBMS是支持`SEMI JOIN`的语法的，如果不支持的话可以换为`EXISTS`

上述语句可以替换为下述查询：

<img src="/medias/23-Distributed-OLAP-Databases\semi-join_02.png" style="zoom:150%;" />

<br/>

针对上述这种朴素的思想，可以进一步的优化：

只传输需要查询的那一部分数据（比如这里只传输R表的id列），而不用将整个表都传输

<img src="/medias/23-Distributed-OLAP-Databases/semi-join_03.png" style="zoom:150%;" />

<br/>

<br/>

<br/>

# Cloud Systems

越来越多的数据库厂商提供数据库产品服务，即`DBaaS`

可以理解为，将数据库和数据库运行的具体环境（CPU、存储、硬盘等）打包

然后给用户提供使用该产品的接口（比如说可能是一个ip地址）

客户可以直接在这个ip地址上对DBMS进行操作

<br/>

而另一方面，`shared-nothing`和`shared-disk`，这二者的界限也因为数据库的云化而变得逐渐模糊

比如说我们买一个虚拟服务器，但这个服务器上的硬盘可能也是厂商虚拟出来的（不存在CPU、内存和硬盘在同一个物理机上的情况）

而厂商的实现手段可能是`shared-disk`架构，即存算分离（虚拟出多个硬盘、CPU等资源）

使得用户好像是在使用`shared-nothing`架构一样

PS：现在很多厂商都在将原有的`shared-nothing`架构转向`shared-disk`架构

<br/>

云厂商的数据库可以提供更加丰富的服务，比如说Amazon S3

可以在存储层对数据进行过滤，即在云的场景下，存储层可以实现更加丰富的功能

<br/>

<br/>

## Managed DBMS

DBMS的设计理念上保持不变，而是让传统的DBMS在云环境上运行

并将DBMS和其运行的云端环境打包，以此作为软件产品，对外提供服务（比如腾讯云、阿里云等）

可以理解为是将传统的DBMS是运行在云厂商的虚拟环境上

<br/>

这种类型价格便宜，适合刚刚转向云端的厂商

<br/>

<br/>

## Cloud-Native DBMS

这种类型的DBMS从设计之初就是为了能够运行在云环境中的

首选`shared-disk`架构（主要是存算分离、方便扩容）

比如SnowFlake，Google BigQuery，Amazon Redshift，Microsoft SQL Azure

<br/>

<br/>

## Serverless Databases

在此之前，云厂商的客户都是一致使用着服务器等资源，无论此时服务器上是否有工作需要运行

而serverless DBMS，会根据服务器上的工作负载，动态的调度资源

<br/>

无服务器，可以理解为客户使用的存储资源和计算资源都不是客户单独一人占有的

是从一个较大的存储缓冲池或是计算缓冲池中抽离出来的

当客户不再需要的时候又会归还回去

<br/>

<br/>

## Disaggregated componsents

可以像组装玩具一样，利用不同的插件，根据需求，满足不同数据库的需求

<img src="/medias/23-Distributed-OLAP-Databases/disaggregated components.png" style="zoom:150%;" />

<br/>

<br/>

## Universal formats

很多数据库之间的互通，一个比较难处理的事情就是数据页格式的不同

而不同系统之间，数据的传输，很多都是依赖于CSV，JSON，XML等文件格式

当然，也有一些致力于解决这些问题的开源项目

<img src="/medias/23-Distributed-OLAP-Databases/universal formats.png" style="zoom:150%;" />





