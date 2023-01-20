---
title: CMU 15-445 18-Multi-Version Concurrency Control
top: false
cover: false
toc: true
mathjax: true
date: 2022-12-01 02:38:24
password:
summary:
tags:
- Database
- CMU 15-445
categories:

---







# Multi-version concurrency control

多版本并发控制协议（常常和2PL或TOO一起实现并发控制）

对于DBMS中的每一个数据，都会去记录数据的所有版本（包括历史版本和当前版本）

DBMS会维护当前所有数据对象的，所有历史版本和当前版本：

- 当事务写入数据的时候，DBMS会创建该数据对象的一个新的版本
- 当事务读入数据的时候，DBMS会读取当前事务启动时，该数据存在的最新版本

<br/>

<br/>

为什么会有MVCC的思路？

从写数据的角度考虑：

- 在2PL中，写数据会加上写锁，这会导致其他的事务无法读取该数据
- 但，有可能其他的事务只是需要**读取一个历史版本的数据**，那么只要给该事务提供一个原数据的副本，就可以使得两个事务并发执行
- 从中发现，如果我们可以保留历史版本的数据，那么就可以提高并发度（因为不会阻塞读操作）

<br/>

从读数据的角度考虑：

- 在2PL中，读取数据会上读锁，这会导致其他的事务无法写入该数据
- 但，其他的事务可能只是给原数据添加了一个新的版本，并没有覆盖原来的数据
- 这样的话，读取数据的一方，可以继续读取原有版本的数据；写入数据的一方，可以继续写入新的版本的数据

<br/>

<br/>

总结：

**Writers do not block readers**（留下当前数据的历史版本，从而事务的写操作就不会阻塞其他事务的读操作）

**Readers do not block writers**（读取数据的历史版本，写入数据变成为数据添加新的版本，从而读取数据不阻塞写入数据）

Read-only txns can read a consistent **snapshot** without acquiring locks（只读的事务，相当于**无锁**的读取一个**一致性**的**快照**）

- 可以理解为，当前事务对数据的读取，并不受数据库动态的影响
- 读到的都是事务开始时的那个版本

使用时间戳来记录当前数据的版本号

同时方便DBMS的回滚（`time-travel`）

- 比如说想要回滚到DBMS三分钟之前的时候的数据，直接指定版本号读取即可

<br/>

<br/>

<br/>

# Example

版本链表中的begin表示该版本数据开始的时间，end表示该版本数据截止的时间（如果没有写的话，就代表是至今）

同时，全局会维护一个`txn table`，用于互相查明事务的状态

<img src="\medias\18-Multi-Version-Concurrency-Control\txn status table.png" style="zoom:150%;" />

<br/>

<br/>

## Example1

T1读数据会检查当前的版本，发现此时版本为T0，因此就直接读取

T2写数据，发现当前版本小于自身，因此在table中添加一条新的记录（该记录的begin为当前记录的版本号）

<img src="\medias\18-Multi-Version-Concurrency-Control\mvcc-example_01.png" style="zoom:150%;" />

<br/>

<br/>

此后，T1又要读数据A，就得找到当前事务对应的版本（即历史版本）读取数据

<img src="\medias\18-Multi-Version-Concurrency-Control\mvcc-example_02.png" style="zoom:150%;" />

<br/>

<br/>

## Example2

T1对数据A的读写、T2对数据A的写入，参考Example1（读历史版本，写入新版本）

<br/>

T2对数据A的读取：

此时T1的数据还没有提交，T2不能读取T1还未提交的数据（避免脏读）

因此T2读取的是A0时刻的数据

PS：可以看出来单单MVCC是无法实现可串行化的（因为可串行化中，T2读取到的应该是T1时刻修改后的数据，但MVCC读到的却是更早的数据）

<img src="\medias\18-Multi-Version-Concurrency-Control\mvcc-example_03.png" style="zoom:150%;" />

<br/>

T2对数据A的写入：

此时T2要修改数据，发现T1有一个未提交的事务数据（即发现了一个未提交的新版本），所以会wait到T1结束，才能继续修改

T1发生在T2之前，那么T2对数据写的版本必然是最终版本

如果T2不阻塞，直接写了新版本的数据

后续T1又重新写了一遍，逻辑上就会出现错误了

所以T2必须要等到T1commit，才能给数据添加上新的版本

