#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_addNode
from pkgutil import iter_modules
from neuropype import nodes

class addNodeDlg(QDialog, ui_addNode.Ui_addNodeDialog):

    def __init__(self, parent=None):
        super(addNodeDlg, self).__init__(parent)
        self.setupUi(self)
        
        mydir = nodes.__path__
        typeNodeList = [i[1] for i in iter_modules(mydir)]
        typeNodeList.sort()
        self.nodeTypeComboBox.addItems(QStringList(typeNodeList))
    
    def values(self):
        return (self.nodeTypeComboBox.currentText(), 
                self.nodeNameLineEdit.text())
