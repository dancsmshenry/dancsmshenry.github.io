---
title: STL源码剖析之map
top: false
cover: false
toc: true
mathjax: true
date: 2022-10-22 11:28:41
password:
summary:
tags:
- STL
- map
categories:

---

# STL中的红黑树

## 特点

`RB-tree`不仅是一个二叉搜索树，而且必须满足以下规则：

1、每个节点不是红色就是黑色

2、根节点是黑色

3、如果节点为红，其子节点必须为黑

4、任一节点到NULL（树尾端）的任何路径，所含的黑色节点数必须相同

![](RB-tree.png)

<br/>

## 插入节点

to do part

<br/>

## RB-tree的节点设计

`_rb_tree_node_base`存放`color`，`parent`，`left`，`right`等数据，同时实现了`minimum`和`maxinum`函数

`_rb_tree_node`继承了`_rb_tree_node_base`，同时存放`value_field`节点值

![](RB-tree的节点设计.png)

<br/>

## RB-tree的迭代器设计

`_rb_tree_base_itreator`存放`_rb_tree_node`，同时实现了`increment`和`decrement`函数

`_rb_tree_itreator`继承了`_rb_tree_base_itreator`，同时重载了`*，->，++，--`等运算符

![](RB-tree的迭代器设计.png)

`RB-tree`的迭代器属于双向迭代器，但不具备随机定位能力

<br/>

## RB-tree的数据结构

![](RB-tree的数据结构.png)

<br/>

## RB-tree的元素操作

<br/>

<br/>

<br/>

# map

## 定义

`map`的特性是，所有元素都会根据元素的键值自动被排序，`map`的所有元素都是`pair`，同时拥有实值（`value`）和键值（`key`）

`pair`的第一个元素被视为键值，第二元素被视为实值

![](map中pair的设计.png)

`map`不允许两个元素拥有相同的键值

底层是`RB-tree`实现的，所以插入删除查找都是$O(logn)$

<br/>

## 迭代器

对map中的元素进行操作时，之前原有元素的迭代器不会因此失效

map的iterators只能修改pair的实值，不能修改其键值

- 因此map iterators既不是一种constant iterators，也不是一种mutable iterators

<br/>

## 源码

![](map的数据结构.png)

<br/>

## 基本用法

```cpp
#include <map>
#include <iostream>
#include <string>
using namespace std;

int main() {
    map<string, int> maps;
    //插入若干元素
    maps["jack"] = 1;
    maps["jane"] = 2;
    maps["july"] = 3;

    //以pair形式插入
    pair<string, int> p("david", 4);
    maps.insert(p);

    //迭代输出元素
    map<string, int>::iterator iter = maps.begin();
    for (; iter != maps.end(); ++iter) {
        cout << iter->first << " ";
        cout << iter->second << "--";
        // david 4--jack 1--jane 2--july 3--
    }
    cout << endl;

    //使用subscipt操作取实值
    int num = maps["july"];
    cout << num << endl; // 3

    //查找某key
    iter = maps.find("jane");
    if (iter != maps.end()) cout << iter->second << endl; // 2

    //修改实值
    iter->second = 100;
    int num2 = maps["jane"]; // 100
    cout << num2 << endl;

    // 几种插入数据的方式
    std::map<int, std::string> mapStudent;
	// 1) 用insert函数插入pair数据
	mapStudent.insert(pair<int, string>(1, "student_one"));
	// 2) 用insert函数插入value_type数据
	mapStudent.insert(map<int, string>::value_type(1, "student_one"));
	// 3) 在insert函数中使用make_pair()函数
	mapStudent.insert(make_pair(1, "student_one"));
	// 4) 用数组方式插入数据
	mapStudent[1] = "student_one";
    
    //	删除元素
    map<int, int> map1;
    auto i = map.find(1);
    map.eraset(i)
}

//	自定义类型放入map中
class A {
public:
    A() = default;
    A(const A&) = default;
    ~A() = default;
    int i;
    bool operator<(const A& a1) const{
        return a1.i < this -> i;
    }
};

int main() {
    map<A, int> map2; 
    A a1, a2;
    map2[a1] = 1;
}
```

<br/>

## at、[]和find的区别

[]

- 将关键码作为下标去执行查找，并返回对应的值
- 如果不存在这个关键码，就将一个具有该关键码和值类型的默认值的项插入这个map
- 所以不能通过[]判断元素是否在容器中



find函数

- 用关键码执行查找，找到了返回该位置的迭代器
- 如果不存在这个关键码，就返回尾迭代器
- 速度快，map的find是二分查找的版本



at
- 将关键码作为下标去执行查找，并返回对应的值
- 如果不存在就会报错

<br/>

<br/>

<br/>

# unordered_map

## 实现

unordered_map中的bucket所维护的list是其自己定义的由hashtable_node数据结构组成的linked-list

bucket聚合体本身使用vector进行存储（**所以说本质是数组**）

hashtable的迭代器只提供前进操作，不提供后退操作

