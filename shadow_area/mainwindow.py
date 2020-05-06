# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(240, 320)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.btn_cap = QtWidgets.QPushButton(self.centralwidget)
        self.btn_cap.setGeometry(QtCore.QRect(0, 290, 70, 30))
        self.btn_cap.setCheckable(True)
        self.btn_cap.setObjectName("btn_cap")
        self.lb_area = QtWidgets.QLabel(self.centralwidget)
        self.lb_area.setGeometry(QtCore.QRect(140, 290, 100, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lb_area.setFont(font)
        self.lb_area.setFrameShape(QtWidgets.QFrame.Box)
        self.lb_area.setFrameShadow(QtWidgets.QFrame.Raised)
        self.lb_area.setAlignment(QtCore.Qt.AlignCenter)
        self.lb_area.setObjectName("lb_area")
        self.lb_video = QtWidgets.QLabel(self.centralwidget)
        self.lb_video.setGeometry(QtCore.QRect(0, 0, 240, 240))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lb_video.sizePolicy().hasHeightForWidth())
        self.lb_video.setSizePolicy(sizePolicy)
        self.lb_video.setText("")
        self.lb_video.setObjectName("lb_video")
        self.sb_hsv = QtWidgets.QSlider(self.centralwidget)
        self.sb_hsv.setGeometry(QtCore.QRect(30, 250, 200, 30))
        self.sb_hsv.setMinimum(20)
        self.sb_hsv.setMaximum(160)
        self.sb_hsv.setSingleStep(1)
        self.sb_hsv.setProperty("value", 40)
        self.sb_hsv.setOrientation(QtCore.Qt.Horizontal)
        self.sb_hsv.setInvertedAppearance(False)
        self.sb_hsv.setInvertedControls(False)
        self.sb_hsv.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.sb_hsv.setTickInterval(10)
        self.sb_hsv.setObjectName("sb_hsv")
        self.lb_hsv = QtWidgets.QLabel(self.centralwidget)
        self.lb_hsv.setGeometry(QtCore.QRect(0, 250, 30, 30))
        self.lb_hsv.setAlignment(QtCore.Qt.AlignCenter)
        self.lb_hsv.setObjectName("lb_hsv")
        self.btn_area = QtWidgets.QPushButton(self.centralwidget)
        self.btn_area.setGeometry(QtCore.QRect(90, 290, 50, 30))
        self.btn_area.setCheckable(True)
        self.btn_area.setObjectName("btn_area")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "crops"))
        self.btn_cap.setText(_translate("MainWindow", "Capture"))
        self.lb_area.setText(_translate("MainWindow", "0 cm^2"))
        self.lb_hsv.setText(_translate("MainWindow", "40"))
        self.btn_area.setText(_translate("MainWindow", "Area"))

