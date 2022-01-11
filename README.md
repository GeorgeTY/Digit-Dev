# A simple driver for ATI Nano 17 Force/Torque Sensor based on SOEM.

BUILDING
========

Prerequisites for all platforms
-------------------------------

 * CMake 2.8.0 or later

Linux & macOS
-------------

   * `mkdir build`
   * `cd build`
   * `cmake ..`
   * `make`

USAGE
=====

   * `cd build`
   * `sudo test/linux/simple_test/simple_test [eth0]`
   
`[eth0]` is the address for NIC connected to EtherCAT OEM Board. You can get `[eth0]` by running * `ip -d a` in terminal (Ubuntu). `enp0s31f6` for example.


<!-- Known Issues
============  -->
