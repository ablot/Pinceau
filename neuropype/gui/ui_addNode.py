# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'addNode.ui'
#
# Created: Sun Dec 12 23:15:07 2010
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_addNodeDialog(object):
    def setupUi(self, addNodeDialog):
        addNodeDialog.setObjectName("addNodeDialog")
        addNodeDialog.resize(285, 111)
        self.gridLayout = QtGui.QGridLayout(addNodeDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.nodeType = QtGui.QLabel(addNodeDialog)
        self.nodeType.setObjectName("nodeType")
        self.gridLayout.addWidget(self.nodeType, 0, 0, 1, 1)
        self.nodeTypeComboBox = QtGui.QComboBox(addNodeDialog)
        self.nodeTypeComboBox.setObjectName("nodeTypeComboBox")
        self.gridLayout.addWidget(self.nodeTypeComboBox, 0, 1, 1, 1)
        self.nodeName = QtGui.QLabel(addNodeDialog)
        self.nodeName.setObjectName("nodeName")
        self.gridLayout.addWidget(self.nodeName, 1, 0, 1, 1)
        self.nodeNameLineEdit = QtGui.QLineEdit(addNodeDialog)
        self.nodeNameLineEdit.setObjectName("nodeNameLineEdit")
        self.gridLayout.addWidget(self.nodeNameLineEdit, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(addNodeDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 2)
        self.nodeType.setBuddy(self.nodeTypeComboBox)
        self.nodeName.setBuddy(self.nodeNameLineEdit)

        self.retranslateUi(addNodeDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), addNodeDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), addNodeDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(addNodeDialog)

    def retranslateUi(self, addNodeDialog):
        addNodeDialog.setWindowTitle(QtGui.QApplication.translate("addNodeDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeType.setToolTip(QtGui.QApplication.translate("addNodeDialog", "Select the type of the node that you want to add", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeType.setText(QtGui.QApplication.translate("addNodeDialog", "Node &type", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeTypeComboBox.setToolTip(QtGui.QApplication.translate("addNodeDialog", "Select the type of the node that you want to add", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeName.setToolTip(QtGui.QApplication.translate("addNodeDialog", "Write the name of the node. Node names must begin by a non-numeric character and cannot contain space.", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeName.setText(QtGui.QApplication.translate("addNodeDialog", "&Node name:", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeNameLineEdit.setToolTip(QtGui.QApplication.translate("addNodeDialog", "Write the name of the node. Node names must begin by a non-numeric character and cannot contain space.", None, QtGui.QApplication.UnicodeUTF8))

