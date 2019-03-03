# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_graphDlg
import matplotlib.image as mpimg


class graphDlg(QDialog, ui_graphDlg.Ui_graphDialog):

    def __init__(self,parent=None,debug=0):
        super(graphDlg, self).__init__(parent)
        self.setupUi(self)
        self.MPLNav.initToolbar(self.MPLFig.fig.canvas)
        self.graph = parent.tree.graph
        self.updateGraph(1)
        self.setWindowTitle('Graph of tree %s'%parent.tree.name)
        self.connect(self.groupCheckBox, SIGNAL("stateChanged(int)"),
                self.updateGraph)
    
    def updateGraph(self, doIt = 0):
        if self.sender is self.groupCheckBox:
            doIt = 1
        if not doIt and not self.interactiveCheckBox.isChecked():
            return
        
        self.graph.updateGraph(groups = self.groupCheckBox.isChecked(), 
                               verbose = 0)
        img=mpimg.imread(self.graph.path)
        ax = self.MPLFig.fig.add_axes([0,0,1,1])
        imgplot = ax.imshow(img, aspect = 'equal')
        ax.axis('off')
        self.MPLFig.fig.canvas.draw()
    
    @pyqtSignature("")
    def on_refreshPushButton_clicked(self):
        self.updateGraph(1)