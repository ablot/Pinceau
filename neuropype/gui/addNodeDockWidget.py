#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_addNodeDockWidget
from pkgutil import iter_modules
from .. import nodes

class addNodeDockWidget(QDockWidget, ui_addNodeDockWidget.Ui_DockWidget):

    def __init__(self, parent=None):
        super(addNodeDockWidget, self).__init__(parent)
        self.setupUi(self)
        
        mydir = nodes.__path__
        typeNodeList = [i[1] for i in iter_modules(mydir)]
        typeNodeList.sort()
        self.comboBox.addItems(QStringList(typeNodeList))
        self.mw = parent
        self.connect(self.pushButton, SIGNAL("clicked()"),
                     self.clicked)
        self.setWindowTitle('Add nodes')

    
    def values(self):
        return (self.comboBox.currentText(), 
                self.lineEdit.text())
    
    def clicked(self):
        nodeType, nodeName = self.values()
        nodeName = str(nodeName)
        nodeType = str(nodeType)
        if not nodeName or nodeName[0].isdigit():
            print 'node names must begin with a non-numeric character'
            return
        nodeName = nodeName.replace(' ', '_')
        self.mw.tree.addNode(nodeName, nodeType)
        self.mw._treeChanged(self)


