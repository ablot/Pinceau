# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'share/Python/neuropype/gui/graph.ui'
#
# Created: Thu Jan 13 11:02:51 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_graphDialog(object):
    def setupUi(self, graphDialog):
        graphDialog.setObjectName("graphDialog")
        graphDialog.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(graphDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.MPLFig = MPLQTFig(graphDialog)
        self.MPLFig.setObjectName("MPLFig")
        self.verticalLayout.addWidget(self.MPLFig)
        self.MPLNav = MPLQTNav(graphDialog)
        self.MPLNav.setObjectName("MPLNav")
        self.verticalLayout.addWidget(self.MPLNav)
        self.line = QtGui.QFrame(graphDialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.interactiveCheckBox = QtGui.QCheckBox(graphDialog)
        self.interactiveCheckBox.setObjectName("interactiveCheckBox")
        self.horizontalLayout.addWidget(self.interactiveCheckBox)
        self.groupCheckBox = QtGui.QCheckBox(graphDialog)
        self.groupCheckBox.setObjectName("groupCheckBox")
        self.horizontalLayout.addWidget(self.groupCheckBox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.refreshPushButton = QtGui.QPushButton(graphDialog)
        self.refreshPushButton.setObjectName("refreshPushButton")
        self.horizontalLayout.addWidget(self.refreshPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(graphDialog)
        QtCore.QMetaObject.connectSlotsByName(graphDialog)

    def retranslateUi(self, graphDialog):
        graphDialog.setWindowTitle(QtGui.QApplication.translate("graphDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.interactiveCheckBox.setText(QtGui.QApplication.translate("graphDialog", "&Interacrive", None, QtGui.QApplication.UnicodeUTF8))
        self.groupCheckBox.setText(QtGui.QApplication.translate("graphDialog", "&Groups", None, QtGui.QApplication.UnicodeUTF8))
        self.refreshPushButton.setText(QtGui.QApplication.translate("graphDialog", "&Refresh", None, QtGui.QApplication.UnicodeUTF8))

from gui.MPLQTclasses import MPLQTFig, MPLQTNav
