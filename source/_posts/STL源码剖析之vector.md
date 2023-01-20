---
title: STL源码剖析之vector
top: false
cover: false
toc: true
mathjax: true
date: 2022-10-20 08:46:01
password:
summary:
tags:
- STL
- vector
categories:
---

# vector实现

![](vector示意图.png)

vector中有**三个指针**：指向使用空间的头（`start`）和尾（`finish`），以及可用空间的尾（`end_of_storage`）

可用空间：为了降低空间配置的速度成本，vector实际配置的大小可能比客户端需求量大一些（即`capacity >= size`）

默认的空间分配器是`alloc`

<br/>

## 源码

vector的数据（三个迭代器）是存储在栈上的，迭代器指向的数组是存放在堆上的

![](vector的定义.png)

为什么不能把数据放到栈上

- 栈上是不能动态扩容的，要实现动态扩容只能是堆
- 同时栈的空间宝贵且有限，不能无限存放元素

为什么end要在最后一个元素再后面的一个位置

- 当没有元素的时候，begin和end指向一起，方便判空

<br/>

## 迭代器

vector的**迭代器本质上就是一个指针，指向元素T**
- 迭代器也可以用[]运算符进行访问：b[i]等价于`*(b + i)`

<br/>

<br/>

<br/>

# vector扩容

## 为什么是成倍扩容

如果是等差扩容

假定每次扩容`m`个元素，总的元素个数是`n`，则需要扩容`n/m`次
$$
\sum^{n/m}_{i = 1}m*i=\frac{ (n+m) * n } { 2 * m}\\
$$

扩容的时间复杂度平均到每个元素上就是`O(n)`

<br/>

而如果是成倍扩容

假定有 `n` 个元素,倍增因子为 `m`

那么完成这 `n` 个元素进行`push_back`操作，需要重新分配内存的次数大约为`logm(n)`

第`i`次重新分配将会导致复制`m^i`（也就是当前的`vector`大小）个旧空间中元素

因此`n`次 `push_back`操作所花费的总时间约为 `n*m/(m - 1)`
$$
\sum^{log_{m}{n}}_{i = 1}m^i=\frac{n*m}{m-1}\\
$$

扩容的时间复杂度平均到每个元素上就是`O(1)`（发现m为2时，时间复杂度最小，所以一般是2倍扩容）

<br/>

<br/>

## 为什么是2倍（gcc）或者1.5倍（msvc）扩容

理想的分配方案：是在第n次扩容时能复用之前n-1次释放的空间
- 而当m=2的时候每次扩容的大小都会大于前面释放掉的所有的空间
- 按照小于2倍方式扩容，多次扩容之后就可以复用之前释放的空间了
- 而超过2倍，就会导致空间的浪费，并且无法完美的使用到前面已经释放掉的内存



总结

- 使用2倍扩容时，每次扩容后的新内存大小必定大于前面的总和
- 使用1.5倍扩容时，在数次扩容后，就可以重用之前的内存空间

<br/>

<br/>

<br/>

# 基本用法

## vector的构造

```cpp
//	vector的四种构造方式
vector<string> i1(2, "hi");
vector<string> i2{"why", "always", "me"};
vector<string> i3(i2.begin(), i3.end());
vector<stirng> i4(i3);

vector<int> f1(4); // 保证得到的元素都是0
vector<int> f2(4, 0); // 二者等价

vector<int> i5{1};
vector<int> i6 = i5;	// operator= 赋值运算符
```



## vector的迭代器

```cpp
// begin返回指向容器的第一个元素的迭代器，end返回指向容器尾端的迭代器
for (vector<int>::reverse_iterator it = v.begin(); it != v.end(); ++ it) {}

// rbegin返回一个指向容器最后一个元素的反向迭代器，rend返回一个指向容器前端的反向迭代器（反向迭代器+1会往前面移动）
for (vector<int>::reverse_iterator it = v.rbegin(); it != v.rend(); ++ it) {}
```



## vector的常用函数

