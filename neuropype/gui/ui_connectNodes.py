# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/connectNodes.ui'
#
# Created: Mon Jun 27 17:02:53 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_connectDialog(object):
    def setupUi(self, connectDialog):
        connectDialog.setObjectName(_fromUtf8("connectDialog"))
        connectDialog.resize(354, 249)
        self.verticalLayout = QtGui.QVBoxLayout(connectDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.inNodeLabel = QtGui.QLabel(connectDialog)
        self.inNodeLabel.setObjectName(_fromUtf8("inNodeLabel"))
        self.horizontalLayout_2.addWidget(self.inNodeLabel)
        self.inNodeComboBox = QtGui.QComboBox(connectDialog)
        self.inNodeComboBox.setObjectName(_fromUtf8("inNodeComboBox"))
        self.horizontalLayout_2.addWidget(self.inNodeComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.inputLabel = QtGui.QLabel(connectDialog)
        self.inputLabel.setObjectName(_fromUtf8("inputLabel"))
        self.horizontalLayout_3.addWidget(self.inputLabel)
        self.inputComboBox = QtGui.QComboBox(connectDialog)
        self.inputComboBox.setObjectName(_fromUtf8("inputComboBox"))
        self.horizontalLayout_3.addWidget(self.inputComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem)
        self.connectedToLabel = QtGui.QLabel(connectDialog)
        self.connectedToLabel.setObjectName(_fromUtf8("connectedToLabel"))
        self.horizontalLayout_7.addWidget(self.connectedToLabel)
        self.verticalLayout.addLayout(self.horizontalLayout_7)
        self.line = QtGui.QFrame(connectDialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.outNodeLabel = QtGui.QLabel(connectDialog)
        self.outNodeLabel.setObjectName(_fromUtf8("outNodeLabel"))
        self.horizontalLayout_5.addWidget(self.outNodeLabel)
        self.outNodeComboBox = QtGui.QComboBox(connectDialog)
        self.outNodeComboBox.setObjectName(_fromUtf8("outNodeComboBox"))
        self.horizontalLayout_5.addWidget(self.outNodeComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.outputLabel = QtGui.QLabel(connectDialog)
        self.outputLabel.setObjectName(_fromUtf8("outputLabel"))
        self.horizontalLayout_4.addWidget(self.outputLabel)
        self.outputComboBox = QtGui.QComboBox(connectDialog)
        self.outputComboBox.setObjectName(_fromUtf8("outputComboBox"))
        self.horizontalLayout_4.addWidget(self.outputComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.showGroupsCheckBox = QtGui.QCheckBox(connectDialog)
        self.showGroupsCheckBox.setChecked(True)
        self.showGroupsCheckBox.setObjectName(_fromUtf8("showGroupsCheckBox"))
        self.horizontalLayout.addWidget(self.showGroupsCheckBox)
        self.forceCheckBox = QtGui.QCheckBox(connectDialog)
        self.forceCheckBox.setChecked(False)
        self.forceCheckBox.setObjectName(_fromUtf8("forceCheckBox"))
        self.horizontalLayout.addWidget(self.forceCheckBox)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem2)
        self.closePushButton = QtGui.QPushButton(connectDialog)
        self.closePushButton.setObjectName(_fromUtf8("closePushButton"))
        self.horizontalLayout_6.addWidget(self.closePushButton)
        self.connectPushButton = QtGui.QPushButton(connectDialog)
        self.connectPushButton.setObjectName(_fromUtf8("connectPushButton"))
        self.horizontalLayout_6.addWidget(self.connectPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.inNodeLabel.setBuddy(self.inNodeComboBox)
        self.inputLabel.setBuddy(self.inputComboBox)
        self.outNodeLabel.setBuddy(self.outNodeComboBox)
        self.outputLabel.setBuddy(self.outputComboBox)

        self.retranslateUi(connectDialog)
        QtCore.QMetaObject.connectSlotsByName(connectDialog)

    def retranslateUi(self, connectDialog):
        connectDialog.setWindowTitle(QtGui.QApplication.translate("connectDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.inNodeLabel.setText(QtGui.QApplication.translate("connectDialog", "Data &consumer", None, QtGui.QApplication.UnicodeUTF8))
        self.inputLabel.setText(QtGui.QApplication.translate("connectDialog", "&input to connect", None, QtGui.QApplication.UnicodeUTF8))
        self.connectedToLabel.setText(QtGui.QApplication.translate("connectDialog", "Not connected", None, QtGui.QApplication.UnicodeUTF8))
        self.outNodeLabel.setText(QtGui.QApplication.translate("connectDialog", "Data &producer", None, QtGui.QApplication.UnicodeUTF8))
        self.outputLabel.setText(QtGui.QApplication.translate("connectDialog", "&output to connect", None, QtGui.QApplication.UnicodeUTF8))
        self.showGroupsCheckBox.setText(QtGui.QApplication.translate("connectDialog", "&Show groups", None, QtGui.QApplication.UnicodeUTF8))
        self.forceCheckBox.setToolTip(QtGui.QApplication.translate("connectDialog", "if checked, when two groups are different, \n"
"try to connect common values", None, QtGui.QApplication.UnicodeUTF8))
        self.forceCheckBox.setText(QtGui.QApplication.translate("connectDialog", "&force", None, QtGui.QApplication.UnicodeUTF8))
        self.closePushButton.setText(QtGui.QApplication.translate("connectDialog", "Cl&ose", None, QtGui.QApplication.UnicodeUTF8))
        self.connectPushButton.setText(QtGui.QApplication.translate("connectDialog", "Co&nnect", None, QtGui.QApplication.UnicodeUTF8))

