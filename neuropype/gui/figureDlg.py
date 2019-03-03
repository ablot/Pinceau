# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_figure

class figureDlg(QDialog, ui_figure.Ui_Figure):

    def __init__(self, parent=None):
        super(figureDlg, self).__init__(parent)
        self.setupUi(self)
        self.MPLNav.initToolbar(self.MPLFig.fig.canvas)
        self.connect(self.closePushButton, SIGNAL("clicked()"),
                     self.parent().closeFigure)
        self.connect(self.hidePushButton, SIGNAL("clicked()"),
                     self.parent().hideFigure)
        self.connect(self.drawPushButton, SIGNAL("clicked()"),
                     self.draw)
    @property
    def fig(self):
        return self.MPLFig.fig
        
    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue(self.windowTitle(), QVariant(self.saveGeometry()))
        
    def draw(self):
        self.MPLFig.fig.canvas.draw()
    

    
