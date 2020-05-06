from lpmslib import LpmsME
import time

imu = LpmsME.LpmsME('/dev/ttyAMA0', 115200)
if(not imu.connect()):
    print("imu sensor连接失败!")
    exit(0)

cnt = 0
while(True):
    imu_data = imu.get_stream_data()[8]
    print(imu_data)
    time.sleep(0.1)
    cnt += 1
    if(cnt > 1000):
        break

imu.disconnect()
