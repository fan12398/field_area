# -*- coding: utf-8 -*-
import os
import sys
import datetime
import argparse
import time
import logging
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
        self.log = log.Log(__name__, file_level=loglevel, console_level=loglevel).getlog()
        self.en_960p = en_960p
        self.savepath = savepath
        self.setupUi(self)
        self.initUI(full_screen)
        self.initDevice(imu_port, loglevel)
    
    def initUI(self, full_screen):
        if(full_screen):
            self.showFullScreen()
            self.setCursor(Qt.BlankCursor)
        welcome_img = cv2.imread('welcome.jpg')
        self.showImage(welcome_img)
        self.sb_hsv.valueChanged.connect(self.sliderbarEvent)
        self.btn_cap.clicked.connect(self.capButtonEvent)
        self.btn_area.clicked.connect(self.areaButtonEvent)
        self.setCtrlEnabled(False)
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
        
        #self.param_960p = self.rgbd.get_color_params()[0]
        #self.param_480p = self.rgbd.get_color_params()[1]
        self.rgbd.create_streams()
        #if(self.en_960p):
        #    self.rgbd.set_color_960p()
        self.rgbd.set_dcsync()
        self.rgbd.select_ImageRegistration(1)
        self.rgbd.get_depth_value_unit()
        # start preview
        self.previewTimer = QTimer(self)
        self.previewTimer.timeout.connect(self.preview)
        self.enterPreviewState()
        self.btn_cap.setEnabled(True)
    
    def setCtrlEnabled(self, val):
        self.btn_cap.setEnabled(val)
        self.btn_area.setEnabled(val)
        self.sb_hsv.setEnabled(val)
    
    def enterPreviewState(self):
        self.btn_cap.setText('Capture')
        self.btn_area.setEnabled(False)
        self.sb_hsv.setEnabled(False)
        self.showArea(-1)
        self.previewTimer.start(33)
    
    def enterCalculateState(self):
        self.previewTimer.stop()
        self.btn_cap.setText('Preview')
        self.btn_area.setEnabled(True)
        self.sb_hsv.setEnabled(True)
    
    def preview(self):
        self.depth, self.color = self.rgbd.start_one_shot(0)
        self.imu_data = self.imu.get_stream_data()[8]
        self.showImage(self.color, True)

    def showArea(self, val):
        if(val < 0):
            txt = '---------'
        else:
            txt = str(val) + ' cm^2'
        self.lb_area.setText(txt)
    
    def showImage(self, img, flip=False):
        img = cv2.resize(img, (240, 240))
        if(flip):
            img = cv2.flip(img, 1)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        toshow = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
        self.lb_video.setPixmap(QPixmap.fromImage(toshow))
    
    def showMask(self, hue):
        self.mask = algorithm.getCropMask(self.color, self.depth, hue)
        mask_red = np.zeros(self.color.shape, np.uint8)
        mask_red[:,:,2] = self.mask
        toshow = cv2.addWeighted(self.color, 0.8, mask_red, 1, 1)
        self.showImage(toshow, True)

    def sliderbarEvent(self, val):
        self.lb_hsv.setText(str(val))
        self.showMask(val)

    def capButtonEvent(self, val):
        if(val):
            self.enterCalculateState()
            self.showMask(self.sb_hsv.value())
        else:
            self.enterPreviewState()
    
    def areaButtonEvent(self):
        self.setCtrlEnabled(False)
        self.showArea(-1)
        QApplication.processEvents()
        # calculate area and show
        area = algorithm.calculateArea(self.depth, self.mask, self.imu_data)
        self.showArea(area)
        # save image <original color, original depth, area color--save to exif>
        name = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '_' + str(area) + '.jpg'
        if(self.savepath[:5] == 'udisk'):
            dirs = os.listdir('/media/pi')
            udisk_name = None
            for d in dirs:
                if(os.access('/media/pi/'+d, os.W_OK)):
                    udisk_name = d
            if(udisk_name is None):
                QMessageBox.critical(self, "保存出错", "未发现移动存储器!")
                self.setCtrlEnabled(True)
                return
            else:
                self.savepath = '/media/pi/' + udisk_name + self.savepath[5:]
        if(not os.path.exists(self.savepath)):
            try:
                os.mkdir(self.savepath)
            except:
                self.log.error("create "+self.savepath+" failed!")

        mask_red = np.zeros(self.color.shape, np.uint8)
        mask_red[:,:,2] = self.mask
        tosave = cv2.addWeighted(self.color, 0.8, mask_red, 1, 1)
        if(cv2.imwrite(self.savepath +'/'+ name, tosave)):
            #cv2.imwrite(self.savepath +'/'+ "depth.png", self.depth)
            pass
        else:
            QMessageBox.critical(self, "保存出错", "无法保存到"+self.savepath+", 请检查存储器是否安装好!")
        self.setCtrlEnabled(True)
    
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
