---
title: CMU 15-445 11-Query Execution Part I
top: false
cover: false
toc: true
mathjax: true
date: 2022-12-29 21:53:35
password:
summary:
tags:
- Database
- CMU 15-445
categories:

---





# Processing model

执行模型有哪些，执行计划是如何运作的

DBMS的执行模型规定了系统是如何执行查询计划的

根据不同的工作负载（TP or AP），在执行计划上有不同的权衡

<br/>

<br/>

## Approach 1 iterator model

迭代器模型，也叫火山模型（Volcano Model），或者流式模型（Pipeline Model）

每个算子都要实现一个`next()`方法

当父算子调用当前算子的`next()`方法的时候，当前算子就会向父算子返回一条数据（或者是返回NULL，表示当前算子运行结束）

如果当前算子有子算子的话，就需要循环的调用子算子的`next()`方法，得到下一层的数据

需要多少条数据，就会有多少次这样的链式的函数调用

<img src="\medias\11-Query-Execution-Part-I\iterator model_01.png" style="zoom: 150%;" />

<br/>

<br/>

### Example

1号算子循环调用`child.next()`算子，即2号算子

2号算子分为两部分，要先执行`left.next()`算子（hash join中构建hash表），再执行`right.next()`算子（将数据放入hash表中映射）

`left.next()`算子，即3号算子，则需要一行一行的向上返回数据；4、5号算子同理

<img src="\medias\11-Query-Execution-Part-I\iterator model_02.png" style="zoom:150%;" />

而在执行2、3、4、5号算子的过程中，1号算子会因为2号算子没有返回数据而阻塞（因为只有下面的算子返回了数据，上面的算子才能继续运行）

<br/>

<br/>

**几乎所有的DBMS都用到了火山模型**（或者它的变种）

一条条数据向上吐出（数据流处理），和直观上认为DBMS的运行是不一样的（直观上认为是把所有的数据都计算好，再往上返回）

某些算子存在阻塞阶段

- 比如join算子在构建hash表的时候，是不会返回数据的
- 又或者说subqueries子查询
- 再比如order by排序，因为需要将所有的数据都获取了以后，进行排序才能够返回

使用这种方法非常方便控制数据的输出

- 比如说此时要求`limit 100`，那么只需要输出到100条数据的时候停止即可
- 而不需要控制底层算子具体需要读取多少条数据，只需要控制算子的出口输出即可

性能上的一些问题

- 部分算子依旧存在阻塞

- 每一条数据的输出都是依靠函数调用，可能出现函数栈溢出

<img src="\medias\11-Query-Execution-Part-I\iterator model_03.png" style="zoom:150%;" />

<br/>

<br/>

## Approach 2 materialization model

物化模型（一般大众直观上认为的一种做法）

每个算子的输入就是当前语句需要执行的所有数据，输出的是语句的所有结果

即将当前语句涉及的所有数据都处理好了，才返回给上一级

<br/>

每一个算子都有一个out数组，用于存储当前算子处理好了的数据，并作为结果返回给上一级算子

模型中所有的算子都只会被调用一次

<img src="\medias\11-Query-Execution-Part-I\materialization model_01.png" style="zoom:150%;" />

<br/>

一些偏向OLTP的数据库，比如交易的数据库会使用这种数据库

- 因为涉及交易的操作很多都是点查询，只涉及很少的数据
- 无论是最终结果还是中间结果，数据量都很小，DBMS能够轻松负载

因此这种做法并不适用于OLAP的数据库，因为中间结果太大，容易爆内存

<img src="\medias\11-Query-Execution-Part-I\materialization model_02.png" style="zoom:150%;" />

<br/>

<br/>


## Approach 3 vectorized/batch model

向量化模型（分批模型），属于是方法一和方法二的中间派，就是两种方法的结合

和`iterator model`一样有`next()`方法，但是返回的不是一条数据，而是一批数据

也和`materialization model`一样有`out`数组，但返回的不是全部数据，而是部分数据

