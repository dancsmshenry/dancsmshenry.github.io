---
title: '深入理解CPP之auto,decltype,move,forward'
top: false
cover: false
toc: true
mathjax: true
date: 2022-10-22 13:50:52
password:
summary:
tags:
- CPP
categories:
---



# left value

## 定义

其实`left value`并没有很好的定义去说明，一种被普遍认同的观点便是**在内存的表达式，能够用内置&进行取地址**的值

```cpp
//	错误的观点1：等号右边的是右值，左边的是左值
int a = 3;	//	a是左值，3是右值
int b;	//	b是左值
b = a; 	//	a在等号右边，但a是左值,可以取地址

//	错误的观点2：不能取地址的（放寄存器中值）是右值
// 字符串字面量没有名字，是左值，
// 我们可以这样直接原始取地址
&("Hello World");
```

<br/>

## 左值引用

能够指向左值，不能指向右值的就是左值引用

- 例外：const左值引用可以指向右值（涉及到const的底层实现，它新建了一个值给其引用）

- const左值引用不会修改指向值，因为可以指向右值

- ```cpp
  std::vector<int> arrs;
  arrs.push_back(1);	//	因为push_back传入的参数是就是const value_type& val
  
  //	push_back的原型(加上const后既可以接受左值，也可以接受右值，方便使用)
  void push_back(const value_type& val);
  //	void push_back(value_type& val); // 这种做法的缺点，只能接收左值，不能接收右值
  ```

可以理解为`c++`的**语法糖**，更加方便的使用指针

<br/>

## 左值（举例）

函数名和变量名

返回左值引用的函数调用

内置的前++与前--，如：`++a`

**变量类型是右值引用的表达式**，如：`TestClassA&& ra = TestClassA(1000);`，ra这里是左值内置*解引用的表达式，如：`*pkValue`

**字符串字面值"abcd"**

<br/>

<br/>

<br/>

# right value

## 定义

不能取地址的没有名字的，临时的，位于等号右边的

更多的是一种值的表达

<br/>

## 右值引用

右值引用可以指向右值，不可以指向左值（如需指向左值，要用move）

- 本质上是将一个右值提升为左值（延长右值的生命周期）

右值引用既可以是**左值**（`int a = std::move(1);`，其中的`a`是左值），也可以是**右值**（`std::move(1)`，没有名字，便是右值）

作为函数形参时，右值引用更灵活。虽然const左值引用也可以做到左右值都接受，但它无法修改，有一定局限性

```cpp
// 形参是个右值引用
void change(int&& right_value) {
    right_value = 8;
}
 
int main() {
    int a = 5; // a是个左值
    int &ref_a_left = a; // ref_a_left是个左值引用
    int &&ref_a_right = std::move(a); // ref_a_right是个右值引用
 
    change(a); // 编译不过，a是左值，change参数要求右值
    change(ref_a_left); // 编译不过，左值引用ref_a_left本身也是个左值
    change(ref_a_right); // 编译不过，右值引用ref_a_right本身也是个左值
     
    change(std::move(a)); // 编译通过
    change(std::move(ref_a_right)); // 编译通过
    change(std::move(ref_a_left)); // 编译通过
 
    change(5); // 当然可以直接接右值，编译通过
     
    cout << &a << ' ';
    cout << &ref_a_left << ' ';
    cout << &ref_a_right;
    // 打印这三个左值的地址，都是一样的
}
```

<br/>

## 纯右值

运算表达式产生的临时变量、不和对象关联的原始字面量、非引用返回的临时变量、lambda表达式等都是纯右值

一般有：

- 除字符串字面值外的字面值
- 返回非引用类型的函数调用
- 后置自增自减表达式i++，i--
- 算术表达式（a+b，a*b，a&&b，a==b等）
- 取地址表达式等（&a）

<br/>

## 将亡值

通常指将要被移动的对象、T&&函数的返回值、std::move函数的返回值、转换为T&&类型转换函数的返回值

可以理解为**即将要销毁的值**（说是将要，是因为后续有人会将其接收），通过“盗取”其它变量内存空间方式获取的值

