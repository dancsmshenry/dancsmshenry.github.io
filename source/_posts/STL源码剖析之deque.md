---
title: STL源码剖析之deque
top: false
cover: false
toc: true
mathjax: true
date: 2022-10-21 01:00:57
password:
summary:
tags:
- STL
- deque
categories:
---





# 定义

是一种**双向开口的连续线性空间，可以在头尾两端分别做元素的插入和删除**

- 允许O（1）时间内对头端进行元素的插入或移除操作

没有容量的概念，因为它是以动态的分段连续空间合成，随时可以增加一段新的空间并连接起来

- 一旦有必要在deque的前端或尾端增加新空间，便配置一段定量连续空间，串接在整个deque的头端或尾端

- 因此非必要不使用deque，如果要对deque进行排序，就要先把deque复制到vector上，将vector排序，再复制会deque

deque的最大任务，便是在这些分段的定量连续空间上，维护其整体连续的假象，并提供随机存取的借口，

避开了“重新配置、复制、释放”的轮回，代价则是复杂的迭代器架构

<br/>

<br/>

<br/>

# deque实现

## 迭代器

**在64位机器、g++10.3下，deque::iterator的大小为32**

![](/medias/STL源码剖析之deque/deque迭代器示意图.png)

deque的迭代器总共有四个指针：

- `cur`（指向当前元素在buffer中的位置）

- `first`（指向当前buffer的头部）

- `last`（指向当前buffer的尾部）

- `node`（指向当前的缓冲区对应的迭代器在中控器上的位置）

![](/medias/STL源码剖析之deque/deque迭代器源码.png)

<br/>

## 组成

**在64位机器、g++10.3下，deque的大小为80**

deque采用一块所谓的map（不是map容器）作为**主控**

这里所谓map是一小块连续空间，其中每个元素（称为节点node）都是指针，指向另一段（较大的）连续线性空间，称为**缓冲区**

缓冲区才是deque的储存空间主体，SGI STL 允许我们指定缓冲区大小，默认值0表示将使用512bytes缓冲区

![](/medias/STL源码剖析之deque/deque中中控器、缓冲区、迭代器的相互关系.png)

deque主要由四个部分组成：

- `start`（头iterator，指向deque的第一个元素）32字节

- `finish`（尾iterator，指向deque最后一个元素的下一个节点）32字节

- `pointer`（map_pointer；map是一块连续的内存空间，上面存放的是指向buffer的指针；所以map_pointer是指向该数组的一个指针；也就是`T**`类型）8字节

- `map_size`（size_type，map中继器的大小，表示map内有多少个指针）8字节

<br/>

## 源码

![](/medias/STL源码剖析之deque/deque数据结构.png)

<br/>

<br/>

<br/>

# 基本用法

## deque的构造

```cpp
//	构造函数的四种方式
deque<string> words1{"the", "is", "deque"};
deque<string> words2(words1.begin(), words1.end());
deque<string> words3(words1);
deque<string> words4(5, "YES");
```

<br/>

## deque的迭代器

```cpp
//	iterator正向迭代器，+1是向右边走
for (deque<string>::iterator it = w.begin(); it != w.end(); ++ it) {}
//reverse_iterator反向迭代器，+1向左走
for (deque<string>::reverse_iterator it = w.rbegin(); it != w.rend(); ++ it) {}
```

<br/>

## deque的常用函数

```cpp
word4.front();	//	获取第一个元素

word4.back();	//	返回最后一个元素

word4.size();	//	返回容器的大小

word4.push_back("NO");	//	把元素放入末尾

word4.pop_back();	//	移除最后一个元素

word4.push_front("SS");	//	把元素放到头部

word4.pop_front();	//	移除第一个元素

word4.empty();	//	判断是否为空

//	erast 移除元素
words4.erase(words4.begin());	//	移除某个位置的元素
words1.erase(words1.begin() + 2, words1.end());	//	移除某个区间的元素

//max_size

//shrink_to_fit

//at

//assign

//emplace_back

//emplace_front

//swap
```

<br/>

<br/>

<br/>

# API的使用

## insert

```cpp
//	作用：将元素插入到指定的位置上
words.insert(words.begin() + 1, words4.begin(), words4.end());	//	第一个参数是位置，后面是要插入的容器的内容
words.insert(words.begin() + 3, "strat");	//	指定位置插入元素
words.insert(words.begin() + 3, 5, "IS");	//	位置，重复次数，重复的数据
```

由于deque是可以两端进行扩充的，插入元素又会引入元素移动问题，进而带来拷贝构造的开销

所以在插入时首先进行判断插入位置距离首位哪边比较短，移动距离较短的一边，最大化的减少开销

![](/medias/STL源码剖析之deque/deque的insert_01.png)

![](/medias/STL源码剖析之deque/deque的insert_02.png)

<br/>

<br/>

<br/>

# to do list

- https://blog.csdn.net/CHYabc123456hh/article/details/121449313
- https://blog.csdn.net/qq_15041569/article/details/110943325
- 侯捷的视频
- 《STL源码剖析》