```cpp
//	容器第一个元素
std::cout << i6.front() << std::endl;

//	容器最后一个元素
std::cout << i6.back() << std::endl;

//	容器为空则返回true，否则为false
std::cout << i6.empty() << std::endl;

//	容器中的元素个数
std::cout << i6.size() << std::endl;

//	容器可容纳的元素最大数量
std::cout << i6.max_size() << std::endl;

//	容器的容量
std::cout << i6.capacity() << std::endl;
```

<br/>

<br/>

<br/>

# API的使用

## resize

作用：将容器的size修改为size1
- 如果size1比当前的size大，那么size就会变为size1（如果capacity比size1小，capacity也会变为size1；否则capacity不变）
  - 扩容多出的部分值为0
- 如果size1比当前的size小，那么size就会变为size1（capacity不变）

总结：capacity只会变大或不变，不会变小

<br/><br/>

## data

作用：返回数据数组的指针

```cpp
vector<int> f(10, 20);
int *p = f.data();
```

<br/><br/>

## push_back

作用：将对象放到vector中

时间复杂度分析（参考扩容，时间复杂度为`O(n)`）

<br/>

实现原理

首先检查是否有备用空间，如果有就直接在备用空间上构造元素，并调整迭代器finish

![push_back](push_back.png)

PS：**为什么还要独立开一个insert_aux函数**：因为可能其他的函数（insert）也会用到插入元素的功能，所以进行抽象封装

<br/>

如果没有可用空间，就扩大原有的vector（重新配置、移动数据、释放原空间）

![insert_aux](insert_aux.png)

PS：**一旦空间重新分配，指向原vector的所有的迭代器都会失效**

所以最好以数组下标作为记录，而不是迭代器作为记录

<br/><br/>

## emplace_back

作用：将对象放到vector中，在容器末尾就地构造元素（在末尾添加元素）

```cpp
#include <iostream>
#include <vector>

class Test {
public:
    Test() {std::cout << "Test" << std::endl;}
    ~Test() {std::cout << "~Test" << std::endl;}
    Test(const Test &p) {std::cout << "Test copy" << std::endl;}
    Test(const Test &&p) {std::cout << "Test move" << std::endl;}
    Test(int age) {std::cout << "Test age" << std::endl;}
};

int main() {
    std::vector<Test> v;
    Test tt;
    std::cout << "----------" << std::endl;

/////////////////////////////////////////////////传入左值

    // v.push_back(tt);	//	调用的是拷贝构造函数
    std::cout << "----------" << std::endl;

    // v.emplace_back(tt);	//	调用的是拷贝构造函数
    std::cout << "----------" << std::endl;
    
/////////////////////////////////////////////////传入右值

    // v.emplace_back(Test(12));
    std::cout << "----------" << std::endl;
    /*
    Test age
	Test move（没有move构造函数，就会调用copy构造函数）
	~Test
	~Test // 程序结束的析构
	传右值：这里调用了一次构造函数（先在外面构造一个临时对象，执行完这句话后析构），一次移动构造函数（在emplace_back里面），所以有两次析构，构造了两个对象
    */
    
    // v.push_back(Test(12));
    std::cout << "----------" << std::endl;
    /*
    Test age
	Test move（没有move构造函数，就会调用copy构造函数）
	~Test
	~Test // 程序结束的析构
	传右值：这里调用了一次构造函数（先在外面构造一个临时对象，执行完这句话后析构），一次移动构造函数（在push_back里面），所以有两次析构，构造了两个对象
    */
    
    // v.emplace_back(12);
    std::cout << "----------" << std::endl;
    /*
    Test age
	~Test//程序结束的析构
	传右值：这里调用了一次含参的构造函数
    */
    
    // v.push_back(12);
    /*
    Test age
	Test move（没有move构造函数，就会调用copy构造函数）
	~Test
	~Test//程序结束的析构
	传右值：这里调用了一次构造函数（先在外面构造一个临时对象，执行完这句话后析构），一次移动构造函数（在push_back里面），所以有两次析构，所以有两次析构，构造了两个对象
    */
    
    // 结论：
    // 传左值：两者都是一样的：调用一次构造函数，再调用一次拷贝构造函数
    // 传右值：如果是已经构造好的右值，比如说Test(12)，那么二者是相同的；但是如果没构造好，比如12，需要调用有参构造函数，那么emplace_pack效率更高一些
    
    //	从另一个角度来看，说明push_back真的会构建一个临时对象（
    vector<pair<int, int>> ret;
    // ret.push_back(1,1)//会报错，因为没有构造一个临时对象
    ret.push_back(pair<int, int>(1, 1)); //不会报错，因为构成了一个pair对象
    ret.emplace_back(1, 1);    //不会报错，因为直接在容器的尾部创建对象
}
```

