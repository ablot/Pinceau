#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_connectNodes

class connectNodesDlg(QDialog, ui_connectNodes.Ui_connectDialog):

    def __init__(self, parent=None):
        super(connectNodesDlg, self).__init__(parent)
        self.setupUi(self)
        self.mw = parent
        self.updateComboBox()
        self.connect(self.showGroupsCheckBox, SIGNAL("stateChanged(int)"),
                     self.updateComboBox)
        self.connect(self.inNodeComboBox, SIGNAL("activated(QString)"),
                     self.updateInputComboBox)
        self.connect(self.outNodeComboBox, SIGNAL("activated(QString)"),
                     self.updateOutputComboBox)
        self.connect(self.connectPushButton, SIGNAL("clicked()"),
                     self.connectNodes)
        self.connect(self.closePushButton, SIGNAL("clicked()"), self.close)
        self.connect(self.inputComboBox, SIGNAL("activated(QString)"),
                     self.updateLabel)
        
    
    def connectNodes(self):
        p = {}
        p['inNodeName'] = str(self.inNodeComboBox.currentText())
        p['outNodeName'] = str(self.outNodeComboBox.currentText())
        p['inputName'] = str(self.inputComboBox.currentText())
        p['outputName'] = str(self.outputComboBox.currentText())
        p['force'] = bool(self.forceCheckBox.isChecked())
        self.parent().tree.Connect(p['inNodeName'], p['inputName'],
                                   p['outNodeName'],p['outputName'], 
                                   force = p['force'])
        self.parent()._treeChanged()
        self.updateLabel(p['inputName'])
    
    def updateComboBox(self, index = 0):
        self.inNodeComboBox.clear()
        self.outNodeComboBox.clear()
        listNodes = list(self.mw.tree.list_nodes())
        listNodes.sort()
        self.inNodeComboBox.addItems(QStringList(listNodes))
        self.outNodeComboBox.addItems(QStringList(listNodes))
        
        #setting connector comboBox
        self.updateInputComboBox(self.inNodeComboBox.currentText())
        self.updateOutputComboBox(self.outNodeComboBox.currentText())
    
    def updateInputComboBox(self, text):
        node = getattr(self.parent().tree, str(text))
        groups = self.showGroupsCheckBox.isChecked()
        if groups:
            inputs = node._inputGroups.keys()
        else:
            inputs = node.inputs.keys()
        inputs.sort()
        self.inputComboBox.clear()
        self.inputComboBox.addItems(QStringList(inputs))
        self.updateLabel(str(self.inputComboBox.currentText()), node)
    
    def updateOutputComboBox(self, text):
        node = getattr(self.parent().tree, str(text))
        groups = self.showGroupsCheckBox.isChecked()
        if groups:
            outputs = node._outputGroups.keys()
        else:
            outputs = node.outputs.keys()
        outputs.sort()
        self.outputComboBox.clear()
        self.outputComboBox.addItems(QStringList(outputs))
                
    def updateLabel(self, inputName, node = None):
        inputName = str(inputName)
        if node is None:
            node = getattr(self.parent().tree, 
                           str(self.inNodeComboBox.currentText()))
        if self.showGroupsCheckBox.isChecked():
            insource = node._inGrConnection
        else:
            insource = node.inputs
            if not insource.has_key(inputName):
                raise ValueError('Unknown input %s'%inputName)
        connected = insource[inputName] if insource.has_key(inputName) else None
        if connected is None:
            self.connectedToLabel.setText('Not connected')
        else:
            self.connectedToLabel.setText('Connected to %s of %s'%(connected[1],
                                                                 connected[0]))