<br/>

T1对数据A的读取：读取当前事务中上一次添加的版本A1时的数据

<img src="\medias\18-Multi-Version-Concurrency-Control\mvcc-example_04.png" style="zoom:150%;" />

<br/>

当T1事务commit以后，T2事务才可以继续往下写数据

<img src="\medias\18-Multi-Version-Concurrency-Control\mvcc-example_05.png" style="zoom:150%;" />

<br/>

<br/>

**Oracle的最高隔离级别快照隔离（snapshot隔离）**，依靠的就是**MVCC**

只有`MVCC`的话，是无法实现可串行化的，所以一般都是结合其他方法实现并发的，比如说TO，OCC，2PL

MVCC不仅仅是并发控制的手段，更是DBMS管理事务的手段

几乎所有的DBMS都实现了MVCC

<img src="\medias\18-Multi-Version-Concurrency-Control\mvcc-example_06.png" style="zoom:150%;" />

<br/>

<br/>

<br/>

# Concurrenct control protocol

MVCC常常和其他的并发控制协议结合在一起

<img src="\medias\18-Multi-Version-Concurrency-Control\concurrency control protocol.png" style="zoom:150%;" />

<br/>

<br/>

<br/>


# Version storage

新老版本（不同版本）的数据是如何存储的

DBMS会使用一个指针，接着建立一个链表记录每个版本的版本号

<br/>

<br/>

## Append only storage

简单追加

每次向DBMS中给数据追加新的版本，都相当于给数据表中追加了一条新的记录，通过指针将不同的版本记录链接起来，组成版本链

所有数据的所有版本，都存放在同一个表（`Main Table`）里面

<img src="\medias\18-Multi-Version-Concurrency-Control\append-only storage.png" style="zoom:150%;" />

<br/>

追加一个新的数据记录：

首先要插入最新的数据记录

接着找到此时除去当前记录外最新的版本，将该版本的指针指向这个新的数据记录

<br/>

<br/>

`Main table`中链表的两种实现思路

<img src="\medias\18-Multi-Version-Concurrency-Control\version chain ordering.png" style="zoom:150%;" />

<br/>

第一种是将新的数据追加到链表后面（`Oldest-to-Newest`）

- 生成新版本时，将老版本的指针指向新版本
- 所以访问最新记录时，需要遍历老记录（造成读放大）

第二种是将新的数据追加到链表前面（`Newest-to-Oldest`）

- 生成新版本时，将新版本的指针指向老版本
- 所以访问某个版本的记录时，需要从新记录开始遍历到指定版本

<img src="\medias\18-Multi-Version-Concurrency-Control\O2N and N2O.png" style="zoom:150%;" />

<br/>

<br/>

## Time-travel storage

<img src="\medias\18-Multi-Version-Concurrency-Control\time-travel storage.png" style="zoom:150%;" />

main table存储的是当前最新的数据，time-travel table存储的是历史的数据

- main table中的value是最新版本的数据，pointer则指向time-travel table上的历史数据，version是版本号

<br/>

数据的写入：将老版本的数据复制到time-travel table中，将新版本数据写入main table中，同时调整指针指向（新版本的指针指向老版本）

数据的回滚：通过main table中最新版本的指针，找到对应的历史版本

<br/>

比如说，总共有十行记录

那么main table就只有十行记录的最新版本，而time-travle table中就可能会存放很多的历史版本（这些历史版本都用链表连在一起）

<br/>

time-travel也是append-only的存储方式，只是新老版本在不同的表空间中。这种方式有利于回收老版本记录，但同时产生了写放大

<br/>

<img src="\medias\18-Multi-Version-Concurrency-Control\time travel storage.png" style="zoom:150%;" />

<br/>

<br/>

## Delta storage

如果每次只修改了一点点数据，就要把整份数据都放到time-travel table中，那么无疑是一种浪费

因此一种改进方案就是只存储增量，即存储数据的变化

<br/>

main table存储原数据，delta storage segment存储每次修改的增量（具体修改了哪些部分）

<img src="\medias\18-Multi-Version-Concurrency-Control\delta storage.png" style="zoom:150%;" />

<br/>

<br/>

如果想读取历史版本，就要调用delta storage segment中的记录逐条回滚

优点：可以节约历史版本大小

