# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime
import logging
import argparse
import numpy as np
from cv2 import cv2
import serial
# pyqt
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from mainwindow import Ui_MainWindow

import log
from rgbd import RGBD_Camera
from lpmslib import LpmsME
import algorithm

class appUI(QMainWindow, Ui_MainWindow):
    def __init__(self, imu_port=None, loglevel=logging.WARN, savepath='data', full_screen=False, en_960p=False):
        super().__init__()
        self.en_960p = en_960p
        self.savepath = savepath
        self.log = log.Log(__name__, file_level=loglevel, console_level=loglevel).getlog()
        self.setupUi(self)
        self.initUI(full_screen)
        self.initDevice(imu_port, loglevel)
    
    def initUI(self, full_screen):
        if(full_screen):
            self.showFullScreen()
            self.setCursor(Qt.BlankCursor)
        welcome_img = cv2.imread('welcome.jpg')
        self.showImage(welcome_img)
        self.btn_cap.clicked.connect(self.capButtonEvent)
        self.btn_cap.setEnabled(False)
        self.show()
        QApplication.processEvents()
    
    def initDevice(self, imu_port, loglevel):
        self.rgbd = RGBD_Camera(loglevel)
        try:
            self.rgbd.open()
        except Exception as e:
            self.log.error("RGBD相机打开失败: %r" %e)
            return
        
        ser = serial.Serial(imu_port, 115200)
        ser.write('hello\r\n'.encode())
        ser.close()
        self.imu = LpmsME.LpmsME(imu_port, 115200)
        if(not self.imu.connect()):
            self.log.error("imu sensor连接失败!")
            return
        
        self.param_960p = self.rgbd.get_color_params()[0]
        self.param_480p = self.rgbd.get_color_params()[1]
        self.rgbd.create_streams()
        if(self.en_960p):
            self.rgbd.set_color_960p()
        self.rgbd.set_dcsync()
        self.rgbd.select_ImageRegistration(1)
        self.rgbd.get_depth_value_unit()
        # start preview
        self.previewTimer = QTimer(self)
        self.previewTimer.timeout.connect(self.preview)
        self.enterPreviewState()
        self.btn_cap.setEnabled(True)
    
    def enterPreviewState(self):
        self.btn_cap.setText('Capture')
        self.previewTimer.start(33)
    
    def enterCaptureState(self):
        self.previewTimer.stop()
        self.btn_cap.setText('Preview')
        # save image <original color, original depth, area color--save to exif>
        if(self.area > 0):
            name = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '_' + str(self.area) + '.jpg'
            if(self.savepath[:5] == 'udisk'):
                dirs = os.listdir('/media/pi')
                if(len(dirs) == 0):
                    QMessageBox.critical(self, "保存出错", "未发现移动存储器!")
                    return
                else:
                    self.savepath = '/media/pi/' + dirs[-1] + self.savepath[5:]
            if(not os.path.exists(self.savepath)):
                try:
                    os.mkdir(self.savepath)
                except:
                    self.log.error("create "+self.savepath+" failed!")
            if(cv2.imwrite(self.savepath +'/'+ name, self.color)):
                #cv2.imwrite(self.savepath +'/'+ "depth.png", self.depth)
                pass
            else:
                QMessageBox.critical(self, "保存出错", "无法保存到"+self.savepath+", 请检查存储器是否安装好!")
        else:
            QMessageBox.warning(self, "照片未保存", "目标区域超出测量范围!")
    
    def preview(self):
        self.depth, self.color = self.rgbd.start_one_shot()
        imu_data = self.imu.get_stream_data()[8]
        if(self.en_960p):
            self.area = algorithm.getRectArea_960p(self.depth, self.color, self.param_960p, imu_data)
        else:
            self.area = algorithm.getRectArea_480p(self.depth, self.color, self.param_480p, imu_data)
        self.showImage(self.color, self.area, True)
    
    def showImage(self, img, area=0, flip=False):
        img = cv2.resize(img, (240, 240))
        if(flip):
            img = cv2.flip(img, 1)
        if(area > 0):
            txt = str(area) + ' cm^2'
            img = cv2.putText(img, txt, (10, 30), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        toshow = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
        self.lb_video.setPixmap(QPixmap.fromImage(toshow))

    def capButtonEvent(self, val):
        if(val):
            self.enterCaptureState()
        else:
            self.enterPreviewState()
    
    #关闭窗口
    def closeEvent(self, event):
        reply = QMessageBox.question(self, "消息","确定退出?", QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
        if(reply == QMessageBox.Yes):
            try:
                self.previewTimer.stop()
                self.rgbd.close()
                self.imu.disconnect()
            except:
                pass
            event.accept()
        else:
            event.ignore()
        
def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--imu_port', type=str, required=True, help="imu serial port eg: COM3, /dev/ttyUSB0")
    parser.add_argument('-f','--full_screen', action='store_true', default=False, help="indicate whether window full screen")
    parser.add_argument('-e','--enable_960p', action='store_true', default=False, help="indicate whether enable 960p mode")
    parser.add_argument('-l','--loglevel', type=str, default='warn', help='log level, eg: debug, info, warn, error, critical, fatal')
    parser.add_argument('-s','--save_path', type=str, default='data', help='log level, eg: picture save path')
    args = parser.parse_args(argv)
    if(args.loglevel.lower() == 'debug'):
        args.loglevel = logging.DEBUG
    elif(args.loglevel.lower() == 'info'):
        args.loglevel = logging.INFO
    elif(args.loglevel.lower() == 'warn'):
        args.loglevel = logging.WARN
    elif(args.loglevel.lower() == 'error'):
        args.loglevel = logging.ERROR
    elif(args.loglevel.lower() == 'critical'):
        args.loglevel = logging.CRITICAL
    elif(args.loglevel.lower() == 'fatal'):
        args.loglevel = logging.FATAL
    else:
        args.loglevel = logging.WARN
    return(args)
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    args = parse_arguments(sys.argv[1:])
    ui = appUI(args.imu_port, args.loglevel, args.save_path, args.full_screen, args.enable_960p)
    sys.exit(app.exec_())
