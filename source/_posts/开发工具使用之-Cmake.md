---
title: 开发工具使用之 Cmake
top: false
cover: false
toc: true
mathjax: true
date: 2023-11-21 23:25:05
password:
summary:
tags:
- Tool
categories:
---





# 0、通用的 CMakeLists 模板

目前在 linux 下使用的 cmake 版本为 3.16，而在 windows 下使用的版本为 3.20

```cmake
# 指定 cmake 所需的最小版本
cmake_minimum_required(VERSION 3.16)

# 指定 cpp 编译的版本
set(CMAKE_CXX_STANDARD 17)

# 是否一定要支持上述指定的 cpp 标准
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 项目的基本信息，名字版本号
project(learning_cmake LANGUAGES C CXX)

# 编译得到的二进制文件是否和当前源码是在同一目录下，如果是的话就需要警告
if (PROJECT_BINARY_DIR STREQUAL PROJECT_SOURCE_DIR)
	message(WARNING "The binary directory of CMake cannot be the same as source directory!")
endif()

# 设置项目的编译模式（可以理解为项目的优化程度）
if (NOT CMAKE_BUILD_TYPE)
	set(CMAKE_BUILD_TYPE Release)
endif()

# 设置最终的可执行文件
add_executable(main)

# 添加指定目录下需要编译的文件
aux_source_directory(. SOURCES)
aux_source_directory(src SOURCES)

# 将文件添加到最终的编译单元中
target_sources(main PUBLIC ${SOURCES})

# 编译出静态库
add_library(dog STATIC dog/dog.cc)

# 链接静态库
target_link_libraries(main PUBLIC dog)

# 添加头文件搜索路径
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/dog)

```

<br/>

<br/>

<br/>

# 1、cmake 的命令行使用方法

通过 -B 生成对应的 makefile 或者 ninja 文件，其中路径被设置为 build（如果不设置那么就会在当前路径生成）

后续参数则是设置一些编译参数，例如 DCMAKE_EXPORT_COMPILE_COMMANDS 用于生成 json 数据库文件，方便使用插件 clangd 进行代码跳转，DCMAKE_INSTALL_PREFIX 是用于设置安装目录，DCMAKE_BUILD_TYPE 是用于设置安装的版本

```shell
cmake -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=./build/release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

<br/>

编译，将编译的目录指定为 build，其中 --parallel 4 则是编译时用到的线程数

```shell
cmake --build build --parallel 4
```

<br/>

安装，将当前项目安装到指定目录中，上述指定了将目录安装在 build/release 中

```shell
cmake --build build --target install
```

<br/>

<br/>

通过 -G 选择，来控制 cmake 的生成器，可选的有 ninja、makefile以及 .sln

```shell
# 选择 ninja 作为后续的生成构建器
cmake -GNinja -B build

