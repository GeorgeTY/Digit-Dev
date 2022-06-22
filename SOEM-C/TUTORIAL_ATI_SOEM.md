# 使用 SOEM 读取 ATI Nano-17 传感器数值

## Table of Contents
1. [Introduction](#introduction)
    1. [Requirements](#requirements)
2. [Usage](#usage)
    1. [Build](#build)
    2. [Run](#run)
3. [Known Issues](#known-issues)
4. [Contact](#contact)

## Introduction
本文档为使用SOEM读取 ATI Nano-17 力/力矩传感器数据的教程。
我修改过的主程序文件为 `./test/linux/simple_test`

有两种方式与程序交互：
1. 在终端里直接读取数据
2. 用Socket与Python脚本交换数据

本教程仅为第一种方式的教程。第二种方式的教程见 `./TUTORIAL_Python.md`。


### Requirements
* Linux x86-PC （本程序在Ubuntu 20.04上开发）
* Intel 网卡（SOEM的要求）
* 网线（**按ATI EtherCAT OEM板文档连接网线的各个端子，可参照我连接的网线**）
    >网线粗细和端子大小选择 Molex 50058-8000 (28-32 AWG) or Molex 50079-8000 (26-28 AWG) 
* **PoE 电源**（为 ATI EtherCAT OEM板 供电，最好选择可以自适应供电的型号，以免因网线接错而烧坏板子）

## Usage

### Build
1. `./test/linux/simple_test/simple_test.c` 已经编写为使用Socket连接的程序，直接在终端中打开的话不会有输出。如果你需要直接从终端中读取数据，你需要根据你的需要修改`./test/linux/simple_test/simple_test.c`中 `simple_test` 函数。
2. 编译

    在终端中打开 `./SOEM-C` 目录

   * `mkdir build`
   * `cd build`
   * `cmake ..`
   * `make`

    编译后，可执行文件会出现在 `./SOEM-C/build/linux/simple_test/` 中。(你可以通过修改 `./CMakeLists.txt` 来修改你想要编译的源文件)

### Run
3. 注入PoE供电后，将圆形的ATI EtherCAT OEM板通过网线连接到PC上的Intel网口，几秒后应看到板上闪绿灯，表示供电成功。如果没看到灯亮，请检查供电。
4. 在终端里使用 `ifconfig` 命令查看连接ATI EtherCAT OEM板对应的网卡地址，例如 `enp0s31f6` 。
5. 在终端内运行 `sudo /SOEM-C/build/linux/simple_test/simple_test enp0s31f6` ，最后一个参数为你ATI EtherCAT OEM板对应的网卡地址
 

## Known Issues
1. 无法稳定进入Operational模式，如果无法进入可能需要多运行几次程序。(修正这个Bug的方法可以参考[这个GitHub连接](https://github.com/OpenEtherCATsociety/SOEM/issues/251)，因本人能力有限，不能做到100%稳定……同时，我在Windows系统下尝试使用Beckhoff TwitCAT读取这个传感器数据时，也不能100%稳定，问题可能在ATI的ECATOEM板上，可尝试联系厂家)
2. 没有做修改传感器单位的部分程序，只能读取Fx、Fy、Fz、Tx、Ty、Tz，各值的单位可以参考终端输出（默认为N, N-mm）。
3. 进入Operational模式后，请求传感器数据时有概率会卡住，几秒后会将请求过的数据一次性发送回来，原因不明。
4. 采样率不高。

## Contact
ratiomiith@gmail.com
