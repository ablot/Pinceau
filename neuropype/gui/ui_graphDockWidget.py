# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/blot/share/Python/neuropype/gui/graphDockWidget.ui'
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
        DockWidget.resize(583, 320)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.widget = DotWidget(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout.addWidget(self.widget)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.refreshToolButton = QtGui.QToolButton(self.dockWidgetContents)
        self.refreshToolButton.setObjectName(_fromUtf8("refreshToolButton"))
        self.horizontalLayout.addWidget(self.refreshToolButton)
        self.line_2 = QtGui.QFrame(self.dockWidgetContents)
        self.line_2.setFrameShape(QtGui.QFrame.VLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.horizontalLayout.addWidget(self.line_2)
        self.zoomInToolButton = QtGui.QToolButton(self.dockWidgetContents)
        self.zoomInToolButton.setObjectName(_fromUtf8("zoomInToolButton"))
        self.horizontalLayout.addWidget(self.zoomInToolButton)
        self.zoomOutToolButton = QtGui.QToolButton(self.dockWidgetContents)
        self.zoomOutToolButton.setObjectName(_fromUtf8("zoomOutToolButton"))
        self.horizontalLayout.addWidget(self.zoomOutToolButton)
        self.fitToolButton = QtGui.QToolButton(self.dockWidgetContents)
        self.fitToolButton.setObjectName(_fromUtf8("fitToolButton"))
        self.horizontalLayout.addWidget(self.fitToolButton)
        self.originalSizeToolButton = QtGui.QToolButton(self.dockWidgetContents)
        self.originalSizeToolButton.setObjectName(_fromUtf8("originalSizeToolButton"))
        self.horizontalLayout.addWidget(self.originalSizeToolButton)
        spacerItem = QtGui.QSpacerItem(18, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.line = QtGui.QFrame(self.dockWidgetContents)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout.addWidget(self.line)
        self.interactiveCheckBox = QtGui.QCheckBox(self.dockWidgetContents)
        self.interactiveCheckBox.setObjectName(_fromUtf8("interactiveCheckBox"))
        self.horizontalLayout.addWidget(self.interactiveCheckBox)
        self.groupCheckBox = QtGui.QCheckBox(self.dockWidgetContents)
        self.groupCheckBox.setChecked(True)
        self.groupCheckBox.setObjectName(_fromUtf8("groupCheckBox"))
        self.horizontalLayout.addWidget(self.groupCheckBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        DockWidget.setWindowTitle(QtGui.QApplication.translate("DockWidget", "View graph", None, QtGui.QApplication.UnicodeUTF8))
        self.refreshToolButton.setText(QtGui.QApplication.translate("DockWidget", "Refresh", None, QtGui.QApplication.UnicodeUTF8))
        self.zoomInToolButton.setText(QtGui.QApplication.translate("DockWidget", "Zoom in", None, QtGui.QApplication.UnicodeUTF8))
        self.zoomOutToolButton.setText(QtGui.QApplication.translate("DockWidget", "Zoom out", None, QtGui.QApplication.UnicodeUTF8))
        self.fitToolButton.setText(QtGui.QApplication.translate("DockWidget", "Best fit", None, QtGui.QApplication.UnicodeUTF8))
        self.originalSizeToolButton.setText(QtGui.QApplication.translate("DockWidget", "100%", None, QtGui.QApplication.UnicodeUTF8))
        self.interactiveCheckBox.setToolTip(QtGui.QApplication.translate("DockWidget", "Auto refresh graph when the tree is changed", None, QtGui.QApplication.UnicodeUTF8))
        self.interactiveCheckBox.setText(QtGui.QApplication.translate("DockWidget", "Interactive", None, QtGui.QApplication.UnicodeUTF8))
        self.groupCheckBox.setToolTip(QtGui.QApplication.translate("DockWidget", "Display only input/output groups", None, QtGui.QApplication.UnicodeUTF8))
        self.groupCheckBox.setText(QtGui.QApplication.translate("DockWidget", "Groups", None, QtGui.QApplication.UnicodeUTF8))

from neuropype.gui.xdot_qt import DotWidget