<br/>

总结

push_back

- 对于右值，如果是已经构造好了的，就直接调用move或copy函数（优先调用move）；如果还没构造好（例如传入12，需要调用有参构造函数，隐性的转换为该类对象），那就先构造出对象，然后再调用move或copy函数（优先调用move）
- 对于左值，拷贝构造

emplace_back

- 对于右值， 如果是已经构造好了的，就直接调用move或copy函数（优先调用move）；如果还没构造好，**就直接原地调用有参构造函数**
- 对于左值，拷贝构造

<br/>

emplace_back使用上的一个**坑**

```cpp
#include <iostream>
#include <vector>

int main() {
	std::vector<std::vector<int>> a;
    
	a.push_back({1, 2});
	a.emplace_back(std::vector<int>{1, 2});
	a.emplace_back(std::initializer_list<int>{1, 2});

	auto x = {1, 2};
	a.emplace_back(x);
	a.emplace_back({1,2,3,4,5,6,7}); //	这里会报错
}
```

解释：

- 因为对于push_back来说，查看源代码发现它接收的是一个具体的value_type，即是固定的类型
- 再看看有关vector的构造，它没有写explicit，所以{1,2}可以隐式转换为vector<int>
- 而对于emplace_back，它的源代码是一个模板函数，造成的结果就是所提供的参数{1,2}会做模板参数类型匹配，不会主动强转std::initializer_list<int>，需要你显式构造，或者用auto先推导一遍
- 但是这里模板推到不出来类型，所以就会报错
- ![](push和emplace_back_01.png)
- ![](push和emplace_back_02.png)
- 这里的value_type是typeof，即为T，可以理解为已经固定了的类型

- 参考：https://www.zhihu.com/question/438004429

<br/>

<br/>

## shrink_to_fit

作用：把capacity减小到size；可能使得现有的迭代器失效

```cpp
int main() {
    std::vector<int> f(10, 0);
    f.push_back(1);
    std::cout << f.capacity() << std::endl;	//	20
    f.shrink_to_fit();
    std::cout << f.capacity() << std::endl;	//	11
}
```

<br/><br/>

## erase

作用：删除内容，不改变容量大小（即size会发生变化，capacity不变）

<br/>

语法：

```cpp
//	删除指定位置的元素，返回值是一个迭代器，指向删除元素的下一个元素
iterator erase(iterator _Where);
//	删除从 _First开始到 _Lsat位置的元素，返回值也是一个迭代器，指向最后一个删除元素的下一个位置
iterator erase(iterator _First, iterator _Last);

// erase的应用
i6.erase(i6.begin());                     //删除单个元素
i6.erase(i6.begin() + 2, i6.begin() + 5); //删除指定区间的元素
```

<br/>

返回值：被删除元素后一个元素的迭代器（被删除元素的迭代器其实不会失效，而是指向被删除元素的下一个位置元素）

```cpp
// 删除一个vector中所有等于2的数字的正确做法
vector<int> count{0,1,2,2,2,2,2,3,4};
for(auto iter=count.begin(); iter!=count.end(); ) {
    if(2 == *iter) {
        iter = count.erase(iter);
    } else {
        ++ iter;
    }
}
```

erase实质是将迭代器后面的元素全部复制一遍，接着往前移动一个位置

