# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/blot/share/Python/neuropype/gui/graph.ui'
#
# Created: Tue Apr 23 10:06:44 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_graphDialog(object):
    def setupUi(self, graphDialog):
        graphDialog.setObjectName(_fromUtf8("graphDialog"))
        graphDialog.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(graphDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.MPLFig = MPLQTFig(graphDialog)
        self.MPLFig.setObjectName(_fromUtf8("MPLFig"))
        self.verticalLayout.addWidget(self.MPLFig)
        self.MPLNav = MPLQTNav(graphDialog)
        self.MPLNav.setObjectName(_fromUtf8("MPLNav"))
        self.verticalLayout.addWidget(self.MPLNav)
        self.line = QtGui.QFrame(graphDialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.interactiveCheckBox = QtGui.QCheckBox(graphDialog)
        self.interactiveCheckBox.setObjectName(_fromUtf8("interactiveCheckBox"))
        self.horizontalLayout.addWidget(self.interactiveCheckBox)
        self.groupCheckBox = QtGui.QCheckBox(graphDialog)
        self.groupCheckBox.setObjectName(_fromUtf8("groupCheckBox"))
        self.horizontalLayout.addWidget(self.groupCheckBox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.refreshPushButton = QtGui.QPushButton(graphDialog)
        self.refreshPushButton.setObjectName(_fromUtf8("refreshPushButton"))
        self.horizontalLayout.addWidget(self.refreshPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(graphDialog)
        QtCore.QMetaObject.connectSlotsByName(graphDialog)

    def retranslateUi(self, graphDialog):
        graphDialog.setWindowTitle(QtGui.QApplication.translate("graphDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.interactiveCheckBox.setText(QtGui.QApplication.translate("graphDialog", "&Interactive", None, QtGui.QApplication.UnicodeUTF8))
        self.groupCheckBox.setText(QtGui.QApplication.translate("graphDialog", "&Groups", None, QtGui.QApplication.UnicodeUTF8))
        self.refreshPushButton.setText(QtGui.QApplication.translate("graphDialog", "&Refresh", None, QtGui.QApplication.UnicodeUTF8))

from neuropype.gui.MPLQTclasses import MPLQTFig, MPLQTNav
