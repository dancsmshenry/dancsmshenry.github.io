---
title: STL 源码剖析之 vector
top: false
cover: false
toc: true
mathjax: true
math: true
date: 2022-10-20 08:46:01
password:
summary:
tags:
- STL
categories:
---





# 实现

![](vector示意图.png)

vector 中有**三个指针**：指向使用空间的头（`start`）和尾（`finish`），以及可用空间的尾（`end_of_storage`）

可用空间：为了降低空间配置的速度成本，vector 实际配置的大小可能比客户需求的大一些（即`capacity >= size`）

默认的空间分配器是`alloc`

<br/>

## 源码

![](vector的定义.png)

vector 的数据（三个迭代器）是存储在栈上的，迭代器指向的数组是存放在堆上的

<br/>

为什么不能把数据放到栈上

- 栈的空间宝贵且有限，不能无限存放元素
- 栈中数据的生命周期和函数挂钩

<br/>

为什么 end 要在最后一个元素再后面的一个位置

- 当没有元素的时候，begin 和 end 指向一起，方便判空

<br/>

## 迭代器

vector 的**迭代器本质上就是一个指针，指向元素T**
- 迭代器也可以用 [] 运算符进行访问：b[i] 等价于`*(b + i)`

<br/>

<br/>

<br/>

# 基本用法

## 构造

```cpp
std::vector<int> vec0(2);

std::vector<int> vec1(3, 333);

std::vector<int> vec2{111, 222, 333};

//	拷贝构造（深拷贝）
std::vector<int> vec3(vec2.begin(), vec2.end());
std::vector<int> vec4(vec3);
std::vector<int> vec5 = vec3;

//	移动构造
std::vector<int> vec6(10, 100);
std::vector<int> vec7 = std::move(vec6);
std::cout << "vec6.size() = " << vec6.size() << std::endl;	//	0
```

<br/>

## 迭代器

```cpp
std::vector<int> vec;

//	begin 返回容器第一个元素的迭代器，end 返回指向容器尾端的迭代器
//	当容器没有元素时，begin 和 end 相等
for (auto iter = vec.begin(); iter != vec.end(); ++ iter) {}
for (const auto iter = vec.begin(); iter != vec.end(); ++ iter) {}

//	rbegin 返回一个容器最后一个元素的反向迭代器，rend 返回一个容器前端的反向迭代器
//	当反向迭代器 +1 时，会往前面移动
for (auto iter = vec.rbegin(); iter != vec.rend(); ++ iter) {}

//	cbegin 返回容器第一个元素的迭代器，cend 返回指向容器尾端的迭代器
//	与 begin 和 end 不同的是，cbegin 为 const 类型，
//	而 begin 会根据返回值特化为 const 和非 const 类型
for (auto iter = vec.cbegin(); iter != vec.cend(); ++ iter) {}
```

<br/>

## 常用函数

```cpp
std::vector<int> vec(10, 20);

//	返回容器第一个元素
std::cout << vec.front() << std::endl;

//	返回容器最后一个元素
std::cout << vec.back() << std::endl;

//	容器为空则返回 true，否则返回 false
std::cout << vec.empty() << std::endl;

//	返回容器元素的个数
std::cout << vec.size() << std::endl;

//	返回容器的容量
std::cout << vec.capacity() << std::endl;

//	返回容器可容纳的元素最大数量，可以理解是无穷大，具体与平台实现有关
std::cout << vec.max_size() << std::endl;

//	返回容器首元素的数据指针
int *p = vec.data();
```

<br/>

## shrink_to_fit

将 capacity 减小为指定大小（**使得已有迭代器失效**）

```cpp
std::vector<int> vec(10, 0);
vec.push_back(1);

//	20
std::cout << vec.capacity() << std::endl;
auto iter = vec.begin();

vec.shrink_to_fit();

//	11
std::cout << vec.capacity() << std::endl;

//	UB, 概率会 coredump
std::cout << *iter << std::endl;
```

<br/>

## pop_back

删除容器最后一个元素（size 变小，capacity 不变）

```cpp
std::vector<int> vec(10, 0);
vec.pop_back();

//	10
std::cout << f.capacity() << std::endl;

//	9
std::cout << f.size() << std::endl;
```

<br/>

## assign

替换容器的元素

```cpp
std::vector<int> vec(10, 100);
vec.assign(5, 1000);

//	可以用迭代器或者 initializer_list
//	vec.assign(vec1.begin(), vec1.end()); 
//	vec.assign({'1', '2', '3'});

//  1000 1000 1000 1000 1000
for (const auto& iter : vec) {
  std::cout << iter << " ";
}
std::cout << std::endl;
```

<br/>

## insert

在指定位置添加元素

```cpp
std::vector<int> vec(10, 1000);

// 在 begin 的位置添加一个 10 的元素
vec.insert(vec.begin(), 10);
// 在 begin 的位置添加 10 个值为 10 的元素
vec.insert(vec.begin(), 10, 10);

// 将另一个容器的元素插入到指定位置
std::vector<int> vec1(10, 1111);
vec.insert(vec.begin() + 2, vec1.begin(), vec1.end()); 
```

