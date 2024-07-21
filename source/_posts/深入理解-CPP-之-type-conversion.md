---
title: 深入理解 CPP 之 type conversion
top: false
cover: false
toc: true
mathjax: true
date: 2022-10-23 17:03:40
password:
summary:
tags:
- CPP
categories:
---





# backround

**基类对象转换为派生类对象，是不安全的**

- 派生类是包含于基类的，即基类的“体积”是小于派生类的

- 如果一个指向基类的指针强转为指向派生类的指针（该指针始终指向基类，只是指针类型变了），再通过该指针调用派生类的特有方法或者数据
- 就会访问到未知的数据，从而导致崩溃
- 所以这种转换在`dynamic_cast`中就会报错

<br/>

**派生类对象转换为基类对象，是安全的**

- 理由同上，派生类是包含于基类的，因此对方法或数据的使用，不会造成越界

<br/>

**派生类指针只能指向派生类，基类指针可以指向基类或派生类**

<br/>

**type conversion针对的是指针和引用**

- 引用可以理解为指针的语法糖

<br/>

<br/>

<br/>

# static_cast

## 用途

- 等价于C里面的强制转换，可以将`non-const`对象转为`const`对象
- 用于基本数据类型之间的转换（例如`int`转换为`char`）
- 把空指针转换为目标类型的空指针
- 把任何类型的表达式转换成`void`类型
- 也可以用于类对象之间的转换（但没有动态类型检查，所以不安全）

格式：`static_cast<type-id>(expression);`

<br/>

## 优点

更加明显，能够一眼看出转换为什么类型

更加安全

<br/>

## 缺点

没有运行时类型检查来保证转换的安全性（`dynamic_cast`）

不能用于在不同类型指针之间的转换

不能用于整型和指针之间的的转换

不能用于不同类型的引用之间的转化

**不能去除掉已有对象的const或volatile，或者__unaligned属性**

<br/>

## 总结

可以理解为C里面强制转换的平替，但又有一些局限性

<br/>

<br/>

<br/>

# dynamic_cast

## 用途

- 将基类的指针或引用安全地转换为派生类的指针或引用（前提：该基类指针指向的是派生类，同时**基类必须有虚函数**）
- 或是将派生类的指针或引用安全地转换为基类的指针或引用（基类不需要有虚函数）

格式：`dynamic_cast <type-id>(expression)`，其中`type-id`可以是类指针，类引用或`void*`，`expression`也要是对应的类型

<br/>

若对指针进行`dynamic_cast`，失败返回`nullptr`，成功返回正常cast后的对象指针

若对引用进行`dynamic_cast`，失败抛出一个**异常**，成功返回正常cast后的对象引用

<br/>

## 代码

```cpp
#include <iostream>
#include <assert.h>

using namespace std;

// 父类
struct Tfather {
    virtual void f() { cout << "father's f()" << endl; }
};

// 子类
struct Tson : public Tfather {
    void f() { cout << "son's f()" << endl; }
    int data; // 子类独有的成员
};

int main() {
    Tfather father;
    Tson son;
    son.data = 123;

    Tfather *pf;
    Tson *ps;

    //	上行转换：没有问题
    ps = &son;
    pf = dynamic_cast<Tfather *>(ps);
    pf->f();

    //	下行转换（pf实际指向子类对象）：没有问题
    pf = &son;
    ps = dynamic_cast<Tson *>(pf);
    ps->f();
    cout << ps->data << endl; // 访问子类独有成员有效

    //	下行转换（pf实际指向父类对象）：含有不安全操作，dynamic_cast则返回nullptr（而static_cast则会无视）
    pf = &father;
    ps = dynamic_cast<Tson *>(pf);
    assert(ps != nullptr); // 违背断言，阻止以下不安全操作
    ps->f();
    cout << ps->data << endl; // 不安全操作，对象实例根本没有data成员
}
```

<br/>

## 总结

主要用于类之间的转换

上行转换（派生类转换为基类），和`static_cast`等效

下行转换（基类转换为派生类），`dynamic_cast`具有类型检查功能，更加安全

相比`static_cast`会更加耗时，因为`dynamic_cast`会在运行时进行类型检查来保证转换的安全性

<br/>

<br/>

<br/>

# reinterpret_cast

## 用途

- 可以将整型转换为指针，也可以把指针转换为数组，或是将指针和引⽤之间进⾏转换

- 从底层对数据进⾏重新解释；依赖具体的平台，可移植性差
- 等价于C里面的强制转换

格式：`reinterpret_cast<type-id>(expression);`，`type-id`必须是一个指针、引用、算术类型、函数指针或者成员指针，用于类型之间进行强制转换

<br/>

<br/>

<br/>

# const_cast

## 用途

- 给已有对象添加`const`或删除`const`，或是`volstile`
- 是唯一一个可以操作常量的转换符
- 常量指针（或引用）被转化为非常量指针（或引用），并且仍然指向原来的对象
- 一般用于修改底层指针，如`const char *p`形式

格式：`const_cast <type-id> (expression);`
