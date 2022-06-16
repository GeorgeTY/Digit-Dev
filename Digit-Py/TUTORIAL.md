# Digit 标定流程

## Table of Contents
1. [Introduction](#introduction)
    1. [Requirements](#requirements)
    2. [Overview](#overview)
2. [Usage](#usage)
3. [Known Issues](#known-issues)


## Introduction
本文档为使用 ATI Nano-17 力/力矩传感器标定 Digit 传感器的教程。

### Requirements
* Linux x86-PC （本程序在Ubuntu 20.04上开发）
* Intel 网卡（SOEM的要求）
* 网线（**按ATI EtherCAT OEM板文档连接网线的各个端子，可参照我连接的网线**）
    >网线粗细和端子大小选择 Molex 50058-8000 (28-32 AWG) or Molex 50079-8000 (26-28 AWG) 
* **PoE 电源**（ATI Nano-17的要求，最好选择可以自适应供电的型号，以免网线接错）

### Overview
Python脚本与SOEM通过Socket通讯（端口`6319`）。当Python脚本收到从SOEM发来的 `OPGT` 时，进入可以读取传感器数值的状态。从Python脚本向SOEM发读取数据请求 `REQD` 后，SOEM将当前力/力矩数据发回Python脚本。

```mermaid
flowchart TD;
    subgraph main[程序框图]

        direction TB
        subgraph one[程序初始化]
            A[Python Script] -->|由Subprocess库启动| F[SOEM Executable]
            F --> |建立Socket连接| A
            subgraph three[SOEM 建立EtherCAT连接]
                F --> |EtherCAT连接失败| C[OPFL]
                F --> |EtherCAT连接成功| D[OPGT]
            end
        end

        subgraph two[数据沟通]
            B[Python Script] -->|REQD| G[SOEM Executable]
            G --> |力/力矩数据| B
        end

        D --> two

    end
```


## Usage

1. 网线连接、PoE供电无误后，将圆形的ATI EtherCAT OEM板连接到PC上的Intel网口，几秒后应看到板上闪绿灯，表示供电成功。如果没看到灯亮，请检查供电。
2. 在终端里使用 `ifconfig` 命令查看连接ATI EtherCAT OEM板对应的网卡地址，例如 `enp0s31f6` 。
3. 打开 `Digit-Py/calibrate_force.py`，修改 `line 23` 对应的 `sudo_password` 为你用户对应的用户密码，修改 `line 24` 对应的 `command` 内的网卡地址为你对应的网卡地址。
4. 在 `Digit-Py` 目录内启动终端，使用 `Python` 运行 `./calibrate_force.py`。


## Known Issues