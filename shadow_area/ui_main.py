# -*- coding: utf-8 -*-

import sys
import time
import logging
import numpy as np
from cv2 import cv2
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
    def __init__(self, imu_port=None, loglevel=logging.WARN):
        super().__init__()
        self.log = log.Log(__name__, file_level=loglevel, console_level=loglevel).getlog()
        self.setupUi(self)
        self.initUI()
        self.initDevice(imu_port, loglevel)
    
    def initUI(self):
        if(sys.platform != 'win32'):
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
        self.imu = LpmsME.LpmsME(imu_port, 115200)
        try:
            self.rgbd.open()
        except Exception as e:
            self.log.error("RGBD相机打开失败: %r" %e)
            return
        if(not self.imu.connect()):
            self.log.error("imu sensor连接失败!")
            return
        self.rgbd.create_streams()
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    if(sys.platform == 'win32'):
        imu_port = 'COM3'
    else:
        imu_port = '/dev/ttyAMA0'
    ui = appUI(imu_port, logging.INFO)
    sys.exit(app.exec_())