<br/>

## emplace

将元素插入到指定位置（简化版 insert）

```cpp
std::vector<int> vec(10, 1000);

// 1000 1000 1000 1000 1000 1000 1000 1000 1000 1000
for (const auto &iter : vec) {
  std::cout << iter << " ";
}
std::cout << std::endl;

vec.emplace(vec.begin() + 6, 66);

// 1000 1000 1000 1000 1000 1000 66 1000 1000 1000 1000
for (const auto &iter : vec) {
  std::cout << iter << " ";
}
std::cout << std::endl;
```

<br/>

## swap

交换两个容器的内容（需要注意入参为 `vector& other`）

```cpp
std::vector<int> vec(10, 0);

std::vector<int>{}.swap(vec);
//	vec.swap(std::vector<int>{});	//	error， do not support right value

//  0
std::cout << "vec size is " << vec.size() << std::endl;
//  0
std::cout << "vec capacity is " << vec.capacity() << std::endl;
```

函数 `clear` 只会析构容器的元素，但是不会释放容器使用的空间，因此可以用函数 `swap` 和临时的空对象交换，实现内存空间的释放

<br/>

## erase

删除指定迭代器的内容（size 会变，capacity 不变）

```cpp
std::vector<int> vec(10, 20);

//	删除指定位置的元素
vec.erase(vec.begin());

//	删除从 first 开始到 last 位置的元素
vec.erase(vec.begin() + 2, vec.begin() + 5);
```

<br/>

实际上，当指定位置的元素被删除了之后，会被后面的元素依次的往前挪一个位置，因此返回的迭代器还是需要被删除的迭代器，但是指向的值不一样了

```cpp
//	删除 vector<int> 中所有等于 2 的值
std::vector<int> vec{0, 1, 2, 2, 2, 2, 2, 3, 4};
for (auto iter = vec.begin(); iter != vec.end();) {
  if (2 == *iter) {
    vec.erase(iter);
  } else {
    ++iter;
  }
}

//  0 1 3 4
for (const auto &iter : vec) {
  std::cout << iter << " ";
}
std::cout << std::endl;

//	一种更为简单的实现
//	先将为 2 的 value 都挪到容器尾部，然后 erase
auto checkIs2 = [](const auto& x) { return x == 2; }; 
vec.erase(std::remove_if(vec.begin(), vec.end(), checkIs2), vec.end()); 
```

<br/>


## clear

清空容器中所有的元素。只改变 size，不改变 capacity

```cpp
std::vector<int> vec(10, 20);

vec.clear();

//	0
std::cout << vec.size() << std::endl;

//	10
std::cout << vec.capacity() << std::endl;
```

<br/>

根据数据类型的不同，时间复杂度也会不同

- 如果容器中是 POD 或基本数据类型，那由于该元素没有析构函数，加之 vector 内部连续存储的特性，编译器的实现是可以在 `O(1)` 完成的
- 而如果是自定义数据，又或者 list 或 vector 等类型，就要逐个去析构，时间复杂度就会到 `O(n)`

<br/>

## resize 和 reserve

`resize`：将容器的 size 修改为指定大小（capacity 只会变大或不变，**不会变小**）

`reserve`：将容器的 capacity 修改为指定大小（size **不变**）

```cpp
{
  std::vector<int> vec(10, 0);
  //	10
  std::cout << "before vec capacity = " << vec.capacity() << std::endl;
  //	20 > capacity，因此 size 和 capacity 一起变为 20
  vec.resize(20);
  
  //	20
  std::cout << "after vec capacity = " << vec.capacity() << std::endl;
  //	20
  std::cout << "after vec size = " << vec.size() << std::endl;
}

{
  std::vector<int> vec(40, 0);
  //	40
  std::cout << "before vec capacity = " << vec.capacity() << std::endl;
  //	20 < capacity, 因此 size 变为 20，capacity 不变
  vec.resize(20);
  
  //	40
  std::cout << "after vec capacity = " << vec.capacity() << std::endl;
  //	20
  std::cout << "after vec size = " << vec.size() << std::endl;
}

{
  std::vector<int> vec(10, 20);
  
  vec.reserve(10000);
  
  std::cout << vec.at(9) << std::endl;	//	yes
  
  std::cout << vec.at(999) << std::endl;	//	error
}
```

<br/>

## push_back 和 emplace_back

将元素放到容器尾端

