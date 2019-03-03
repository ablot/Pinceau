# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/blot/share/Python/neuropype/gui/setscaledialog.ui'
#
# Created: Wed Oct 31 16:06:10 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_SetScale(object):
    def setupUi(self, SetScale):
        SetScale.setObjectName(_fromUtf8("SetScale"))
        SetScale.resize(231, 128)
        self.verticalLayout = QtGui.QVBoxLayout(SetScale)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_3 = QtGui.QLabel(SetScale)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(SetScale)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.maxlimDoubleSpinBox = QtGui.QDoubleSpinBox(SetScale)
        self.maxlimDoubleSpinBox.setObjectName(_fromUtf8("maxlimDoubleSpinBox"))
        self.horizontalLayout.addWidget(self.maxlimDoubleSpinBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(SetScale)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.minlimDoubleSpinBox = QtGui.QDoubleSpinBox(SetScale)
        self.minlimDoubleSpinBox.setObjectName(_fromUtf8("minlimDoubleSpinBox"))
        self.horizontalLayout_2.addWidget(self.minlimDoubleSpinBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.buttonBox = QtGui.QDialogButtonBox(SetScale)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.label.setBuddy(self.maxlimDoubleSpinBox)
        self.label_2.setBuddy(self.minlimDoubleSpinBox)

        self.retranslateUi(SetScale)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SetScale.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SetScale.reject)
        QtCore.QMetaObject.connectSlotsByName(SetScale)
        SetScale.setTabOrder(self.maxlimDoubleSpinBox, self.minlimDoubleSpinBox)
        SetScale.setTabOrder(self.minlimDoubleSpinBox, self.buttonBox)

    def retranslateUi(self, SetScale):
        SetScale.setWindowTitle(QtGui.QApplication.translate("SetScale", "Set scale", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("SetScale", "Set scale for channel:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SetScale", "y m&ax lim:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("SetScale", "y m&in lim:", None, QtGui.QApplication.UnicodeUTF8))

