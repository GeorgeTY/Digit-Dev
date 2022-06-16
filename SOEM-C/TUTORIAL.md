# 使用SOEM读取ATI Nano-17传感器数值

## Table of Contents
1. [Introduction](#introduction)
    1. [Requirements](#requirements)
2. [Usage](#usage)
    1. [Build](#build)
    2. [Run](#run)
    3. [Socket Communication](#socket-communication)
3. [Known Issues](#known-issues)

## Introduction
本文档为使用SOEM读取 ATI Nano-17 力/力矩传感器数据的教程。

## Usage

### Requirements
* Linux x86-PC （本程序在Ubuntu 20.04上开发）
* Intel 网卡（SOEM的要求）
* 网线（**按ATI EtherCAT OEM板文档连接网线的各个端子，可参照我连接的网线**）
    >网线粗细和端子大小选择 Molex 50058-8000 (28-32 AWG) or Molex 50079-8000 (26-28 AWG) 
* **PoE 电源**（ATI Nano-17的要求，最好选择可以自适应供电的型号，以免网线接错）

### Build

Linux & macOS
   * `mkdir build`
   * `cd build`
   * `cmake ..`
   * `make`

### Run

## Known Issues
1. 无法稳定进入Operational模式，如果无法进入可能需要多运行几次程序。


