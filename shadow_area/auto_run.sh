#!/bin/bash
echo "start program..."
export LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1
export OPENNI2_REDIST=/home/pi/AXonOpenNI-Linux-Arm-2.3/Redist

cd /home/pi
boot=`cat boot_s`
if [ $boot -eq 1 ]; then
  sed -i "1c0" boot_s
  sync
  cd direct_area_py
  python3 ui_main.py -p /dev/ttyAMA0 -f -s udisk/area_pic
else
  sed -i "1c1" boot_s
  sync
  cd shadow_area_rgb
  python3 ui_main.py -p /dev/ttyAMA0 -f -s udisk/shadow_pic
fi