<img src="\medias\11-Query-Execution-Part-I\vectorization model_01.png" style="zoom:150%;" />

<br/>

<br/>

适用于OLAP类型的数据库

- 因为既能使得中间的结果集不太大，又能使得函数的调用次数相对少一点

在底层指令集上的优势：

- 背景：intel有一个能够同时处理多个数据的指令（即在一个机器指令的周期就能够将数据全部计算好），即**AVX指令集**
- 这种模型的底层就可以利用这种批处理的指令，实现一次性处理多条数据
- 也叫做向量执行模型

<img src="\medias\11-Query-Execution-Part-I\vectorization model_02.png" style="zoom:150%;" />

<br/>

<br/>

<br/>

# Plan processing direction

执行语句时，函数调用的方向（是从根节点的函数往下调用叶子节点的函数，还是从叶子结点的函数往上调用根结点的函数）

PS：数据流动的方向一直是从下往上的

<br/>

方法一：**top to bottom**

- 从上往下执行，先执行根结点，再执行叶子节点

<br/>

方法二：**bottom to top**

- 从下往上执行，先执行叶子节点，然后叶子节点调用根结点

<br/>

<br/>

<br/>

# Access methods

从磁盘读取数据、存储数据的方式有哪些

主要就是研究如何读表中的数据

<img src="\medias\11-Query-Execution-Part-I\access methods.png" style="zoom:150%;" />

<br/>

<br/>

## Sequential scan

顺序扫描，从磁盘中把数据页放到内存中，每条记录每条记录的扫描遍历（说白了就是全表遍历）

```python
for page in table.pages:	#	外层循环遍历数据页
    for t in page.tuples:	#	内存循环遍历数据页里面的数据
        if evalPred(t):
            #	do something
```

如果需要某个数据页页，就先在buffer pool中去找，如果有的话，就把它取出来遍历；否则就去硬盘中去找

在执行过程中的算子需要保持一个指针，把这个指针当作迭代器一样去扫描遍历数据（同时记录上一次读取到哪里的数据了）

<br/>

<br/>

### Optimizations

类似全表扫描等操作，存在很多优化的可能

方法一：prefetching

在执行计划之前，提前将数据从磁盘中预先取出来

<br/>

方法二：buffer pool bypass

在全表扫描时，假如用过的数据后续不会再用了，那么就不用将数组再存储在buffer中了，而是用完后就丢掉

<br/>

方法三：parallelization

多线程并行执行：启用两个线程，一个线程从前扫到中间，另一个线程从中间扫到后面

<br/>

方法四：zone maps

背景：假设有一个需求，要扫描大于100的数据值；但是有可能某个数据页里面所有的值都小于100，如果把该页放入内存，就会造成资源的浪费

所以希望用一个map，用来**记录关于这个页**的相关信息（比如说max，min，avg，sum等），以便DBMS筛选掉某些页，从而优化全表扫描的速度

<img src="\medias\11-Query-Execution-Part-I\zone maps.png" style="zoom:150%;" />

缺点：

- 浪费空间；如果该信息是存放在每个页的话，那么就无法达到筛选的目的（因为我们本来就是希望利用zone map减少无用数据页的读取），所以必然是存储在额外的数据页的
- 不利于数据的存放；如果原始数据可能发生了一点点修改，那么map可能会因此发生很大的修改，不方便维护，甚至可能造成写放大，即单单写入一个数据表的数据，结果需要修改过多zone map上的数据

<br/>

方法五：late materialization

延迟物化

只需要把符合条件的记录的id（offsets）给返回，在最后返回数据的时候才将数据进行物化（最后才回表），减少了扫描的工作量

适用于**列存储**的数据库，因为算子一般只对列的数据进行处理（而行存储是将一连串数据一起存储，不方便获取单独列的数据）

<br/>

<br/>

## Index scan

查询扫描走索引的一些条件：

- 索引有没有我们需要的属性
- 索引是否含有我们需要的输出列
- 索引的值域
- 谓词的压缩
- 是否为唯一索引

