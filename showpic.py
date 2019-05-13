# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'showpic.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog
import cv2
from PyQt5.QtGui import QPixmap

class Ui_Dialog(QDialog):
    def __init__(self, fp):
        super(Ui_Dialog, self).__init__()
        self.fp = fp
        self.pixmap = QPixmap(self.fp)
        self.setupUi(self)

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setFixedSize(self.pixmap.width(), self.pixmap.height())
        # Dialog.resize(400, 400)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(0, 0, self.pixmap.width(), self.pixmap.height()))
        self.label.setObjectName("label")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", self.fp.split('_')[-1].split('.')[0]))
        self.label.setPixmap(self.pixmap)

