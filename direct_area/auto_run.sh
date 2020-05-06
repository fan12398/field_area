#!/bin/bash
echo "start program..."
export LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1
export OPENNI2_REDIST=/home/pi/tof/AXonOpenNI-Linux-Arm-2.3/Redist
cd /home/pi/direct_area
python3 ui_main.py --imu_port /dev/ttyUSB0 --loglevel warn --full_screen
#--enable_960p --save_path data