在hashtable设计bucket的数量上，其内置了28个质数[53, 97, 193,...,429496729]，在创建hashtable时，会根据存入的元素个数选择大于等于元素个数的质数作为hashtable的容量（vector的长度），其中每个bucket 所维护的linked-list长度也等于hashtable的容量。如果插入hashtable的元素个数超过了bucket的容量，就要进行重建table操作，即找出下一个质数，创建新的buckets vector，重新计算元素在新hashtable的位置

什么时候扩容：当向容器添加元素的时候，会判断当前容器的元素个数，如果大于等于阈值---即当 前数组的长度乘以加载因子的值的时候，就要自动扩容啦

![](拉链法实现hashtable.png)

unordered_map是基于**hash_table**实现，一般是由一个大vector，vector元素节点可挂接链表来解决冲突来实现。hash_table最大的优点，就是把数据的存储和查找消耗的时间大大降低，几乎可以看成是常数时间；而代价仅仅是消耗比较多的内存。然而在当前可利用内存越来越多的情况下，用空间换时间的做法是值得的

hash_table节点的定义

- ```cpp
  template<class Vaule>
  struct __hashtable_node {
      __hashtable_node* next;
      Value val;
  };
  ```

<br/>

## 迭代器

![](hashtable的迭代器.png)

hashtable的迭代器没有后退操作，hashtable也没有定义所谓的逆向迭代器

<br/>

## 源码

![](hashtable的数据结构.png)

![](hashtable的节点数.png)

<br/>

## 基本用法

```cpp
//	自定义类型放入unordered_map中
#include <iostream>
#include <string>
#include <unordered_map>
using namespace std;
struct my_key {
    int    num;
    string name;
    my_key(){}
    ~my_key(){}
    my_key(int a, string b) : num(a), name(b){}
    bool operator==(const my_key &t)const {
        return this->num == t.num;
    }
};
struct myHashFuc {
	std::size_t operator()(const my_key &key) const {
		return std::hash<int>()(key.num);
	}
};
 
int main() {
    unordered_map <my_key, bool, myHashFuc> mmp;
    my_key myuin(1, "bob");
    mmp[myuin] = true;
 
    cout << mmp[myuin] << endl;
    return 0;
}
```

由于unordered_map是采用哈希实现的，对于系统的类型int, string等，都已经定义好了hash函数，所以如果我们引入新的自定义类型的话，系统并不知道如何去计算我们引入的自定义类型的hash值，所以我们就需要自己定义hash函数，告诉系统用这种方式去计算我们引入的自定义类型的hash值

除了自定义哈希函数外，系统计算了hash值后，还需要判断是否冲突，对于默认的类型，系统都知道怎样去判断是否相等，但不知道怎样去判断我们引入的自定义类型是否相等，所以需要我们重载==号，告诉系统用这种方式去判断2个键是否相等

<br/>

## 为什么bucket的数量都是质数

因为我们在hashtable的定义中，hash函数使用的是标准的求模函数，因此这样定义桶数有利于元素各个桶之间的均匀分布

如果说是合数，那么只要是和桶的数量有相同公约数的，比如说桶数为4，数字8，12，16都一定会被放到同一个桶0里面，就会造成hash冲突

那么这时候hashtable的性能将取决于到底有多少元素能够和桶数有公约数，这对hashtable尽量使各个桶之间的元素数近似相等的原则违背

因此如果对于合数，放入的元素有一定的规律性，就会很容易造成极端情况的出现

另外，hashtable相比于RB-tree的一个优势就在于RB-tree虽然平均查找时间是对数时间，但是这是在假设数据均匀分布的基础之上的，而hashtable也有平均对数时间上的性能，且这种表现是以统计为基础，不需依赖元素输入的随机性。

<br/>

<br/>

<br/>

# multimap

<img src="multimap.png" style="zoom:150%;" />

<br/>

<br/>

<br/>

# map和unordered_map的对比

## map

- 底层实现是红黑树，所以可以支持键值的自动排序，所以在查询和维护的时间和空间复杂度上都为$O(logn)$
  - 内部元素有序

- 但是空间占用比较大，因为每个节点要保持父节点、孩子节点及颜色的信息
- 相比哈希表，没有了rehash的过程

<br/>

## unordered_map

- 底层机制是哈希表，通过hash函数计算元素位置，查询时间复杂度为O(1)
  - 内部元素无序
- 维护时间与bucket桶所维护的list长度有关
- 但是建立hash表耗时较大，同时rehash耗时较大

<br/>

## 总结

- map适用于有序数据的应用场景，unordered_map适用于高效查询的应用场景
- map 底层数据结构为红黑树，有序，不重复
- multimap 底层数据结构为红黑树，有序，可重复
- unordered_map 底层数据结构为hash表，无序，不重复
- unordered_multimap 底层数据结构为hash表，无序，可重复

<br/>

<br/>

<br/>

# to do list

https://mp.weixin.qq.com/s?__biz=MzkyMjIxMzIxNA==&mid=2247483656&idx=1&sn=a204fedfbf2cf7f2023979c56b756c8a&scene=19#wechat_redirect

https://mp.weixin.qq.com/s?__biz=MzkyMjIxMzIxNA==&mid=2247483848&idx=1&sn=d459a04730a4e56653452eae9f71d424&scene=19#wechat_redirect
