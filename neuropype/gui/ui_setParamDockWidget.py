# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'share/Python/neuropype/gui/setParamDockWidget.ui'
#
# Created: Wed Oct 31 17:44:23 2012
#      by: PyQt4 UI code generator 4.9.1
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
        DockWidget.resize(424, 209)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.selectNodeLabel = QtGui.QLabel(self.dockWidgetContents)
        self.selectNodeLabel.setObjectName(_fromUtf8("selectNodeLabel"))
        self.horizontalLayout.addWidget(self.selectNodeLabel)
        self.selectNodeComboBox = QtGui.QComboBox(self.dockWidgetContents)
        self.selectNodeComboBox.setObjectName(_fromUtf8("selectNodeComboBox"))
        self.horizontalLayout.addWidget(self.selectNodeComboBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.line = QtGui.QFrame(self.dockWidgetContents)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout_2.addWidget(self.line)
        self.scrollArea = QtGui.QScrollArea(self.dockWidgetContents)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 404, 76))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.label_2 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.line_2 = QtGui.QFrame(self.scrollAreaWidgetContents)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.verticalLayout_3.addWidget(self.line_2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout_3.addLayout(self.verticalLayout)
        self.line_3 = QtGui.QFrame(self.scrollAreaWidgetContents)
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.verticalLayout_3.addWidget(self.line_3)
        spacerItem1 = QtGui.QSpacerItem(20, 4, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.line_4 = QtGui.QFrame(self.dockWidgetContents)
        self.line_4.setFrameShape(QtGui.QFrame.HLine)
        self.line_4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_4.setObjectName(_fromUtf8("line_4"))
        self.verticalLayout_2.addWidget(self.line_4)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.closePushButton = QtGui.QPushButton(self.dockWidgetContents)
        self.closePushButton.setObjectName(_fromUtf8("closePushButton"))
        self.horizontalLayout_3.addWidget(self.closePushButton)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.defaultPushButton = QtGui.QPushButton(self.dockWidgetContents)
        self.defaultPushButton.setObjectName(_fromUtf8("defaultPushButton"))
        self.horizontalLayout_3.addWidget(self.defaultPushButton)
        self.cancelPushButton = QtGui.QPushButton(self.dockWidgetContents)
        self.cancelPushButton.setObjectName(_fromUtf8("cancelPushButton"))
        self.horizontalLayout_3.addWidget(self.cancelPushButton)
        self.applyPushButton = QtGui.QPushButton(self.dockWidgetContents)
        self.applyPushButton.setObjectName(_fromUtf8("applyPushButton"))
        self.horizontalLayout_3.addWidget(self.applyPushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        DockWidget.setWidget(self.dockWidgetContents)
        self.selectNodeLabel.setBuddy(self.selectNodeComboBox)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        DockWidget.setWindowTitle(QtGui.QApplication.translate("DockWidget", "Set parameter", None, QtGui.QApplication.UnicodeUTF8))
        self.selectNodeLabel.setText(QtGui.QApplication.translate("DockWidget", "&node:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("DockWidget", "Param name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("DockWidget", "Value", None, QtGui.QApplication.UnicodeUTF8))
        self.closePushButton.setToolTip(QtGui.QApplication.translate("DockWidget", "Close set param dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.closePushButton.setText(QtGui.QApplication.translate("DockWidget", "Cl&ose", None, QtGui.QApplication.UnicodeUTF8))
        self.defaultPushButton.setToolTip(QtGui.QApplication.translate("DockWidget", "Set parameters value to default values", None, QtGui.QApplication.UnicodeUTF8))
        self.defaultPushButton.setText(QtGui.QApplication.translate("DockWidget", "&Default", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelPushButton.setToolTip(QtGui.QApplication.translate("DockWidget", "Cancel non applied changes", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelPushButton.setText(QtGui.QApplication.translate("DockWidget", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.applyPushButton.setToolTip(QtGui.QApplication.translate("DockWidget", "Apply changes", None, QtGui.QApplication.UnicodeUTF8))
        self.applyPushButton.setText(QtGui.QApplication.translate("DockWidget", "&Apply", None, QtGui.QApplication.UnicodeUTF8))