缺点：查看历史版本（或回滚）复杂度高，即恢复（回滚）的时候需要逐步读delat storage segment（可以理解为用时间换取空间）

<img src="\medias\18-Multi-Version-Concurrency-Control\delta storage.jpg" style="zoom:150%;" />

<br/>

PS：MySQL使用的就是这种方法，不过MySQL存储的是undo段

<br/>

<br/>

<br/>

# Garbage collection

背景：DBMS不可能无限存储历史的版本，所以要删除掉一些历史版本

<br/>

垃圾回收的宗旨：

- 如果任何活跃的事务都看不到这个版本（或是说不需要这个版本），那么这个版本就直接删掉了

  - 例如：有个事务的版本是1，但当前活跃事务的版本都是10以上的，那么事务1的版本就可以删除了

  - 或者说，在快照隔离中，如果所有的事务都不需要它了，就要把它删掉

- 如果一个事务发生了abort，就需要删除该版本

<br/>

需要考量的问题：

- 如何发现这些版本

- 什么时候删掉历史版本

<br/>

<br/>

## Tuple level

以元组（行记录）为粒度（范围），清理过期记录

遍历行记录，寻找哪些没有用的行记录

<br/>

### background vacuuming

开启一个后台线程对当前发生的事务和历史版本进行扫描对比，如果有数据的版本是小于当前所有的活跃事务的版本，就要清理掉

<img src="\medias\18-Multi-Version-Concurrency-Control\tuple-level gc.png" style="zoom:150%;" />

<br/>

优化技巧：

- 后台线程会对所有的数据进行扫描，浪费时间
- 而如果当前的数据页被更新过了就标记一下，后续就扫描那些被标记过的数据页即可，而不是全表扫描

<br/>

<br/>

### cooperative cleaning

合作清理

执行事务的语句在检索版本的时候

同时查看一下有哪些版本是没有用的

发现没有用的版本，就删除

<img src="\medias\18-Multi-Version-Concurrency-Control\tuple-level gc(cooperative cleaning).png" style="zoom:150%;" />

<br/>

<br/>

## Transaction-level

以事务为单位进行回收，清理旧事务的数据版本

<br/>

<img src="\medias\18-Multi-Version-Concurrency-Control\transaction-level gc.png" style="zoom:150%;" />

每次修改数据时，同时记录修改数据之前的旧版本

过一段时间后，DBMS决定多少版本号之前的事务都可以干掉了，那么就可以遍历事务，然后把数据的老版本给干掉

<br/>

<br/>

<br/>

# Index management

研究在MVCC（多版本）下，如何对索引进行管理

主键索引指向的是版本链表的第一个，并且一般是物理地址（比如说某个数据具体在哪一个page的哪一个slot）

如果一个事务修改了主键的值，就要把数据先删除，后插入

<br/>

比较麻烦的是辅助索引的处理，下图是辅助索引管理的两大流派：

<img src="\medias\18-Multi-Version-Concurrency-Control\index management.jpg" style="zoom:150%;" />

<br/>

<br/>

## Logical pointers

键（`key`）存储的是被索引的那一列的数据

值（`value`）记录的是逻辑地址（比如说记录的是主键的值，或者行id的值），即逻辑索引

索引指向一个"中间指针"，即逻辑指针，这个中间指针再指向主表存储的元组的位置（某个页面的某个位置）

<br/>

优点：

- 如果数据发生了更新，那么只需要修改主键索引的地址（因为辅助索引指向的是主键索引的位置，不用批量修改辅助索引）

- 对于数据的写入比较友好：如果更新某条记录，则这条记录相关的所有索引都不需要更新，只需要更新"中间指针"指向新的元组的位置即可

<br/>

缺点：

- 存在读放大问题，所有索引访问数据都需要先访问"中间指针"，再跳转到实际数据存储位置，即存在**回表**的过程

<img src="\medias\18-Multi-Version-Concurrency-Control\index pointers_02.png" style="zoom:150%;" />

<br/>

PS：MySQL InnoDB就是使用逻辑指针的方式，所有索引都指向主键，通过主键再去访问真实的数据

<br/>

<br/>

## Physical pointers

键（`key`）存储的是被索引的那一列的数据

值（`value`）记录的是物理索引（比如说某个数据具体在哪一个page的哪一个slot）

