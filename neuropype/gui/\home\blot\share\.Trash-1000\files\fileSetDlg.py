# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_fileSetDlg
import nodes.FileSet as fls

col2name = {2:'title', 3:'unit', 4: 'gain', 5:'maxval', 6:'samplingInterval', 
            7:'t0', 8:'length', 9: 'path'}

class fileSetDlg(QDialog, ui_fileSetDlg.Ui_fileSetDialog):

    def __init__(self,parent=None,debug=0):
        super(fileSetDlg, self).__init__(parent)
        self.setupUi(self)
        self.mw = parent
        listNodes = list(self.mw.tree.list_nodes())
        self.listNodes = []
        for name in listNodes:
            if isinstance(getattr(self.mw.tree, name), fls.FileSet):
               self.listNodes.append(name) 
        self.listNodes.sort()
        self.selectNodeComboBox.addItems(QStringList(self.listNodes))
        if len(self.listNodes)>0:
            currentFls = getattr(self.mw.tree, self.listNodes[0])
        self.treeView.model().load(currentFls)
        
