---
title: 开发工具使用之 Gdb
top: false
cover: false
toc: true
mathjax: true
date: 2025-02-12 00:00:11
password:
summary:
tags:
- Tool
categories:
---



# 多线程调试

```shell
# 查看所有线程的堆栈
thread apply all bt

# 切换到指定线程的堆栈
t 线程号

# 进入正在运行的程序查看堆栈（一般用于排查死锁或者进程卡死的问题）
gdb attach 进程号

# 查看当前所有线程的调用栈
info threads
```

<br/>

<br/>

<br/>

# 调试堆栈

```shell
# 查看的堆栈
bt

# 查看具体第几个帧栈
f 1/2/3/4

# 查看具体某个变量
p 变量名字
# 打印变量的数据，以十六进制的形式打印（默认的是 8 进制）
print/x 变量名字 

# 清理 gdb 的控制台
shell clear
```

<br/>

<br/>

<br/>

# 如何生成 coredump

1. 在 shell 中输入 `ulimit -c`，查看当前允许的生成 coredump 文件的大小
2. 在 shell 中输入 `ulimit -c unlimited`，允许生成无限大小的 coredump 文件
3. 在 shell 中输入 `echo "kernel.core_pattern=/tmp/core-%e-%p-%t" | sudo dd of=/proc/sys/kernel/core_pattern`
   1. 用于指定 coredump 文件的生成路径（有些场景可能会无法写入，需要强行用 dd 写进去）
4. coredump 会生成到指定路径下，然后 `gdb 可执行文件 coredump文件`
