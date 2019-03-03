# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_graphDockWidget
from xdot_qt import *
import matplotlib.image as mpimg


class graphDockWidget(QDockWidget, ui_graphDockWidget.Ui_DockWidget):

    def __init__(self,parent=None,debug=0):
        super(graphDockWidget, self).__init__(parent)
        self.setupUi(self)
        self.refreshToolButton.setIcon(QIcon.fromTheme('view-refresh'))
        self.zoomInToolButton.setIcon(QIcon.fromTheme('zoom-in'))
        self.zoomOutToolButton.setIcon(QIcon.fromTheme('zoom-out'))
        self.fitToolButton.setIcon(QIcon.fromTheme('zoom-fit-best'))
        self.originalSizeToolButton.setIcon(QIcon.fromTheme('zoom-original'))

        self.updateGraph()
        self.connect(self.groupCheckBox, SIGNAL("stateChanged(int)"),
                self.updateGraph)
        self.connect(self.refreshToolButton, SIGNAL("clicked()"),
                self.updateGraph)
        self.connect(self.zoomInToolButton, SIGNAL("clicked()"),
                self.widget.on_zoom_in)
        self.connect(self.zoomOutToolButton, SIGNAL("clicked()"),
                self.widget.on_zoom_out)
        self.connect(self.fitToolButton, SIGNAL("clicked()"),
                self.widget.on_zoom_fit)
        self.connect(self.originalSizeToolButton, SIGNAL("clicked()"),
                self.widget.on_zoom_100)

    @property
    def tree(self):
        """tree associated with the widget (find it through parent)"""
        return self.parent().tree
    
    def treeChanged(self):
        if self.interactiveCheckBox.isChecked():
            self.updateGraph()
    
    def updateGraph(self):
        self.tree.graph.updateGraph(groups = self.groupCheckBox.isChecked(), 
                                verbose = 0)
        fname = self.tree.graph.path
        fp = file(fname, 'rt')
        self.widget.set_dotcode(fp.read(), fname)
        fp.close()
        self.widget.reload()

