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
        self.btn_cap.setGeometry(QtCore.QRect(40, 270, 160, 40))
        self.btn_cap.setCheckable(True)
        self.btn_cap.setObjectName("btn_cap")
        self.lb_video = QtWidgets.QLabel(self.centralwidget)
        self.lb_video.setGeometry(QtCore.QRect(0, 0, 240, 240))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lb_video.sizePolicy().hasHeightForWidth())
        self.lb_video.setSizePolicy(sizePolicy)
        self.lb_video.setText("")
        self.lb_video.setObjectName("lb_video")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "crops"))
        self.btn_cap.setText(_translate("MainWindow", "Capture"))

