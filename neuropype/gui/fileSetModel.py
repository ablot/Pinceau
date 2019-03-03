# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import neuropype.nodes.FileSet as fls



class fileSetModel(QAbstractItemModel):
    
    def __init__(self, parent = None):
        super(fileSetModel,self).__init__(parent)
        self.header = ['File/Sweep/Channel', 'Tag', 'title', 'unit', 
                       'gain', 'maxval', 'sampling', 't0', 'length', 
                       'path']
        self.fileSet = None
        self.root = fls.BranchNode("")
    
    def load(self, fileSet):
        if self.fileSet == fileSet:
            return
        self.fileSet = fileSet
        self.fileSet.load_files()
    
    def columnCount(self, parent):
        return len(self.header)
    
    def rowCount(self, parent):
        node = self.nodeFromIndex(parent)
        if isinstance(node, fls.BranchNode):
            return len(node)
        if node is None or not isinstance(node.__base__, fls.BranchNode):
            return 0
        return len(node)

    def data(self, index, role):
        print index
        if role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignTop|Qt.AlignLeft))
        if role != Qt.DisplayRole:
            return QVariant()
        
        node = self.nodeFromIndex(index)
        assert node is not None
        if index.column() == 0:
            print node.name
            return QVariant(node.name)
        if not hasattr(node, col2name[index.column()]):
            QVariant(QString(""))
        out = getattr(node, col2name[index.column()])
        if hasattr(out, '__call__'):
            out = out()
        print out
        print QString(out)
        return QVariant(QString(out))

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            assert 0 <= section <= len(self.header)
            return QVariant(self.header[section])
        return QVariant()
    
    def index(self, row, column, parent):
        node = self.nodeFromIndex(parent)
        return self.createIndex(row, column, node.childAtRow(row))
    
    def parent(self, child):
        node = self.nodeFromIndex(child)
        if node is None:
            return QModelIndex()
        parent = node.parent
        if parent is None:
            return QModelIndex()
        
        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.rowOfChild(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)
    
    def nodeFromIndex(self, index):
        return index.internalPointer() if index.isValid() else self.root