因此当前位置的迭代器会指向原iter的后一位数字（所以其实是将后一部分的元素覆盖了前面部分的元素，比如说长为9的数组，删除掉前面5个数字，但当前下标为7和8位置的数据是不变的）

看了一下源码实现，如果是删除最后一个元素的话，就只会移动最后一个迭代器（end）

<br/>

<br/>


## clear

作用：清空容器中所有的元素（只改变size，不改变capacity）；所以clear是不会释放容器的内存

<br/>

时间复杂度分析

根据数据类型的不同，时间复杂度也会不同

- 如果容器中是POD或基本数据，那由于该元素没有析构函数，加之vector内部连续存储的特性，编译器的实现是可以在`O(1)`完成`clear()`的
- 而如果是自定义数据，或者list或vector等类型，就要逐个去析构，时间复杂度就会到`O(n)`

<br/>

因此，clear在某些时候时间复杂度是很高的

- 在工程实践中，我们要思考是否每次都需要及时的clear掉一个容器
- 比如在后台服务中，有些容器类型的变量在符合某些条件下要进行clear()，后续逻辑中判断容器是空的，就不在用之进行某些逻辑（比如遍历它，进行某种操作）
- 其实也可以用一个bool标记来存储后续是否需要遍历该容器，待到本次请求的响应返回给client之后，再来清理这个容器也不迟

<br/>

<br/>

## pop_back

作用：删除最后一个元素（size发生变化，capacity不变）

<br/>

<br/>

## at和[]

作用：二者是等价的，即也可以用at对对应下标的数值赋值

```cpp
// at(索引)
vector<int> i6{1, 2, 3};
i6.at(1); //等价于i6[1]

//	at的源码
	reference
    at(size_type __n)
    {
		_M_range_check(__n);
		return (*this)[__n];
    }

// operator[]，返回第几个值
i6[1] = 10;
```

[]的越界访问是不会报错

- 每次访问都需要判断越界，是非常损耗性能的
- 因此越界访问到什么数据都是未知的

<br/>

而at的越界访问是会报错的

- at会检查是否越界
- 同时，at的参数时size_t，放入负数的话会被转为整数

<br/>

<br/>

## 其他

```cpp
// assign
vector<char> i5;
i5.assign(5, 'x');               // 第一个参数是数字，第二个参数是变量，即数量*变量
i5.assign(i4.begin(), i4.end()); // 也可以用迭代器
i5.assign({'1', '2', '3'});      // 还可以用initializer_list

// resize重设容器大小以容纳count个元素
i6.resize(10);

// insert的三种形式
i6.insert(i6.begin(), 10);                       //在begin的位置添加一个10的元素
i6.insert(i6.begin(), 10, 10);                   //在begin的位置添加10个值为10的元素
i6.insert(i6.begin() + 2, i5.begin(), i5.end()); //把另一个容器的元素插入到指定位置

// swap交换两个容器的内容
i6.swap(i5);

// emplace在指定位置添加元素
i6.emplace(i6.begin() + 1, 11);
```

<br/>

<br/>

<br/>

# trick

## 删除首个元素

```cpp
vector<int> v1(10, 100);
v1.erase(v1.begin());
```

<br/>

<br/>

## 释放空间

背景：一般情况下vector的内存占用空间只增不减

比如一开始分配了10000个字节，然后erase掉后面9999个，留下一个有效元素

但是内存占用仍为10,000个（并且所有内存空间是在vector析构时候才能被系统回收）

clear()可以清空所有元素，但vector所占用的内存空间不变，无法保证内存的回收

所以如果想要清空vector所占用的内存，就用swap

```cpp
#include <vector>
#include <iostream>

using namespace std;

int main() {
    vector<int> f1(100, 100);
    {
        vector<int> f;
        f1.swap(f);
    }
    //	vector<int>().swap(f1); // 或者这样
    
    
    // 这样不行，因为swap的参数是T&，不能传递匿名对象
    //	f1.swap(vector<int>());
    cout << f1.size() << endl;
}
```