<br/>

假如有两个索引，应该选择哪一个索引效果更好？

<img src="\medias\11-Query-Execution-Part-I\index scan.png" style="zoom:150%;" />

选择该索引后，剩下的数据，即需要再排查的数据越少，就选那一个

比如说上面要选择age < 30的，那么如果选择age的索引，最后剩下的数据更少，那么就选择age的索引

<br/>

<br/>

## Multi-index scan

比如上面的问题，多索引的思路是用一个索引筛出数据A，用另一个索引筛出数据B，然后对这两个数据进行取交集

<img src="\medias\11-Query-Execution-Part-I\multi-index scan.png" style="zoom:150%;" />

在PG中，multi-index scan的底层就是用bitmap实现的

<br/>

<br/>

<br/>

# Modification queries

此前对于数据的研究都是读取，并没有涉及到数据层面的修改

而涉及数据的修改的语句的执行逻辑，和读取的逻辑是截然不同的

<br/>

比如说，对于数据的插入、更新和删除，都是要检查其是否符合数据库的约束的，即一致性（比如unique等），同时还要维护数据的索引

<br/>

update/delete

- 下面的算子将要删除的记录id返还给上一层（而不是整条数据），然后用这个id回表删除记录
- 删除算子和更新算子都要记录自己对哪些数据进行了操作

<br/>

insert

- 算子内部将数据物化，将数据整个插入
- 需要子算子将行记录物化好，则当前的insert算子只要将记录插入即可

<br/>

<br/>

## Update query problem

假设要更新一个索引上所有的数据，使其全部加上100

update的操作流程是，按照索引的顺序，每读一个数据就把该数据先从index中移除，接着给这个数据+100，然后再放回去

而如果不记录当前update的算子对于哪些数据进行了操作，

比如说我们希望age小于30的人全部加10岁，某个人现在11岁

那么在第一次加10岁以后，变成了21岁，但我们没有记录对哪些数据进行了操作，那么就会重复给这个数据再加10岁

造成数据更新的重复

因此无论是update还是delete，都要记录下自己对哪些数据进行了操作

这个问题被简称为halloween problem，即万圣节问题

<br/>

<br/>

<br/>

# Expression evaluation

谓词表达式的一些计算（谓词表达式本质上就是一个计算式，涉及到不同的符号，比如等于不等于等符号）

<img src="\medias\11-Query-Execution-Part-I\expression evaluation.png" style="zoom:150%;" />

<br/>

<br/>

在DBMS中，一个通用的处理方案是：

将谓词表达式拆分为一个树状的流程图，即分为几个不同的算子

<img src="\medias\11-Query-Execution-Part-I\expression evaluation_01.png" style="zoom:150%;" />



<br/>

<br/>

不过这种流程存在一些优化的方向：

<img src="\medias\11-Query-Execution-Part-I\expression evaluation_02.png" style="zoom:150%;" />

<br/>

这里的`WHERE`需要先读取`B.value`，然后计算`? + 1`的值是多少，最后再将二者进行比较看是否相等

而每次都要计算一遍`? + 1`的值是多少，效率非常低

一个优化的方式就是先直接将`? + 1`的值计算好，后续直接调用即可

<br/>

这就有点类似java里面的JIT

- just in time，java运行的是字节码，相当于把代码编译为了字节码，而不是二进制；于是有一种思路就是，发现一些重复利用的代码，于是就将其编译成了二进制，提高效率，即再使用这类代码的时候就变为二进制执行了
- 把一些热点的代码段编译为二进制，从而提高效率
- PS：jit是在执行的时候判断

- 而与JIT对立的是AOT，执行之前就判断，还没运行的时候就将重复的字节码编译为二进制

<br/>

<br/>

<br/>

# Conclusion

一个相同的执行计划，不同的执行模型，执行方法也会不同

在排查大部分DBMS的问题的时候，查询是否走索引是一个经常需要注意的方向

按照树形的方法进行查询是非常灵活的，但是会很慢，所以需要后续的一些优化