```cpp
#include <iostream>
#include <vector>

class StructA {
public:
  StructA() { std::cout << "StructA" << std::endl; }
  StructA(const StructA &other) { std::cout << "StructA copy" << std::endl; }
  StructA(const StructA &&other) { std::cout << "StructA move" << std::endl; }
  StructA(int age) { std::cout << "StructA age" << std::endl; }
};

int main() {
  {
    std::cout << "------- Begin push_back for left value -------" << std::endl;
    std::vector<StructA> vec;
    StructA tt;
    vec.push_back(tt); //  有参构造 + 拷贝构造
  }

  {
    std::cout << "------- Begin emplace_back for left value -------"
              << std::endl;
    std::vector<StructA> vec;
    StructA tt;
    vec.emplace_back(tt); //  有参构造 + 拷贝构造
  }

  {
    std::cout << "------- Begin push_back for temp value -------" << std::endl;
    std::vector<StructA> vec;
    vec.push_back(StructA(12)); //  有参构造 + 移动构造(没有移动，就会调用拷贝)
  }

  {
    std::cout << "------- Begin emplace_back for temp value -------"
              << std::endl;
    std::vector<StructA> vec;
    vec.emplace_back(StructA(12)); //  有参构造 + 移动构造(没有移动，就会调用拷贝)
  }

  {
    std::cout << "------- Begin push_back for value -------" << std::endl;
    std::vector<StructA> vec;
    vec.push_back(12); //  有参构造 + 移动构造(没有移动，就会调用拷贝)
  }

  {
    std::cout << "------- Begin emplace_back for value -------" << std::endl;
    std::vector<StructA> vec;
    vec.emplace_back(12); //  有参构造
  }
  
  {
    std::vector<std::vector<int>> vec;

    vec.emplace_back(std::vector<int>{1, 2});
    vec.push_back(std::vector<int>{1, 2});

    vec.emplace_back(std::initializer_list<int>{1, 2});
    vec.push_back(std::initializer_list<int>{1, 2});

    auto temp = {1, 2};
    vec.emplace_back(temp);
    vec.push_back(temp);

    vec.push_back({1, 2, 3, 4, 5, 6, 7});
    //	vec.emplace_back({1, 2, 3, 4, 5, 6, 7}); //  error
    
    // vec.push_back(1, 2);  //  error
    vec.emplace_back(1);
    vec.emplace_back(1, 2);
  }
}
```

<br/>

**总结**

对于左值，都是调用拷贝构造

对于右值，如果是已经构造好了的，都是调用移动或者拷贝构造（优先调用移动构造）

- 如果是没构造好的（需要隐式转换），`push_back` 是先构造，然后再移动或者拷贝构造（优先调用移动构造）；`emplace_back` 是直接构造

<br/>

`push_back` 的入参是 `value_type`，即已经指明了需要接受的参数类型（并且只能有一个入参），因此即使传入的并非 `value_type` 的类型，也会做隐式转换

`emplace_back` 的入参是 `class... _Args`，没有指明接受的参数类型和个数，同时不会为入参做隐式转换（需要使用者指明入参的类型）

- 因此，`emplace_back` 希望接受 `std::initializer_list` 或者能够构造出 `std::vector` 的入参（因为这二者可以构成 `value_type`），而入参 `{1, 2, 3, 4, 5, 6, 7}` 希望函数的入参能隐式的把它转换为上述两种类型。结果就有点类似死锁了，编译报错
- 特别的，当传入 `(1, 2)` 或者 `(1)`的时候，可以隐式的转换构造出 `std::vector`

<br/>

## at 和 []

访问容器下标的元素

```cpp
std::vector<int> vec{1, 2, 3};

vec.reserve(11111);

//	11111
std::cout << vec.capacity() << std::endl;

//	3
std::cout << vec.size() << std::endl;

//	error
std::cout << vec.at(3) << std::endl;

//	yes
std::cout << vec[3] << std::endl;
```

<br/>

[] 的越界访问是不会报错（每次访问都需要判断越界，对性能损耗大）

at 的越界访问是会报错的（会检查越界，以 size 为准，而不是 capacity）

<br/>

<br/>

<br/>

# 扩容

## 为什么不是等差扩容

如果是等差扩容

假定每次扩容 `m` 个元素，总的元素个数是 `n`，则需要扩容 `n/m` 次

```latex
\sum^{n/m}_{i = 1}m*i=\frac{ (n+m) * n } { 2 * m}\\
```

扩容的时间复杂度平均到每个元素上就是 `O(n)`

<br/>

如果是成倍扩容

假定有 `n` 个元素,倍增因子为 `m`

那么完成这 `n` 个元素进行 `push_back` 操作，需要重新分配内存的次数大约为 `logm(n)`

第 `i` 次重新分配将会导致复制 `m^i`（也就是当前的 `vector` 大小）个旧空间中元素

因此 `n` 次 `push_back` 操作所花费的总时间约为  `n*m/(m - 1)`

扩容的时间复杂度平均到每个元素上就是`O(1)`（发现 m 为 2 时，时间复杂度最小，所以一般是 2 倍扩容）

<br/>

<br/>

## 为什么是 2 倍或者 1.5 倍扩容

理想的分配方案：是在第 n 次扩容时能复用之前 n-1 次释放的空间

- 而当 m=2 的时候每次扩容的大小都会大于前面释放掉的所有的空间
- 按照小于 2 倍方式扩容，多次扩容之后就可以复用之前释放的空间了
- 而超过 2 倍，就会导致空间的浪费，并且无法完美的使用到前面已经释放掉的内存

<br/>

总结

- 使用 2 倍扩容时，每次扩容后的新内存大小必定大于前面的总和
- 使用 1.5 倍扩容时，在数次扩容后，就可以重用之前的内存空间
