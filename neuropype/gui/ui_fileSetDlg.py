# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'share/Python/neuropype/gui/fileSetDlg.ui'
#
# Created: Fri Jan  7 17:41:25 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_fileSetDialog(object):
    def setupUi(self, fileSetDialog):
        fileSetDialog.setObjectName("fileSetDialog")
        fileSetDialog.resize(703, 597)
        self.verticalLayout = QtGui.QVBoxLayout(fileSetDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.selectNodeLabel = QtGui.QLabel(fileSetDialog)
        self.selectNodeLabel.setObjectName("selectNodeLabel")
        self.horizontalLayout.addWidget(self.selectNodeLabel)
        self.selectNodeComboBox = QtGui.QComboBox(fileSetDialog)
        self.selectNodeComboBox.setObjectName("selectNodeComboBox")
        self.horizontalLayout.addWidget(self.selectNodeComboBox)
        self.selectNodePushButton = QtGui.QPushButton(fileSetDialog)
        self.selectNodePushButton.setObjectName("selectNodePushButton")
        self.horizontalLayout.addWidget(self.selectNodePushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.line = QtGui.QFrame(fileSetDialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.treeView = fileSetWidget(fileSetDialog)
        self.treeView.setObjectName("treeView")
        self.verticalLayout.addWidget(self.treeView)

        self.retranslateUi(fileSetDialog)
        QtCore.QMetaObject.connectSlotsByName(fileSetDialog)

    def retranslateUi(self, fileSetDialog):
        fileSetDialog.setWindowTitle(QtGui.QApplication.translate("fileSetDialog", "fileSet", None, QtGui.QApplication.UnicodeUTF8))
        self.selectNodeLabel.setText(QtGui.QApplication.translate("fileSetDialog", "&node:", None, QtGui.QApplication.UnicodeUTF8))
        self.selectNodePushButton.setText(QtGui.QApplication.translate("fileSetDialog", "&Ok", None, QtGui.QApplication.UnicodeUTF8))

from gui.fileSetWidget import fileSetWidget
