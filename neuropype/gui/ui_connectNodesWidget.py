# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/blot/share/Python/neuropype/gui/connectNodesWidget.ui'
#
# Created: Mon Nov  5 17:22:31 2012
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
        DockWidget.resize(254, 285)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.inNodeLabel = QtGui.QLabel(self.dockWidgetContents)
        self.inNodeLabel.setObjectName(_fromUtf8("inNodeLabel"))
        self.horizontalLayout.addWidget(self.inNodeLabel)
        self.inNodeComboBox = QtGui.QComboBox(self.dockWidgetContents)
        self.inNodeComboBox.setObjectName(_fromUtf8("inNodeComboBox"))
        self.horizontalLayout.addWidget(self.inNodeComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.inputLabel = QtGui.QLabel(self.dockWidgetContents)
        self.inputLabel.setObjectName(_fromUtf8("inputLabel"))
        self.horizontalLayout_2.addWidget(self.inputLabel)
        self.inputComboBox = QtGui.QComboBox(self.dockWidgetContents)
        self.inputComboBox.setObjectName(_fromUtf8("inputComboBox"))
        self.horizontalLayout_2.addWidget(self.inputComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.connectedToLabel = QtGui.QLabel(self.dockWidgetContents)
        self.connectedToLabel.setObjectName(_fromUtf8("connectedToLabel"))
        self.horizontalLayout_3.addWidget(self.connectedToLabel)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.line = QtGui.QFrame(self.dockWidgetContents)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.outNodeLabel = QtGui.QLabel(self.dockWidgetContents)
        self.outNodeLabel.setObjectName(_fromUtf8("outNodeLabel"))
        self.horizontalLayout_4.addWidget(self.outNodeLabel)
        self.outNodeComboBox = QtGui.QComboBox(self.dockWidgetContents)
        self.outNodeComboBox.setObjectName(_fromUtf8("outNodeComboBox"))
        self.horizontalLayout_4.addWidget(self.outNodeComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.outputLabel = QtGui.QLabel(self.dockWidgetContents)
        self.outputLabel.setObjectName(_fromUtf8("outputLabel"))
        self.horizontalLayout_5.addWidget(self.outputLabel)
        self.outputComboBox = QtGui.QComboBox(self.dockWidgetContents)
        self.outputComboBox.setObjectName(_fromUtf8("outputComboBox"))
        self.horizontalLayout_5.addWidget(self.outputComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.showGroupsCheckBox = QtGui.QCheckBox(self.dockWidgetContents)
        self.showGroupsCheckBox.setChecked(True)
        self.showGroupsCheckBox.setObjectName(_fromUtf8("showGroupsCheckBox"))
        self.horizontalLayout_6.addWidget(self.showGroupsCheckBox)
        self.forceCheckBox = QtGui.QCheckBox(self.dockWidgetContents)
        self.forceCheckBox.setChecked(False)
        self.forceCheckBox.setObjectName(_fromUtf8("forceCheckBox"))
        self.horizontalLayout_6.addWidget(self.forceCheckBox)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem3)
        self.closePushButton = QtGui.QPushButton(self.dockWidgetContents)
        self.closePushButton.setObjectName(_fromUtf8("closePushButton"))
        self.horizontalLayout_7.addWidget(self.closePushButton)
        self.connectPushButton = QtGui.QPushButton(self.dockWidgetContents)
        self.connectPushButton.setObjectName(_fromUtf8("connectPushButton"))
        self.horizontalLayout_7.addWidget(self.connectPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_7)
        DockWidget.setWidget(self.dockWidgetContents)
        self.inNodeLabel.setBuddy(self.inNodeComboBox)
        self.inputLabel.setBuddy(self.inputComboBox)
        self.outNodeLabel.setBuddy(self.outNodeComboBox)
        self.outputLabel.setBuddy(self.outputComboBox)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        DockWidget.setWindowTitle(QtGui.QApplication.translate("DockWidget", "DockWidget", None, QtGui.QApplication.UnicodeUTF8))
        self.inNodeLabel.setText(QtGui.QApplication.translate("DockWidget", "Data consumer", None, QtGui.QApplication.UnicodeUTF8))
        self.inputLabel.setText(QtGui.QApplication.translate("DockWidget", "input to connect", None, QtGui.QApplication.UnicodeUTF8))
        self.connectedToLabel.setText(QtGui.QApplication.translate("DockWidget", "Not connected", None, QtGui.QApplication.UnicodeUTF8))
        self.outNodeLabel.setText(QtGui.QApplication.translate("DockWidget", "Data producer", None, QtGui.QApplication.UnicodeUTF8))
        self.outputLabel.setText(QtGui.QApplication.translate("DockWidget", "output to connect", None, QtGui.QApplication.UnicodeUTF8))
        self.showGroupsCheckBox.setText(QtGui.QApplication.translate("DockWidget", "Show groups", None, QtGui.QApplication.UnicodeUTF8))
        self.forceCheckBox.setToolTip(QtGui.QApplication.translate("DockWidget", "if checked, when two groups are different, \n"
"try to connect common values", None, QtGui.QApplication.UnicodeUTF8))
        self.forceCheckBox.setText(QtGui.QApplication.translate("DockWidget", "force", None, QtGui.QApplication.UnicodeUTF8))
        self.closePushButton.setText(QtGui.QApplication.translate("DockWidget", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.connectPushButton.setText(QtGui.QApplication.translate("DockWidget", "Connect", None, QtGui.QApplication.UnicodeUTF8))
