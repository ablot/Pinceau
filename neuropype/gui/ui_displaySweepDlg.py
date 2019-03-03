# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/displaySweepDlg.ui'
#
# Created: Tue Jun  7 17:43:41 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_displaySweepDlg(object):
    def setupUi(self, displaySweepDlg):
        displaySweepDlg.setObjectName(_fromUtf8("displaySweepDlg"))
        displaySweepDlg.resize(427, 280)
        self.verticalLayout = QtGui.QVBoxLayout(displaySweepDlg)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.nodeLabel = QtGui.QLabel(displaySweepDlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nodeLabel.sizePolicy().hasHeightForWidth())
        self.nodeLabel.setSizePolicy(sizePolicy)
        self.nodeLabel.setObjectName(_fromUtf8("nodeLabel"))
        self.horizontalLayout.addWidget(self.nodeLabel)
        self.nodeComboBox = QtGui.QComboBox(displaySweepDlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nodeComboBox.sizePolicy().hasHeightForWidth())
        self.nodeComboBox.setSizePolicy(sizePolicy)
        self.nodeComboBox.setObjectName(_fromUtf8("nodeComboBox"))
        self.horizontalLayout.addWidget(self.nodeComboBox)
        self.sweepLabel = QtGui.QLabel(displaySweepDlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sweepLabel.sizePolicy().hasHeightForWidth())
        self.sweepLabel.setSizePolicy(sizePolicy)
        self.sweepLabel.setObjectName(_fromUtf8("sweepLabel"))
        self.horizontalLayout.addWidget(self.sweepLabel)
        self.sweepComboBox = QtGui.QComboBox(displaySweepDlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sweepComboBox.sizePolicy().hasHeightForWidth())
        self.sweepComboBox.setSizePolicy(sizePolicy)
        self.sweepComboBox.setObjectName(_fromUtf8("sweepComboBox"))
        self.horizontalLayout.addWidget(self.sweepComboBox)
        self.okPushButton = QtGui.QPushButton(displaySweepDlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.okPushButton.sizePolicy().hasHeightForWidth())
        self.okPushButton.setSizePolicy(sizePolicy)
        self.okPushButton.setObjectName(_fromUtf8("okPushButton"))
        self.horizontalLayout.addWidget(self.okPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.displaySweepWidget = displaySweep(displaySweepDlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self.displaySweepWidget.sizePolicy().hasHeightForWidth())
        self.displaySweepWidget.setSizePolicy(sizePolicy)
        self.displaySweepWidget.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.displaySweepWidget.setObjectName(_fromUtf8("displaySweepWidget"))
        self.verticalLayout.addWidget(self.displaySweepWidget)
        self.nodeLabel.setBuddy(self.nodeComboBox)
        self.sweepLabel.setBuddy(self.sweepComboBox)

        self.retranslateUi(displaySweepDlg)
        QtCore.QMetaObject.connectSlotsByName(displaySweepDlg)

    def retranslateUi(self, displaySweepDlg):
        displaySweepDlg.setWindowTitle(QtGui.QApplication.translate("displaySweepDlg", "Display Sweep", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeLabel.setText(QtGui.QApplication.translate("displaySweepDlg", "No&de", None, QtGui.QApplication.UnicodeUTF8))
        self.sweepLabel.setText(QtGui.QApplication.translate("displaySweepDlg", "Sw&eep", None, QtGui.QApplication.UnicodeUTF8))
        self.okPushButton.setText(QtGui.QApplication.translate("displaySweepDlg", "&Ok", None, QtGui.QApplication.UnicodeUTF8))

from displaySweepWidget import displaySweep
