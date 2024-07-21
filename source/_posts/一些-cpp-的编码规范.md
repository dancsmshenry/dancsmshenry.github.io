---
title: 一些 cpp 的编码规范
top: false
cover: false
toc: true
mathjax: true
date: 2024-03-17 16:11:58
password:
summary:
tags:
- CPP
categories:
---



## 什么时候使用前置声明

为了防止循环引用的情况发生

避免头文件的使用者引入过多的无用的头文件（希望屏蔽底层的实现细节）

<br/>

<br/>

<br/>

## 是否需要有 assert

assert 只在 debug 的模式下才会生效，而 debug 模式并不会是生产模式下使用的，因此最好只在调试阶段使用

可以使用 static_assert，主要是给模板用的 

<br/>

<br/>

<br/>

## 函数的命名规范

当 socket 收到具体的数据的时候，使用 Onxxx，例如 onTcpMessage，onUdpMessage

<br/>

<br/>

<br/>

## 关于 auto 的使用规范

在标准库的迭代器里面使用，或者标准库函数里面放 lambda 表达式时，（入参可以为 auto，14之后是可以的）

在返回值确定的情况下（例如说 `make_shared_<int>`，又或者说是 `xxx.get_future()`）

或者说变量的命名清楚确定的情况下（例如 afterResult 等）

<br/>

<br/>

<br/>

## 关于 log 的打印和等级

使用 error 的情况：解析数据的过程中出现了问题，或者数据中有意料之外的情况（比如说2012的版本，是没有 tls 的接口的）；读取数据发生错误，或者长度不符合预期

使用 debug 的情况：正式的代码中是不能有 debug 的代码的，debug仅在调试和测试的时候使用

使用 info 的情况：代码执行某个流程开始或者结束

使用 warn 的情况：当收到了报文，但在校验的时候发生了错误

<br/>

<br/>

<br/>

## shared_ptr，unique_ptr 还是 raw point 的使用规范

对于智能指针 std::unique_ptr/std::shared_ptr 到底是传入 引用还是值就目前的场景来看，感觉更多的时候需要传入的是值

<br/>

<br/>

<br/>

## 对于 function 和 lambda 的区别分析

对于 funciton，传递 引用 值 右值 那个效率更高

lambda 转 std::function<void()>& 为什么不行？

