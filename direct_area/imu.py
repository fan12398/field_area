# -*- coding: utf-8 -*-
"""
Auther: Fan Tenglong
Time: 2019-04-08
"""
import serial
import sys
import logging
import time
import struct
import log

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication

class IMU_Sensor(QThread):
    euler_signal = pyqtSignal(list)
    error_signal = pyqtSignal()
    def __init__(self, port=None, loglevel=logging.WARN):
        super().__init__()
        self.uart = serial.Serial()
        self.uart.port = port
        self.uart.baudrate = 115200
        self.uart.timeout = 0.1
        self.euler_data = [0, 0, 0]
        self.log = log.Log(__name__, file_level=loglevel, console_level=loglevel).getlog()
    
    def setPort(self, port):
        self.uart.port = port

    def isOpen(self):
        return(self.uart.isOpen())

    def open(self, port=None):
        open_result = False
        if(port != None):
            self.uart.port = port
        try:
            self.uart.open()
        except serial.serialutil.SerialException:
            self.log.error("failed opening serial port: %s!" %(self.uart.port))
            self.error_signal.emit()
        else:
            open_result = True
            self.runflag = True
            self.start()
        return(open_result)
    
    def close(self):
        # 结束线程
        self.runflag = False
        self.wait()
        if(self.uart.isOpen()):
            self.uart.close()
    
    def send(self, buf):
        result = False
        if(self.uart.isOpen()):
            self.uart.write(buf)
            self.log.debug("serial send: " + str(buf))
            result = True
        else:
            self.log.error("serial failed send: " + str(buf) + ", port is closed.")
            self.error_signal.emit()
        return(result)
    
    def getEuler(self):
        return(self.euler_data)
    
    def decodeEuler(self, dat):
        result = []
        if(dat[:7] == b'\x3a\x01\x00\x09\x00\x2c\x00'):
            # LRC=sum(Sensor ID，指令号，数据长度，数据)
            if(int.from_bytes(dat[-4:-2], byteorder='little', signed=False) == sum(dat[1:-4])):
                #timestamp = int.from_bytes(dat[7:11], byteorder='little', signed=False)
                euler = [0,0,0]
                euler[0] = struct.unpack('f', dat[27:31])[0]
                euler[1] = struct.unpack('f', dat[31:35])[0]
                euler[2] = struct.unpack('f', dat[35:39])[0]

                euler[0] = euler[0]*180/3.1416
                euler[1] = euler[1]*180/3.1416
                euler[2] = euler[2]*180/3.1416
                result = euler
        return(result)

    def run(self):
        self.remain = b''
        while(self.runflag):
            self.remain += self.uart.readline()
            if(len(self.remain)>2 and self.remain[-2:]==b'\x0d\x0a'):
                #packet decode
                euler = self.decodeEuler(self.remain)
                if(len(euler)):
                    self.euler_data = euler
                self.remain = b''

if __name__ == "__main__":
    app = QApplication(sys.argv)
    imu = IMU_Sensor('COM3')
    imu.open()
    sys.exit(app.exec_())
