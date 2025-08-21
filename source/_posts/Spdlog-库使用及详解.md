---
title: Spdlog 库使用及详解
top: false
cover: false
toc: true
mathjax: true
date: 2025-08-21 22:38:50
password:
summary:
tags:
- CPP
categories:
---

# 前置知识

- 函数 fwrite 是 glibc 封装的一层有关 write 的接口，会在应用层再创建一个缓冲的 buffer，当调用的 fwrite 到一定的数量时，才会调用一次操作系统原生的 write。也因此有了函数 fflush，将这个缓冲的 buffer 内容，强制调用一次 write。
- 而 write 也不一定能够强制刷盘，所以还需要再强制调用一次 fsync（或是 fdatasync）（spdlog 估计是不想再上层再封装一个缓冲的 buffer，所以就走 glibc 的接口）

<br/>

# 整体架构

异步逻辑的类图

![async](spdlog-async.svg)

<br/>

Pattern 的类图

![format](spdlog-format.svg)

<br/>

Sink 的类图

![sink](spdlog-sink.svg)

<br/>

总体图

![total](spdlog-total.svg)
