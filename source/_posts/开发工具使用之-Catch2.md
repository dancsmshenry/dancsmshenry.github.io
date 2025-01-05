---
title: 开发工具使用之 Catch2
top: false
cover: false
toc: true
mathjax: true
date: 2024-05-04 13:53:24
password:
summary:
tags:
- Tool
categories:
---





# 介绍

目前使用的测试框架，好处就是只有头文件，方便无论是新人还是老人进行开发（gtest 需要编译成 静态库，使用上有点难度）



# CHECK 和 REQUIRE

`CHECK` 和 `REQUIRE` 用于检测当前括号中的表达式是否为真，常用于校验函数的结果是否符合预期，从而达到测试函数逻辑的目的

```cpp
TEST_CASE("TEST", "[test1]") {
    CHECK(1 == 1);	//	CHECK 在检查项错误的时候，不会导致程序停下来
    REQUIRE(1 == 1); //	REQUIRE 在检查项错误的时候，会停下程序

    CHECK_FALSE(1 == 0);	//	等价于 CHECK(1 != 0);
    REQUIRE_FALSE(1 == 0);	//  等价于 REQUIRE(1 != 0);

    // 检测当前表达式中是否没有异常
    REQUIRE_NOTHROW(expression);
    CHECK_NOTHROW(expression);

    //	检测当前表达式是否有异常
    REQUIRE_THROWS(expression);
	CHECK_THROWS(expression);
}
```

<br/>

但是 CHECK 这种，在宏展开的时候会有些问题：

```cpp
//	error
CHECK(a == 1 && b == 2);
CHECK(a == 2 || b == 1);

//	right
CHECK((a == 1 && b == 2));
CHECK((a == 2 || b == 1));
```

<br/>

<br/>

# SECTION

`SECTION` 主要用于测试某个类的多个函数。

```cpp
TEST_CASE( "vectors can be sized and resized", "[vector]" ) {
    std::vector<int> v( 5 );

    REQUIRE( v.size() == 5 );
    REQUIRE( v.capacity() >= 5 );

    SECTION( "resizing bigger changes size and capacity" ) {
        v.resize( 10 );
        REQUIRE( v.size() == 10 );
        REQUIRE( v.capacity() >= 10 );
    }

    SECTION( "resizing smaller changes size but not capacity" ) {
        v.resize( 0 );
        REQUIRE( v.size() == 0 );
        REQUIRE( v.capacity() >= 5 );
    }
}
```

<br/>

<br/>

# Matchers

当前的表达式在 matcher 中是否成立

```cpp
REQUIRE_THAT(expression, matchers);
```

<br/>

## String

验证某个 string 是否以某个 string 结束：

```cpp
using Catch::Matchers::EndsWith; // or Catch::EndsWith

std::string str = getStringFromSomewhere();

REQUIRE_THAT(str, EndsWith("as a service" ))
```

<br/>

验证某个 string 是否以某个 string 开始：

```cpp
using Catch::Matchers::StartsWith; // or Catch::EndsWith

std::string str = getStringFromSomewhere();

REQUIRE_THAT(str, StartsWith("as a service"))
```

<br/>

验证某个 string 是否包含某个 string：

```cpp
using Catch::Matchers::StartsWith; // or Catch::EndsWith

std::string str = getStringFromSomewhere();

REQUIRE_THAT(str, Contains("as a service"))
```
