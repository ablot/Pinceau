# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_displaySweepDlg

class displaySweepDlg(QDialog, ui_displaySweepDlg.Ui_displaySweepDlg):

    def __init__(self, parent=None):
        super(displaySweepDlg, self).__init__(parent)
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.mw = parent
        self.updateNode()
        self.updateSweep()
        self.connect(self.nodeComboBox, SIGNAL("currentIndexChanged(QString)"),
                     self.updateSweep)
        self.connect(self.nodeComboBox, SIGNAL("focusInEvent()"),
                     self.updateNode)
        self.connect(self.okPushButton, SIGNAL("clicked()"), self.changeNode)
        
        
    def updateSweep(self, value = None):
        if value is None:
            value = str(self.nodeComboBox.currentText())
        if value != '':
            nodeName = str(value)
            self.sweepComboBox.clear()
            self.sweepComboBox.addItems(QStringList(self.listNodes[nodeName]))
        self.sweepComboBox.adjustSize()
        #self.changeNode()
    
    def changeNode(self):
        node = getattr(self.mw.tree, str(self.nodeComboBox.currentText()))
        grName = str(self.sweepComboBox.currentText())
        self.displaySweepWidget.setNode(node, grName)
    
    def updateNode(self):
        listNodes = list(self.mw.tree.list_nodes())
        
        self.listNodes =dict([(name, []) for name in listNodes])
        for nodeName in listNodes:
            node = getattr(self.mw.tree, nodeName)
            found = 0
            for grName, grDict in node._outputGroups.iteritems():
                if 'sweep' in grDict.keys():
                    self.listNodes[nodeName].append(grName)
                    found = 1
            if not found:
                self.listNodes.pop(nodeName)
        self.nodeComboBox.addItems(QStringList(sorted(self.listNodes.keys())))
        self.nodeComboBox.adjustSize()
        
        
