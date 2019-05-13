# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QFileDialog
import PyQt5
from showpic import Ui_Dialog

from FFT import fft_and_ifft
import cv2
import os

def fft_and_ifft_path(path):
    img_name = os.path.basename(path)
    img_dir = os.path.dirname(path)
    name_list = img_name.split('.')
    fft_img, ifft_img = fft_and_ifft(path)
    fft_path = os.path.join(img_dir,name_list[0]+'_fft.'+name_list[1])
    ifft_path = os.path.join(img_dir,name_list[0]+'_ifft.'+name_list[1])
    cv2.imwrite(fft_path,fft_img)
    cv2.imwrite(ifft_path,ifft_img)
    return [fft_path,ifft_path]


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.setupUi(self)
        self.dialog = []

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(359, 400)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setFixedSize(339, 280)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setMaximumSize(QtCore.QSize(16777215, 30))
        self.textBrowser.setObjectName("textBrowser")
        self.horizontalLayout_4.addWidget(self.textBrowser)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.clicked.connect(self.select_file)
        self.pushButton.setMaximumSize(QtCore.QSize(16777215, 30))
        self.pushButton.setIconSize(QtCore.QSize(16, 30))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_4.addWidget(self.pushButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout_3.addWidget(self.pushButton_2)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 359, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "快速傅里叶变换"))
        self.pushButton.setText(_translate("MainWindow", "选择文件"))
        self.pushButton_2.setText(_translate("MainWindow", "开始变换"))


    @pyqtSlot()
    def select_file(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "image (*.png *.jpeg *.jpg)", options=options)
        if fileName:
            self.fileName = fileName
            self.textBrowser.setText(fileName)
            pixmap = QPixmap(fileName)
            self.label.setPixmap(pixmap.scaled(self.label.width(), self.label.height(), PyQt5.QtCore.Qt.KeepAspectRatio))

            self.thread = Picshow(fileName)
            self.thread.sinOut.connect(self.handle_pic)
            self.thread.finish.connect(self.pushButton_2.setEnabled)
            self.pushButton_2.clicked.connect(self.click)

    @pyqtSlot()
    def click(self):
        self.pushButton_2.setEnabled(False)
        self.thread.start()


    def handle_pic(self, fp):
        self.dialog.append(Ui_Dialog(fp))
        self.dialog[-1].show()


class Picshow(QThread):
    sinOut = pyqtSignal(str)
    finish = pyqtSignal(bool)

    def __init__(self, fp):
        super(Picshow, self).__init__()
        self.fp = fp

    def run(self):
        #res = histest(self.fp)
        res = fft_and_ifft_path(self.fp)
        for i in res:
            self.sinOut.emit(i)
        self.finish.emit(True)
