# -*- coding: utf-8 -*-

import matplotlib.figure
import matplotlib.backends.backend_qt4agg
import PyQt4.QtCore
import PyQt4.QtGui
#import pdb

#################################################################################
class MPLQTFig(matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg):
#################################################################################
    def __init__(self, parent=None):
        #pdb.set_trace()
        self.fig = matplotlib.figure.Figure()
        matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg.__init__(self, self.fig)
        #self.setParent(parent)
        #sizePolicy = PyQt4.QtGui.QSizePolicy(PyQt4.QtGui.QSizePolicy.Expanding, PyQt4.QtGui.QSizePolicy.Expanding)
        #sizePolicy.setHorizontalStretch(1)
        #sizePolicy.setVerticalStretch(1)
        #self.setSizePolicy(sizePolicy)
        
        
#################################################################################
class MPLQTNav(PyQt4.QtGui.QWidget):
#################################################################################
    def __init__(self, parent=None):
        PyQt4.QtGui.QWidget.__init__(self, parent)
    
    # Inheriting directly from the toolbar, which is itself a widget, would preclude use of designer because it assumes a default constructor taking just the parent as an optional parameter, whereas the toolbar constructor requires the canvas as well.
    def initToolbar(self, canvas):
        self.toolbar = matplotlib.backends.backend_qt4agg.NavigationToolbar2QTAgg(canvas, self)
        self.box = PyQt4.QtGui.QHBoxLayout()
        self.box.addWidget(self.toolbar)
        self.setLayout(self.box)