# 这个有点坑爹的就是，一旦你修改了构造器，那么后续就会一直是这个构造器
# 所以后续需要设置回 makefile
# 还有就是，直接使用这个命令，就等价于使用了 cmake -B
cmake -G"Unix Makefiles"
```

<br/>

<br/>

## cmake 编译的两阶段

第一阶段是 `cmake -B build`，称为**配置阶段**（configure），这时只检测环境并生成构建规则，会在 build 目录下生成本地构建系统能识别的项目文件（Makefile 或是 .sln）

在配置阶段，可以利用 -D 指定配置变量（即一些缓存变量），这些变量会被在本地缓存，即使后续只是 cmake -B build ，前面的缓存也会被使用到

<br/>

第二阶段是 `cmake --build build`，称为**构建阶段**（build），这时才实际调用编译器来编译代码

<br/>

<br/>

<br/>

# 2、cmake 的基本语法

## list

向指定的 list 进行操作

```cmake
list(APPEND <list><element> [<element>...])

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake")
```



`` 向 list 中添加数据 element

PS：这里给 .cmake 模块指定了文件夹以后，后续的子模块可以直接 include 对应的 .cmake 文件并使用，而不需要重新指定路径

<br/>

<br/>

## option

```cmake
option(ARA_CXX_STANDARD_EXTENSIONS "Description" OFF)
```

一般用于控制编译流程，可以理解为 c 语言里面的宏，即条件编译

`option(<variable> "<help_text>" [value])`

- `variable`：定义选项名称
- `help_text`：说明选项的含义
- `value`:定义选项默认状态，一般是 OFF 或者 ON，除去 ON 之外，其他所有值都为认为是 OFF
- PS：如果主目录的 cmakelists 和子目录的 cmakelists 中定义的变量值不同，比如主目录中定义为 ON，子目录中定义为 OFF，那么遵循主目录中的内容

这里看到主目录定义了 ARA_CXX_STANDARD_EXTENSIONS ，后面的子目录就会用这个宏，来判断是否要加上 c++ 的编译拓展

<br/>

<br/>

## if

```cmake
if (CMAKE_BINARY_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
	#正文
	# STREQUAL 用于比较字符串，相同的话返回 true
endif()
```

<br/>

<br/>

## message

message 一般用于输出，而输出也分为不同的等级（第一个 slot 写输出语句的等级，第二个 slot 写输出的具体内容）

```cmake
# 输出语句字符串
message("hello world!") # hello world!

# STATUS 输出状态信息，会带有 -- 前缀
message(STATUS "hello world!") # -- hello world!

# NONE 输出通知信息
message(NONE "test message in cmake!") # NONEtest message in cmake!

# FATAL_ERROR 输出错误信息并终止程序执行
message(FATAL_ERROR "Building in-source is not supported. Create a build dir and remove CMakeFiles and CMakeCache.txt")

# SEND_ERROR 输出错误信息并继续执行
message(SEND_ERROR "Building in-source is not supported. Create a build dir and remove CMakeFiles and CMakeCache.txt")

# WARNING 输出警告信息，继续执行
message(WARNING "test in warning")
```

<br/>

<br/>

<br/>

# 3、cmake 的基本配置

```cmake
# 指定最低所需的 cmake 版本，当用户使用的 cmake 小于这个版本的时候，就会报错
cmake_minimum_required(VERSION 3.16 FATAL_ERROR) # 在2.6以后的版本会被接受但是忽略
cmake_minimum_required(VERSION 3.15...3.20) # 指定使用 cmake 的版本范围

# 用于控制编译模式，分为 debug，release，minsizerel，relwithdebinfo 几种模式
set(CMAKE_BUILD_TYPE Release)

# project 初始化项目信息，并把当前 cmakelists.txt 所在位置作为根目录
# 第一个 slot （NAME）用于指定项目的名称
# 第二个 slot （VERSION）用于指定项目的版本号（可以把当前项目的版本号设定为 x.y.z；再通过一些宏可以获得具体的版本号）
# 第三个 slot （DESCRIPTION）用于补充项目的具体信息
# 第四个 slot （LANGUAGES）用于指定项目使用的语言（可以同时写多种语言）
project(LearningCpp VERSION 1.0.0 LANGUAGES CXX)
project(LearningC
	VERSION 1.0.0
	DESCRIPTION "a free open-source"
	HOMEPAGE_URL http://www.baidu.com
	LANGUAGES CXX C
	)

# 一些常用的宏
# CMAKE_CURRENT_SOURCE_DIR 表示当前源码目录的位置，例如 ~/hellocmake
# CMAKE_CURRENT_BINARY_DIR 表示当前输出目录的位置，例如 ~/hellocmake/build
# PROJECT_SOURCE_DIR 表示最近一次调用 project 的 CMakeLists.txt 所在的源码目录（我理解为就是根目录的路径）
# CMAKE_CURRENT_SOURCE_DIR 表示当前 CMakeLists.txt 所在的源码目录
# CMAKE_SOURCE_DIR 表示最为外层 CMakeLists.txt 的源码根目录
# CMAKE_BINARY_DIR 指的是存放二进制文件的文件夹

# 设置 cpp 的编译选项
set(CMAKE_CXX_STANDARD 17) # 选择 cpp 的编译版本；因此不要用 -std=17 指定版本，因为这样跨平台就会出问题；不过这里配置的一般是当前主项目的编译版本，其中子项目，例如编译成的相关静态库则需要用 set_target_properties 来表示
set(CMAKE_CXX_STANDARD_REQUIRED ON) # bool 类型，表示是否一定要支持上述指定的 cpp 标准，off 表示 CMake 检测到编译器不支持 C++17 时不报错，而是默默调低到 C++14 给你用；on 则发现不支持报错，更安全
set(CMAKE_CXX_EXTENSIONS ON) # 设为 ON 表示启用 GCC 特有的一些扩展功能；OFF 则关闭 GCC 的扩展功能，只使用标准的 C++；要兼容其他编译器（如 MSVC）的项目，都会设为 OFF 防止不小心用了 GCC 才有的特性；此外，最好是在 project 指令前设置 CMAKE_CXX_STANDARD 这一系列变量，这样 CMake 可以在 project 函数里对编译器进行一些检测，看看他能不能支持 C++17 的特性
```

<br/>

<br/>

<br/>

# 4、如何在项目中添加新的.cc文件

方法一

```cmake
# add_executable 用于设置编译最终得到的可执行文件，以及需要编译的文件
add_executable(main main.cc)
```

<br/>

<br/>

方法二

```cmake
# 先设置最终得到的可执行文件，再依次添加源文件
add_executable(main)
target_sources(main PUBLIC main.cc other.cc)
```

<br/>

<br/>

方法三

```cmake
# 先设置最终得到的可执行文件，再用一个变量存储源文件，最后依次添加源文件
add_executable(main)
set(sources main.cc other.cc)
target_sources(main PUBLIC ${sources})
```

<br/>

<br/>

方法四

```cmake
# 使用 GLOB 自动查找指定拓展名的文件
add_executable(main)
file(GLOB sources *.cc)
file(GLOB sources CONFIGURE_DEPENDS *.cpp *.h) # 可以自动将新的文件添加
file(GLOB sources CONFIGURE_DEPENDS *.cpp *.h mylib/*.cpp mylib/*.h) # 将子文件夹里的文件一起添加进来
target_sources(main PUBLIC ${sources})
```

<br/>

<br/>

方法五

```cmake
# 使用 aux_source_directory 自动搜集需要文件的后缀名（我个人比较认同的使用方式）
add_executable(main)
aux_source_directory(. sources)
aux_source_directory(mylib sources)
target_sources(main PUBLIC ${sources})
```

<br/>

<br/>

方法六

```cmake
# 使用 GLOB_RECURSE 自动包含所有子文件夹下的文件（但是缺点就是可能会将build里面的文件一同加进来，所以我觉得这种比较差，就不用了...）
add_executable(main)
file(GLOB_RECURSE sources CONFIGURE_DEPENDS *.cc *.h)
target_sources(main PUBLIC ${sources})
```

<br/>

<br/>

<br/>



# 5、如何将代码编译成库

把文件编译成一个静态库

```cmake
# 第一个是库的名字，第二个表示要将当前库编译成静态、动态还是对象库，最后是要编译的文件
add_library(mylib STATIC mylib.cc)
add_library(mylib SHARED mylib.cc)
add_library(mylib OBJECT mylib.cc) # 对象库类似于静态库，但不生成 .a 文件，只由 CMake 记住该库生成了哪些对象文件
# 对象库不生成 .a 文件，只由 CMake 记住该库生成了哪些对象文件，因此就有人推荐用对象库代替静态库，避免跨平台的麻烦

add_executable(main main.cc)

target_link_libraries(main PUBLIC mylib)
```

<br/>

一个比较坑的问题，动态库无法连接静态库，解决办法就是设置 `set(CMAKE_POSITION_INDEPENDENT_CODE ON)`

```cmake
# 设置全体库为 PIC
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

add_library(otherlib STATIC otherlib.cc)

add_library(mylib SHARED mylib.cc)
target_link_libraries(mylib PUBLIC otherlib)

add_executable(main main.cc)
target_link_libraries(main PUBLIC mylib)
```

<br/>

<br/>

<br/>

# 6、如何引用第三方库

<br/>

<br/>

<br/>

# 7、如何设置头文件的搜索路径

`include_directories`用于将给定的目录添加到编译器，便于搜索包含文件的目录

```cmake
# 将当前目录下的 include 目录添加到后续 .h 文件的搜索路径中
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
```

也就是说，后续在 .cc 文件中填写的如果是相对路径，那么就会被解释为在当前这个源目录下的路径

比如说我们想要引入 include 文件夹下的 test.h 文件，文件真实路径为 `include/test.h`

那么在主目录中的 main.cc 就只需要 `#include "test.h"`即可引入

<br/>

<br/>

`target_link_directories`则更加细粒度的规定了头文件的引用范围，作用和`include_directories`相同

<br/>

**PRIVATE**

被设定为 PRIVATE 的目录，下属的文件不能对项目外暴露，也不对项目内设为 PUBLIC 的文件暴露

举例： include 下有两个目录：private 和 public，二者都存放 .h 文件，src 目录存放 .cc 文件

其中目录 private 被设为 PRIVATE，目录 public 被设为 PUBLIC

则，src 下的 .cc 文件可以使用 private 的文件，include/public 下的头文件和项目外的文件不可以使用 private 的文件

<br/>

从两种目录结构的角度进行理解：

角度一：项目目录的结构是，将 .h 文件统一放到 include 中，再在 include 中拆分出 private 和 public

- 则 PRIVATE 表示该目录下的头文件，只能给本目录下的 .cc 文件使用，不对外提供接口（例如一些辅助性的类）

<br/>

角度二：项目目录的结构是，将 .h 文件和 .cc 文件都放在一起，按照库或模块对文件进行分类

- 设库 B 为该项目对外提供的库，库 B 依赖于库 A，库 A 的代码在库 B 的代码结构中，而将库 A 设为 PRIVATE 后，则表示库 A 只会提供给库 B 使用，而不会传导给库 B 的使用者，即没有传递性

```cmake
target_include_directories(dog PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include/private)
```

<br/>

**INTERFACE**

被设定为 INTERFACE 的目录，下属的文件对项目外的文件以及项目内被设为 PUBLIC 的文件暴露，不对项目内的可执行文件暴露

举例： include 下有两个目录：interface 和 public，二者都存放 .h 文件，src 目录存放 .cc 文件

其中目录 interface 被设为 INTERFACE，目录 public 被设为 PUBLIC

则，src 下的 .cc 文件不可以使用 interface 的文件，include/public 下的头文件和项目外的文件可以使用 interface 的文件

<br/>

从两种目录结构的角度进行理解：

角度一：项目目录的结构是，将 .h 文件统一放到 include 中，再在 include 中拆分出 interface 和 public

- 则 INTERFACE 表示该目录下的头文件，是对外提供接口的（因此可以被设为 PUBLIC 的头文件使用），但是不能对当前目录下 .cc 文件暴露

角度二：项目目录的结构是，将 .h 文件和 .cc 文件都放在一起，按照库或模块对文件进行分类

- 设库 B 为该项目对外提供的库，库 B 不依赖于库 A，库 A 的代码在库 B 的代码结构中，而将库 A 设为 INTERFACE  后，则表示库 A 不会提供给库 B 使用，而是会直接给使用者用户，也不算有传递性

```cmake
target_include_directories(dog INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include/public)
```

<br/>

**PUBLIC**

被设定为 PUBLIC 的目录，谁都可以使用

<br/>

从两种目录结构的角度进行理解：

角度一：项目目录的结构是，将 .h 文件统一放到 include 中，再在 include 中拆分出 interface 和 public

- 则 PUBLIC 表示该目录下的头文件，谁都可以使用

角度二：项目目录的结构是，将 .h 文件和 .cc 文件都放在一起，按照库或模块对文件进行分类

- 设库 B 为该项目对外提供的库，库 A 的代码在库 B 的代码结构中，无论库 B 是否依赖于库 A，只要将库 A 设为 PUBLIC 后，则库 B 和用户使用者都可以使用，即有传递性

```cmake
target_include_directories(dog PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include/public)
```

<br/>

<br/>

<br/>

# 8、如何添加并构建子模块

```cmake
add_subdirectory(dog)
```

具体格式：`add_subdirectory (source_dir [binary_dir] [EXCLUDE_FROM_ALL])`

必选参数：`source_dir` 指定一个子目录，子目录下应该包含 CMakeLists.txt 文件和代码文件（可以是相对路径或绝对路径）

可选参数：binary_dir 指定一个子目录，用于存放子目录的二进制文件（如果不指明的话，那么生成的二进制文件和 makefile 就会和主目录是在同一个路径下），也可以写相对路径（比如是在主目录下的 cmakelists.txt 中写的，那么相对路径就可以写为 ../demo-apps/build）

<br/>

<br/>

<br/>

# 9、如何配置编译对象的属性

`set_target_properties(dog PROPERTIES POSITION_INDEPENDENT_CODE ON)`

<br/>

<br/>

<br/>

# 10、如何安装库

install 指令

DIRECTORY，例如 `include(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include ESTINATION${CMAKE_INSTALL_INCLUDEIR})`

就是将指定目录下的文件（include 下的文件），全部移动到指定文件目录下

FILE，用法同上，就是将指定文件，移动到指定目录下

TARGET，安装指定的目标文件

```cmake
# 将二进制可执行文件 myrun 安装到目录 ${PROJECT_SOURCE_DIR}/build/bin
install(TARGETS myrun
    RUNTIME DESTINATION ${PROJECT_SOURCE_DIR}/build/bin # 二进制可执行文件
    LIBRARY DESTINATION ${PROJECT_SOURCE_DIR}/build/lib # 动态库
    ARCHIVE DESTINATION ${PROJECT_SOURCE_DIR}/build/lib # 静态库
)
```



<br/>

<br/>

<br/>

# 11、关于 .cmake 文件

背景：为了防止 cmakelists.txt 文件过长，因此将其分为几个模块，同时也方便平台的组件共用该 cmake 文件，cmake 模块文件一般是后缀名为 .cmake

`CMAKE_CURRENT_LIST_DIR` 是用分号分隔的目录列表（是一个 list ，也就是说可以有多个路径），cmake 使用该路径检查附带的 .cmake 文件模块；默认为空

<br/>

<br/>

<br/>

# 12、如何在 windows 下使用 cmake

先去官网上下载 msi 安装包，然后安装

接着在 vscode 中安装插件 cmake 和 cmake tools

接着，cmake 有 makefile 和 ninja，所以需要把他们的可执行程序 exe 放到 cmake/bin 的目录下（当然，这个目录是被加入到系统变量中的）

- ninja 可以直接在官网的 github 上下载二进制程序
- cmake 则需要先下载 mingw32 （我这里是和 llvm 一起下载了），然后把其中 llvm/bin 的可执行程序 mingw32-make 放到 cmake/bin 的目录下，再改名为 make

最后是配置插件，cmake generator 将其配置为 Unix makefiles

注意：这个插件每次一打开目录，就会将 cmakelists 中的内容编译一遍，而上面则是用于修改 cmake 的默认生成构造器

<br/>

记录一次灵异事件：在 windows 上构建 cmake 项目，始终出现找不到编译器的情况

```shell
-- Building for: NMake Makefiles
-- The C compiler identification is unknown
-- The CXX compiler identification is unknown
CMake Error at CMakeLists.txt:11 (project):
  The CMAKE_C_COMPILER:

    cl

  is not a full path and was not found in the PATH.
```

后续使用了指令 cmake -G"Unix Makefiles"  -B build ，才恢复正常

而且，必须要最开始执行这条指令，指定了 makefile 作为构造器，才能够正常运行

<br/>

<br/>

<br/>

# 其他

记录一个之前遇到的小bug：

`set(CMAKE_EXPORT_COMPILE_COMMANDS ON)` 这句话不起作用，感觉是版本的原因

需要修改为`set(CMAKE_EXPORT_COMPILE_COMMANDS ON CACHE INTERNAL "")`，这样才能生成 json 文件，以便 clang 实现代码跳转

cmake中的 public，interface 和 private 大体思路上都是一样的，表示传递的依赖性：

public表示自己可以使用指定的头文件或是链接的库

interface表示自己不可以使用指定的头文件或是链接的库，但是当别的编译单元 target 指定当前单元时，可以使用 interface 标记的头文件和链接的库

private表示自己可以使用指定的头文件或是链接的库，但是别的编译单元使用当前单元时，就无法使用指定的头文件和链接的库

https://blog.csdn.net/sinat_37231928/article/details/121684722

https://zhuanlan.zhihu.com/p/82244559

