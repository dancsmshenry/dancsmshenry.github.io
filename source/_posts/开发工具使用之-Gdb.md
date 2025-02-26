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
categories:
---



# 常用的 gdb 指令

```shell
bt # 查看的堆栈

f 1/2/3/4 # 查看具体第几个帧栈

p 变量名字 # 查看具体某个变量

print/x 变量名字 # 打印变量的数据，以十六进制的形式打印（默认的是 8 进制）

thread apply all bt # 查看所有线程的堆栈

t 线程号 # 切换到指定的线程看堆栈，或者 thread 线程号

gdb attach 进程号 # 进入某个进程查看当前的堆栈信息，有时候可能需要 sudo 的权限

info threads  # 查看当前所有线程的调用栈

shell clear # 清理 gdb 的控制台

kill -2 processId # 等价于对进程 ctrl + c

kill -9 processId # signal kill
```



# 如何生成 coredump

1. 在 shell 中输入 `ulimit -c`，查看当前允许的生成 coredump 文件的大小
2. 接着在 shell 中输入 `ulimit -c unlimited`允 许生成无限大小的 coredump 文件
3. 再在 shell 中输入 `echo "kernel.core_pattern=/tmp/core-%e-%p-%t" | sudo dd of=/proc/sys/kernel/core_pattern` 指定 coredump 文件的生成路径（可以用 vim 修改对应文件，但是有些场景可能会无法写入，所以需要强行用 dd 写进去）
4. 生成 coredump 后会到指定路径下，然后 gdb 可执行文件，接着在 gdb 的输入模式下，写 core /tmp/core** ，后面填写的是 coredump 文件的路径