<br/>

优点：

- 对于读比较友好，索引指向元组的实际位置，直接就可以访问到元组，无需通过中间指针进行跳转（不需要回表）

<br/>

缺点：

- 如果辅助索引记录的是数据记录的物理地址，那么当有新的版本数据到来的时候，所有的辅助索引上数据记录都要修改（特别是在辅助索引数量很多的情况下，复杂度`upup`）
- 因此不利于写，如果更新了某条记录的位置，则相关的索引都需要更新，造成写放大

<img src="\medias\18-Multi-Version-Concurrency-Control\index pointers_01.png" style="zoom:150%;" />

<br/>

PS：PostgreSQL使用这种方式，所以更新记录时成本较高

<br/>

<br/>

<br/>

# MVCC index

DBMS的索引一般是不会保存数据的版本号的

但MVCC有快照，因此索引需要保存冗余的数据（即冗余的键）

即一个键，可能会指向多个值（多个版本）

<br/>

为什么要存储冗余的数据？

T1第一次读数据A

T2修改了数据A后又删除了数据A

T3在原来的位置插入了新的数据A

问题是：T3插入数据的时候，形成了新的版本

而因为T3认为此时没有数据，此时产生的新版本号是A1

导致版本号出现了重复的情况，那么此时T1重复读取数据的时候，就会出现问题

所以就需要存储冗余的键值，以此实现隔离级别（比如此时的数据A，需要维护T1指向的A1的版本和T3指向A1的版本）

<img src="\medias\18-Multi-Version-Concurrency-Control\mvcc duplicate key problem.png" style="zoom:150%;" />

<br/>

因此每个索引上需要维护多个版本的数据，更需要额外的逻辑去维护唯一约束等问题

<br/>

<br/>

<br/>

# MVCC deletes

DBMS一般不会在物理上将数据从数据库中删除

只有当该数据的所有版本在逻辑上被删除（即逻辑上该数据的所有版本都没有用的时候），才会将数据真正删除

因此，一般数据的删除都是指逻辑上的删除，而不是物理内存上的删除（需要保存历史版本，进行一些处理）

所以，需要一些方法来查看数据是否在逻辑上被删除

<br/>

<br/>

## Deleted flag

在行记录上加上一个列，用于判断数据是否被删除

<br/>

<br/>

## Tombstone tuple

给这个行记录添加一个新的版本（是没有数据的），相当于是一个墓碑

代表这个版本之前所有的版本，都是被删掉的

而在这个墓碑之后新的版本，是正常添加的

<br/>

<br/>

<br/>

# MVCC implementations

<img src="\medias\18-Multi-Version-Concurrency-Control\mvcc implementations.png" style="zoom:150%;" />

比较core的部分：

protocol（MVCC和什么手段结合）

version storage（版本管理，版本存储的方案）

garbage collection（垃圾回收）

辅助索引（是logical还是physical的）

<br/>

<br/>

<br/>

# Conclusion

几乎所有的关系型数据库都实现了MVCC，但一般是搭配着其他的并发控制协议使用（比如2PL，OCC等）

当然，也有部分NoSQL也在使用，比如RocksDB

<br/>

<br/>

<br/>

# Thinking

关于读写冲突（写读冲突，同理）

- 普通2PL，因为有事务A先拿了读锁，以至于另一个事务B拿不了写锁，另一个事务B必须等到事务A放锁了以后，才能继续往下走拿到写锁
- 而MVCC，事务A读不加锁，直接读，然后事务B写一个新的版本放入storage，接着如果事务A继续读的话，读历史版本即可
- 由此可见2PL和MVCC都可以解决读写冲突，但MVCC没有锁，没有阻塞，提高了效率和并发度

<br/>

而因为是用了类似TO的时间戳，MVCC也解决了写写冲突的问题

<br/>

<br/>

现有的2PL、严格2PL + 间隙锁就可以实现很多的隔离级别，为什么还需要MVCC？

- 我觉得使用MVCC可以提高并发度，一定程度的不阻塞读（依靠的是历史版本数据）
- 2PL其实是可以实现的，但是会减损一些并发度，所以要使用MVCC（使得原本的范围变得宽松而合理一些）
- 从另一个角度说，MVCC需要2PL，因为单靠MVCC无法实现可串行化（参考Example2）
