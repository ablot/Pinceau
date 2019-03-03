# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/blot/share/Python/neuropype/gui/figureDockWidget.ui'
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

class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName(_fromUtf8("DockWidget"))
        DockWidget.resize(446, 401)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.MPLFig = MPLQTFig(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.MPLFig.sizePolicy().hasHeightForWidth())
        self.MPLFig.setSizePolicy(sizePolicy)
        self.MPLFig.setObjectName(_fromUtf8("MPLFig"))
        self.verticalLayout.addWidget(self.MPLFig)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.MPLNav = MPLQTNav(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MPLNav.sizePolicy().hasHeightForWidth())
        self.MPLNav.setSizePolicy(sizePolicy)
        self.MPLNav.setObjectName(_fromUtf8("MPLNav"))
        self.horizontalLayout.addWidget(self.MPLNav)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.drawPushButton = QtGui.QPushButton(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.drawPushButton.sizePolicy().hasHeightForWidth())
        self.drawPushButton.setSizePolicy(sizePolicy)
        self.drawPushButton.setMaximumSize(QtCore.QSize(50, 16777215))
        self.drawPushButton.setObjectName(_fromUtf8("drawPushButton"))
        self.horizontalLayout.addWidget(self.drawPushButton)
        self.hidePushButton = QtGui.QPushButton(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hidePushButton.sizePolicy().hasHeightForWidth())
        self.hidePushButton.setSizePolicy(sizePolicy)
        self.hidePushButton.setMaximumSize(QtCore.QSize(50, 16777215))
        self.hidePushButton.setObjectName(_fromUtf8("hidePushButton"))
        self.horizontalLayout.addWidget(self.hidePushButton)
        self.closePushButton = QtGui.QPushButton(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.closePushButton.sizePolicy().hasHeightForWidth())
        self.closePushButton.setSizePolicy(sizePolicy)
        self.closePushButton.setMaximumSize(QtCore.QSize(50, 16777215))
        self.closePushButton.setObjectName(_fromUtf8("closePushButton"))
        self.horizontalLayout.addWidget(self.closePushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        DockWidget.setWindowTitle(QtGui.QApplication.translate("DockWidget", "DockWidget", None, QtGui.QApplication.UnicodeUTF8))
        self.drawPushButton.setText(QtGui.QApplication.translate("DockWidget", "Draw", None, QtGui.QApplication.UnicodeUTF8))
        self.hidePushButton.setText(QtGui.QApplication.translate("DockWidget", "Hide", None, QtGui.QApplication.UnicodeUTF8))
        self.closePushButton.setText(QtGui.QApplication.translate("DockWidget", "Close", None, QtGui.QApplication.UnicodeUTF8))

from neuropype.gui.MPLQTclasses import MPLQTFig, MPLQTNav