在确保其它变量不再被使用或者即将被销毁时，可以避免内存空间的释放和分配，延长变量值的生命周期

常用来完成**移动构造**或者**移动赋值**的特殊任务

<br/>

## 右值（举例）

非字符串的字面量以及枚举项，如：`nullptr`，`true`

后置自增（减）是纯右值，如：`a--`

内置的算术，逻辑，比较表达式，如：`a+b`，`a&b`，`a||b`, `a<b`

内置取地址表达式，this指针，如:`&a`

lamda表达式，如：`[](int a){ return 2*a; }`

转型为非引用的表达式，如：`static_cast<double>(fValue)`，`(float)42`

转型为右值引用的表达式，如：`static_cast<double&&>(fValue)`，`std::move(x)`

左值转右值引用

```cpp
//可以将左值转为右值，再进行右引用
TestClassA kTA2(1000);
// 使用std::move转为右值引用
TestClassA&& c3 = std::move(kTA2);
// 使用static_cast转为右值引用
TestClassA&& c4 = static_cast<TestClassA&&>(kTA2);
// 使用C风格强转为右值引用
TestClassA&& c5 = (TestClassA&&)kTA2;
// 使用std::forwad<T&&>为右值引用
TestClassA&& c6 = std::forward<TestClassA&&>(kTA2);
```

<br/>

<br/>

<br/>

# auto

程序编译的时候进行推导

<br/>

## 推导规则

1、指针或引用（指左值引用）

- 凡是以引用或指针来接收参数的，都直接忽略原来是否是引用
- 而像const和指针的，原封不动的匹配进去

2、万能引用

- 如果传入的是左值，那T和paramtype直接变为左值引用（传进来的就是T的类型和const）
- 如果传入的是右值，就根据类型推导出T的类型，paramType就是T&&

3、既非指针也非引用

