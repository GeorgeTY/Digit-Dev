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
   * `sudo test/linux/simple_test/simple_test [ifname1]`
   
`[ifname1]` is the address for NIC connected to EtherCAT OEM Board. You can get `[ifname1]` by running `ip -d a` in terminal (Ubuntu). `enp0s31f6` or `eth0` for example.
Press ENTER for next measurement.

<!-- Known Issues
============  -->
