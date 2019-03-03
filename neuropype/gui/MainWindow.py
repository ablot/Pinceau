# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
print 'importing tree'
from .. import tree
print 'importing dialogs'
import addNodeDockWidget, connectNodesWidget, displaySweepDockWidget, setParamDockWidget
import figureDockWidget, graphDockWidget
import models
import imp

#import fileSetDlg

class MainWindow(QMainWindow):

    def __init__(self, tr = None, parent=None,debug=0):
        super(MainWindow, self).__init__(parent)
        
        #defining properties
        self._tree = tr
        if tr is not None:
            self.filename = os.path.join(tr.home, tr.name)
        else:
            self.filename = None
        self.setDockNestingEnabled(True)
        #defining actions
        #fileMenu
        actionNewTree = self.createAction("&New...", self.newTree,
                QKeySequence.New, None, "Create a new tree")
        actionLoadTree = self.createAction("&Load...", self.loadTree,
                QKeySequence.Open, None, "Load existing tree")
        actionSaveTree = self.createAction("&Save...", self.saveTree,
                QKeySequence.Save, None, "Save current tree")
        actionSaveTreeAs = self.createAction("Save &as...", self.saveTreeAs,
                QKeySequence.SaveAs, None, "Save current tree in a new file")
        actionClose = self.createAction("&Close", self.close,
                QKeySequence.Close, None, "Close the window")

        #treeMenu
        actionAddNode = self.createAction("&Add node", self.addNode, 'alt+a',
                        None, 'Add a node to current tree')
        actionConnect = self.createAction("&Connect", self.connectNodes, 
                        'alt+C', None, "Connect two nodes")

        #viewMenu
        actionShowGraph = self.createAction("Show &graph", self.showGraph, 
                        'alt+G', None, "Show the graphviz image of the tree")
        actionDisplaySweep = self.createAction("Display &sweep",
                                               self.displaySweep, 'alt+S',
                                               None, "Display sweeps from one node of the graph")
        actionSetParam = self.createAction("Set &param", self.setParam, 
                                           'alt+P', None, "Set parameters from one node of the graph")
        actionFileSetDlg = self.createAction("&File Set", self.fileSet, 
                        'alt+I', None, "FileSet")
        
        #figureMenu
        actionNewFigure = self.createAction("New fi&gure", self.newFigure, 
                                            'ctrl+alt+n', None, 
                                            "Create a new empty figure")
        actionCloseAllFigure = self.createAction("&Close all", self.closeFigure, 
                                            'ctrl+alt+c', None, 
                                            "Close all figures")
        actionHideAllFigure = self.createAction("&Hide all", self.hideFigure, 
                                            'ctrl+alt+h', None, 
                                            "Hide all figures")
        actionRaiseAllFigure = self.createAction("&Raise all", self.raiseFigure, 
                                            'ctrl+alt+r', None, 
                                            "Raise all figures")
        self.figureMenuActions = [actionNewFigure, actionCloseAllFigure,
                                  actionHideAllFigure, actionRaiseAllFigure]
        
        #Menu bar
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(actionNewTree)
        self.fileMenu.addAction(actionLoadTree)
        self.fileMenu.addAction(actionSaveTree)
        self.fileMenu.addAction(actionSaveTreeAs)
        self.fileMenu.addAction(actionClose)
        
        self.treeMenu = self.menuBar().addMenu("&Tree")
        self.treeMenu.addAction(actionAddNode)
        self.treeMenu.addAction(actionConnect)
        
        self.viewMenu = self.menuBar().addMenu("&View")
        self.viewMenu.addAction(actionShowGraph)
        self.viewMenu.addAction(actionDisplaySweep)
        self.viewMenu.addAction(actionSetParam)
        self.viewMenu.addAction(actionFileSetDlg)
        
        self.figureMenu = self.menuBar().addMenu('F&igure')
        self.updateFigureMenu()
        self.connect(self.figureMenu, SIGNAL("aboutToShow()"),
                     self.updateFigureMenu)
        self.setWinName()
        if tr is not None:
            self.nodeNameModel = models.nodeNamesModel(tr.list_nodes)
        else:
            self.nodeNameModel = None

    @property
    def tree(self):
        'Analysis tree'
        return self._tree

    def setWinName(self, winName = None):
        if winName is None:
            if self.tree is not None:
                winName = "Neuropype: "+self.tree.name
            else:
                winName = "Neuropype (no tree)"
        self.setWindowTitle(winName)        
        
    def newTree(self):
        print "NewTree"
        if not self.okToContinue():
            return
        directory = os.path.dirname(self.filename) if self.filename is not None\
                    else "."
        self._msgBox = QFileDialog(self)
        self._msgBox.setDirectory(directory)
        self._msgBox.setFileMode(QFileDialog.AnyFile)
        self._msgBox.setViewMode(QFileDialog.Detail)
        self._msgBox.setModal(True)
        self._msgBox.setNameFilters(["Python files (*.py)","All (*)"])
        
        if self._msgBox.exec_():
            fname = str(self._msgBox.selectedFiles()[0])
            name = fname.split('/')[-1]
            path = fname[:fname.rfind('/')+1]
            tr = tree.Tree(name, path)
            self.setTree(tr)
            print 'Tree %s created'%name
            # get_ipython().push(dict(t = self.tree))
        del self._msgBox

    def setTree(self, tr):
        tr.mw = self
        self.filename = os.path.join(tr.home, tr.name)
        self.setWinName()
        if self.nodeNameModel is not None:
            self.nodeNameModel.func = tr.list_nodes
        else:
            self.nodeNameModel = models.nodeNamesModel(tr.list_nodes)
        self._tree = tr
        self._treeChanged(self)

    def loadTree(self):
        print "LoadTree"
        if not self.okToContinue():
            return
        directory = os.path.dirname(self.filename) if self.filename is not None\
                    else "."
        self._msgBox = QFileDialog(self)
        self._msgBox.setDirectory(directory)
        self._msgBox.setFileMode(QFileDialog.ExistingFile)
        self._msgBox.setViewMode(QFileDialog.Detail)
        self._msgBox.setModal(True)
        self._msgBox.setNameFilters(["Python files (*.py)","All (*)"])
        if self._msgBox.exec_():
            fname = str(self._msgBox.selectedFiles()[0])
            name = fname.split('/')[-1]
            path = fname[:fname.rfind('/')+1]
            mod = imp.load_source("bidonName",fname)
            self.setTree(mod.t)
            get_ipython().push(dict(t = self.tree))
            print 'tree loaded'
            self.setWinName()
        del self._msgBox
    
    def saveTree(self):
        self.tree.save()
    
    def saveTreeAs(self):
        fname = str(QFileDialog.getSaveFileName(self, "Neuropype - Save as ...", 
                                            self.filename))
        if fname:
            self.tree.save(fname, force =1)
        
        
    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action
    
    def okToContinue(self):
        if self.tree is not None and self.tree._dirty:
            self._msgBox = QMessageBox(self)
            self._msgBox.setText("The document has been modified.");
            self._msgBox.setInformativeText("Do you want to save your changes?");
            self._msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel);
            self._msgBox.setDefaultButton(QMessageBox.Save);
            reply = self._msgBox.exec_();
            # reply = QMessageBox.question(self,
            #                 "Tree %s - Unsaved Changes"%self.tree.name,
            #                 "Save unsaved changes?",
            #                 QMessageBox.Yes|QMessageBox.No|
            #                 QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Yes:
                self.tree.save()
        return True
    
    def findFigure(self):
        fig = {}
        for n, v in self.__dict__.iteritems():
            if type(v) == figureDockWidget.figureDockWidget:
                fig[n]=v
        return fig
    
    def updateFigureMenu(self):
        self.figureMenu.clear()
        for action in self.figureMenuActions:
            self.figureMenu.addAction(action)
        figs = self.findFigure()
        
        if figs:
            self.figureMenu.addSeparator()
            for i, (fname, f) in enumerate(sorted(figs.iteritems())):
                action = self.createAction("&%d %s"%(i+1, fname.replace('_',' '))
                                           , tip = 'Raise %s'%fname)
                action.setData(QVariant(fname))
                self.connect(action, SIGNAL("triggered()"), self.raiseFigure)
                self.figureMenu.addAction(action)
    
    def _findFname(self, fname, sender, func):
        if fname is None:
            if isinstance(sender, QAction):
                if sender.data() != QVariant():
                    fname = str(sender.data().toString())
                else:
                    for n in self.findFigure().keys():
                        func(n)
            elif isinstance(sender, QPushButton):
                # parent is dockWidgetContents
                dockWidg = sender.parent().parent()
                fname = str(dockWidg.windowTitle()).replace(' ','_')
            else:
                for n in self.findFigure().keys():
                        func(n)
        return fname
    
    def closeFigure(self, fname = None):
        fname = self._findFname(fname, self.sender(), self.closeFigure)
        if fname:
            if not hasattr(self, fname):
                print "Unknown figure: %s"%fname
                return
            figDlg = getattr(self, fname)
            figDlg.deleteLater()
            delattr(self, fname)
            del fname
    
    def raiseFigure(self, fname = None):
        fname = self._findFname(fname, self.sender(), self.raiseFigure)
        if fname:
            if not hasattr(self, fname):
                print "Unknown figure: %s"%fname
                return
            settings = QSettings()
            figDlg = getattr(self, fname)
            geom = settings.value(figDlg.windowTitle())
            if geom != QVariant():
                figDlg.restoreGeometry(geom.toByteArray())
            figDlg.show()
            figDlg.raise_()
        
    def hideFigure(self, fname = None):
        fname = self._findFname(fname, self.sender(), self.hideFigure)
        if fname:
            if not hasattr(self, fname):
                print "Unknown figure: %s"%fname
                return
            figDlg = getattr(self, fname)
            figDlg.close()
        
    def _treeChanged(self, sender):
        if sender is not self.tree and self.tree is not None:
            self.tree._changed(self)
        if hasattr(self, "graphDockWidget") and self.graphDockWidget:
            self.graphDockWidget.treeChanged()
        self.nodeNameModel.changed()
    
    def addNode(self):
        if type(self.tree) != tree.Tree:
            print 'you must create a tree first !'
            return
        if not hasattr(self, 'addNodeDockWidget'):
            self.addNodeDockWidget = addNodeDockWidget.addNodeDockWidget(self)
            self.addDockWidget(Qt.LeftDockWidgetArea, self.addNodeDockWidget)
        self.addNodeDockWidget.show()
        self.addNodeDockWidget.raise_()

    
    def fileSet(self):
        pass
        # if type(self.tree) != tree.Tree:
        #     print 'you must create a tree first !'
        #     return
        # self.fileSetDlg = fileSetDlg.fileSetDlg(self)
        # self.fileSetDlg.show()
        
    def setParam(self):
        if type(self.tree) != tree.Tree:
            print 'you must create a tree first !'
            return
        if not hasattr(self, 'setParamDockWidget'):
            self.setParamDockWidget = setParamDockWidget.setParamDockWidget(self)
            self.addDockWidget(Qt.LeftDockWidgetArea, self.setParamDockWidget)
        self.setParamDockWidget.show()
        self.setParamDockWidget.raise_()
    
    def newFigure(self):
        n = 0
        while hasattr(self, 'Figure_%s'%n):
            n+=1
        fig = figureDockWidget.figureDockWidget(self)
        fig.setWindowTitle("Figure %s"%n)
        setattr(self, 'Figure_%s'%n, fig)
        get_ipython().push({'Figure_%s'%n: fig.fig})
        self.addDockWidget(Qt.TopDockWidgetArea, fig)
        self.raiseFigure("Figure_%s"%n)
        return fig.fig
        
        
    def showGraph(self):
        if type(self.tree) != tree.Tree:
            print 'you must create a tree first !'
            return       
        if not hasattr(self, 'graphDockWidget'):
            self.graphDockWidget = graphDockWidget.graphDockWidget(self)
            self.addDockWidget(Qt.RightDockWidgetArea, self.graphDockWidget)
        self.graphDockWidget.show()
        self.graphDockWidget.raise_()
        # if self.graphDlg is None:
        #     self.graphDlg = graphDlg.graphDlg(self)
        # self.graphDlg.show()
        # self.graphDlg.raise_()
        # self.graphDlg.activateWindow()
            
    def displaySweep(self):
        if type(self.tree) != tree.Tree:
            print 'you must create a tree first !'
            return       
        if not hasattr(self, 'displaySweepDockWidget'):
            self.displaySweepDockWidget = displaySweepDockWidget.displaySweepDockWidget(self)
            self.addDockWidget(Qt.TopDockWidgetArea, self.displaySweepDockWidget)
        self.displaySweepDockWidget.show()
        self.displaySweepDockWidget.raise_()
        self.displaySweepDockWidget.activateWindow()
    
    def connectNodes(self):
        if type(self.tree) != tree.Tree:
            print 'you must create a tree first !'
            return
        if not hasattr(self, 'connectDockWidget'):
            self.connectDockWidget = connectNodesWidget.connectNodesWidget(self)
            self.addDockWidget(Qt.LeftDockWidgetArea, self.connectDockWidget)
        self.connectDockWidget.show()
        self.connectDockWidget.raise_()
        self.connectDockWidget.activateWindow()
            
    def closeEvent(self, event):
        if self.okToContinue():
            print 'Window closed, enter exit() to quit program'
            print 'Main window can be re-opened by calling mw.show()'
        else:
            event.ignore()
    
