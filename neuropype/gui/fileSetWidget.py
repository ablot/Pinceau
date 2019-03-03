# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from neuropype.gui.fileSetModel import fileSetModel

class fileSetWidget(QTreeView):

    def __init__(self, parent=None):
        super(fileSetWidget, self).__init__(parent)
        self.setSelectionBehavior(QTreeView.SelectItems)
        self.setUniformRowHeights(True)
        model = fileSetModel(self)
        self.setModel(model)
        #try:
            #model.load(filename, nesting, separator)
        #except IOError, e:
            #QMessageBox.warning(self, "Server Info - Error",
                                #unicode(e))
        self.connect(self, SIGNAL("activated(QModelIndex)"),
                     self.activated)
        self.connect(self, SIGNAL("expanded(QModelIndex)"),
                     self.expanded)
        self.expanded()

    #def currentFields(self):
        #return self.model().asRecord(self.currentIndex())

    #def activated(self, index):
        #self.emit(SIGNAL("activated"), self.model().asRecord(index))


    def expanded(self):
        for column in range(self.model().columnCount(QModelIndex())):
            self.resizeColumnToContents(column)