- 直接忽略其引用部分，const部分和volatile对象
- 传进来的都当做是值传递，无论原来是不是const，都回归原来的类型
- 例外：如果是const修饰的引用或指针，const会因此保留(const仅会在按值形参处被忽略）

4、`std::initializer`

```cpp
auto x = 27;	//	第三种情况，推导为int
const auto cx = x;	//	第三种情况，推导为const int

const auto& rx = x;	//	第一种情况，推导为const int&

auto&& uref1 = x;	//	第二种情况，传入的左值都变为左值引用，即int&，左值引用
auto&& uref2 = cx;	//	第二种情况，左值，const int&，左值引用
auto&& uref3 = 27;	//	第二种情况，右值，就直接推导，即int&&，右值引用

const char name[] = ":::"; // const char[]

auto arr1 = name;//const char*

auto& arr2 = name;//const char(&)[]

auto func1 = someFunc; // void(*)(int, double)

auto& func2 = someFunc; // void(&)(int, double)

for(auto x : range)	//	原容器中数据的拷贝

for(auto& x : range)	//	原容器中数据的引用
    
for(const auto& x: range) // 对原容器中的数据，只读

for(auto&& x : range)
    
auto&& result = foo(); // auto&& 意味着后边要转发
```

<br/>

## 总结

- `auto` ：拷贝
- `auto&` ：左值引用，只能接左值和常量右值）
- `auto&&` ：万能引用，能接左值和右值
- `const auto&` ：左值引用，能接左值和右值；只读
- `const auto&&` ：常量右值引用，只能接右值；**基本没用**，基本可被 `const auto&` 替代（比 `const auto&` 多一个语义：一定得是右值。然而这没什么用，因为你都不对其进行修改，是左还是右没什么影响）

<br/>

<br/>

<br/>

# decltype

在cpp11中，decltype的主要用途大概就在于声明那些返回值型别依赖于形参型别的函数模板

即decltype可以推导出括号里面的对象的类型，并用于其他的对象

<br/>

<br/>

<br/>

# forward

**作用：会将传入的值，按照T原本的类型返回**

原理：利用**引用折叠**的特性

```cpp
std::forward<T>(param); // T为模板类型，param为参数
```

有一个疑惑：为什么用的时候只要把T放进去就行了？

猜测：用户传入的信息推导后的类型会存入T中，但是我们用的都是解析后的T（即param）

导致我们直接使用param的时候，param都是左值，从而无法确定到底是左值引用还是右值引用（所以需要forward）

<br/>

## 源码

```cpp
/// remove_reference
template<typename _Tp>
struct remove_reference
{ typedef _Tp   type; };

template<typename _Tp>
struct remove_reference<_Tp&>
{ typedef _Tp   type; };

template<typename _Tp>
struct remove_reference < _Tp&& >
{ typedef _Tp   type; };

// 处理左值作为左引用或者右引用
template<typename _Tp>
constexpr _Tp&&
forward(typename std::remove_reference<_Tp>::type& __t) noexcept
{ return static_cast<_Tp&&>(__t); }

// 处理右值作为右引用
template<typename _Tp>
constexpr _Tp&&
forward(typename std::remove_reference<_Tp>::type&& __t) noexcept
{
    static_assert(!std::is_lvalue_reference<_Tp>::value, "template argument"
        " substituting _Tp is an lvalue reference type");
    return static_cast<_Tp&&>(__t);
}    
```

<br/>

<br/>

<br/>

# move

作用：**将对象通过static_cast强转为右值**（语义：不再需要当前变量）

<br/>

为什么说`move`能够提高性能？

- `move`将对象强转为右值，接着赋值的时候会触发移动构造函数，而移动构造函数的语义就是原有的对象是不需要的，从而实现浅拷贝，提高性能
- 换言之，能不能提高性能完全取决于是否有高效的移动构造函数（像int，double类型就不行了）

<br/>

move是不会改变原有数据的const属性（static_cast不会修改const属性）

<br/>

比如

- `bb` 的类型是 `Foo&`，`move` 之后变为 `Foo&&`，会调用移动赋值函数
- `cc` 的类型是 `const Foo`，`move` 之后变为 `const Foo&&`，会调用拷贝赋值函数
- `bb` 的类型是 `const Foo&`，`move` 之后变为 `const Foo&&`，会调用拷贝赋值函数

<br/>

只能说在某个特定的实现中，移动后的对象会变为空，但是c++标准没有规定被移动后的对象为空，所以使用标准库的程序不应当依赖有这些行为的代码

比如说int的move，原来的对象还是没有改变值；而string经过move之后就会变为nullptr，unique_ptr经过move之后变为nullptr

<br/>

## 源码

```cpp
// clang中的实现
/**
  *  @brief  Convert a value to an rvalue.
  *  @param  __t  A thing of arbitrary type.
  *  @return The parameter cast to an rvalue-reference to allow moving it.
*/
template<typename _Tp>
_GLIBCXX_NODISCARD
constexpr typename std::remove_reference<_Tp>::type&& move(_Tp&& __t) noexcept {
    return static_cast<typename std::remove_reference<_Tp>::type&&>(__t);
}

// STRUCT TEMPLATE remove_reference
template <class _Ty>
struct remove_reference {
    using type                 = _Ty;
    using _Const_thru_ref_type = const _Ty;
};

template <class _Ty>
struct remove_reference<_Ty&> {
    using type                 = _Ty;
    using _Const_thru_ref_type = const _Ty&;
};

template <class _Ty>
struct remove_reference<_Ty&&> {
    using type                 = _Ty;
    using _Const_thru_ref_type = const _Ty&&;
};
```

<br/>

<br/>

<br/>

# application

## 移动语义

场景

经常会对一个类对象进行拷贝，而如果原有的类对象不再需要了，那么是不是可以把被拷贝者的数据移动，从而避免深拷贝

即：有了移动语义，更加容易实现浅拷贝

```cpp
class Array {
public:
    Array(int size) : size_(size) {
        data = new int[size_];
    }
     
    // 深拷贝构造
    Array(const Array& temp_array) {
        ...
    }
     
    // 深拷贝赋值
    Array& operator=(const Array& temp_array) {
        ...
    }
 
    // 优雅的实现浅拷贝，从而避免深拷贝
    Array(Array&& temp_array) {
        data_ = temp_array.data_;
        size_ = temp_array.size_;
        // 为防止temp_array析构时delete data，提前置空其data_      
        temp_array.data_ = nullptr;
    }

    ~Array() {
        delete [] data_;
    }
 
public:
    int *data_;
    int size_;
};

// 例1：Array用法
int main() {
    Array a;
 
    // 做一些操作
    .....
     
    // 左值a，用std::move转化为右值
    Array b(std::move(a));
}
```

<br/>

## 万能引用（引用折叠）

**如果任一引用为左值引用，则结果为左值引用。否则（即两个都是右值引用），结果为右值引用**

- T& & 折叠成 T&
- T& && 折叠成 T&
- T&& & 折叠成 T&
- T&& && 折叠成 T&&

**所有引用折叠，最后都代表一个引用：左值引用或右值引用**

<br/>

规则：

万能限定必须是函数模板，可以模板参数是单个，也可以是多个模板参数，形式为**T&&**

万能引用可以接受左值，也可以接受右值

万能引用的T不能被再修饰，否则转为普通右值引用，不能被cv修饰限定

**只存在于模板推导和完美转发中**（比如`auto&&`以及模板函数中的`T&&`）

<br/>

```cpp
//	引用折叠的写法
template<typename T>
void f(T&& param);

int x = 27;
f(x);	//	x是左值，T的类型是int&，param折叠为int&

const int cx = x;
f(cx);	//	cx是左值，T的类型是const int&，param是const int&

const int& rx = x;
f(rx);	//	rx是左值引用，T的类型是const int&，param是const int&

f(27);	//	27是右值，T的类型是int，param折叠为int&&
```

<br/>

## 完美转发

一个具体的应用场景:

需要一个函数能够同时接收左值和右值，并根据不同的类型转发给不同版本的函数

而如果直接用万能引用+左右值函数重载，使用的param都是左值，从而无法判断是左值引用还是右值引用

- param可以被初始化为左值引用或者右值引用，但如果在函数内部要将param传给其它函数，此时的param会被当做左值

<br/>

解决办法：

模板中的 T 保存着传递进来的实参的信息，我们可以利用 T 的信息来强制类型转换我们的 param 使它和实参的类型一致

所以可以使用万能引用 + forward，即利用T的信息实现转发

```cpp
#include <iostream>
using namespace std;

// 接收左值的函数 f()
template<typename T>
void f(T& t) {
	cout << "f(T &)" << endl;
}

// 接收右值的函数f()
template<typename T>
void f(T&& t) {
	cout << "f(T &&)" << endl;
}

// 万能引用，转发接收到的参数 param
template<typename T>
void PrintType(T&& param) {
	// f(param);  // 修改前的版本：只会调用void f(T& t)
    f(std::forward<T>(param)); // 修改后的版本：可以正确区分
}

int main(int argc, char *argv[]) {
	int a = 0;
	PrintType(a);//传入左值
	PrintType(int(0));//传入右值，结果是最后用到的还是左值的版本
}
```

<br/>

<br/>

<br/>

# reference

- [引用折叠和完美转发](https://zhuanlan.zhihu.com/p/50816420)
- [一文读懂C++右值引用和std::move](https://zhuanlan.zhihu.com/p/335994370)
- [左值引用、右值引用、移动语义、完美转发，你知道的不知道的都在这里](https://zhuanlan.zhihu.com/p/137662465)
- [谈谈C++的左值右值，左右引用，移动语意及完美转发](https://zhuanlan.zhihu.com/p/402251966)
- [【Modern C++】深入理解左值、右值](https://mp.weixin.qq.com/s/_9-0iNUw6KHTF3a-vSMCmg)
- [C++11 中的左值、右值和将亡值](https://www.jianshu.com/p/4538483a1d8a)
- https://cloud.tencent.com/developer/article/1561681
