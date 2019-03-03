# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class nodeNamesModel(QAbstractListModel):
    def __init__(self, data_func):
        super(nodeNamesModel, self).__init__()
        self.func = data_func
    
    def sort(self):
        return sorted(self.func(), key=str.lower)
    
    def rowCount(self, index = QModelIndex()):
        return len(self.func())
    
    def data(self, index, role =Qt.DisplayRole):
        if not index.isValid() or not (0<= index.row() < len(self.func())):
            return QVariant()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            ind = int(index.row())
            return QVariant(self.sort()[ind])
        return QVariant()
    
    # def headerData(self, section, orientation, role=Qt.DisplayRole):
    #     if role == Qt.TextAlignmentRole:
    #         if orientation == Qt.Horizontal:
    #             return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
    #         return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
    #     if orientation == Qt.Horizontal and role == Qt.DisplayRole and section ==0:
    #         return QVariant("node name")
    #     return QVariant()
    
    def changed(self):
        self.dataChanged.emit(self.index(0), self.index(0))
        
