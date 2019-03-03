# -*- coding: utf-8 -*-
'''First try to create a class organising the nodes'''

print 'importing node'
import node
print 'importing tag'
import tag
import main

if main.use_graphviz:
    import graphviz

    
import parameter
import os
from numpy import inf
import ressources.path
import CONFIG

class Tree(object):
    '''The analysis class'''
    
    def __init__(self, name = None, path = None):
        if name is None:
            name = 'NoName'
        self._name = name
        if path is None:
            path = os.getcwd()
        if path[0] != '/':
            path += os.getcwd()
        if path[-1] != '/':
            path += '/'
        base = ''
        for direc in path[1:].split('/'):
            base += '/'+direc
            if not os.path.isdir(base):
                os.mkdir(base)
        self._home = path
        if main.use_graphviz:
            self.graph_init(self.name)
        self.interactif_graph = False
        self.tagManager = tag.tagManager()
        self.checkParams = False
        self.autoLoad = []
        self.mw = None
        self.app = None
        self._dirty = False
        
    @property
    def name(self):
        'Name of the tree'
        return self._name
    @property
    def home(self):
        'Directory where to save'
        if not isinstance(self._home, list):
            self._home = [self._home]
        return os.path.join(*self._home)
    
    def _changed(self, sender):
        self._dirty = True
        if self.mw is not None and sender is not self.mw:
            self.mw._treeChanged(self)

    def addNode(self, nodeName, nodeClass):
        if hasattr(self, nodeName):
            print 'A node named %s already exist, delete it first'%nodeName
            return
        nodeCls = get_class('neuropype.nodes.'+nodeClass+'.'+nodeClass)
        setattr(self, nodeName, nodeCls(name = nodeName, parent = self))
        self._changed(self)
    
    def rmNode(self, *args):
        for nodeName in args:
            self.Disconnect(nodeName)
            getattr(self, nodeName).dirty('all') #to empty cache
            delattr(self, nodeName)
        self._changed(self)
    
    def list_nodes(self):
        out = set()
        for name, Object in vars(self).iteritems():
            if Object.__class__.__base__.__name__ == 'Node':
                out.add(name)
        return out
    
    def Connect(self, inNodeName, inputName, outNodeName, outputName, force=0):
        inNode = getattr(self, inNodeName)
        if inNode.__class__.__base__.__name__ != 'Node':
            raise AttributeError('%s is not a node!'%inNodeName)
        outNode = getattr(self, outNodeName)
        if outNode.__class__.__base__.__name__ != 'Node':
            raise AttributeError('%s is not a node!'%outNodeName)
        
        inNode.Connect(inputName, outNodeName, outputName, force)
        self._changed(self)
    
    def Disconnect(self, inNodeName, inputName='all', outputName='all', 
                   verbose=0):
        inNode = getattr(self, inNodeName)
        if inNode.__class__.__base__ != node.Node:
            raise AttributeError('%s is not a node!'%inNodeName)
        #disconnecting inputs:
        if inputName is not None:
            if inputName == 'all':
                inputName = inNode._inputGroups.keys()
            if not isinstance(inputName, list):
                inputName = [str(inputName)]
            for name in inputName:
                inNode.disconnectInput(name)
        #disconnecting outputs:
        if outputName is not None:
            if outputName == 'all':
                outputName = inNode._outputGroups.keys()
            if not isinstance(outputName, list):
                outputName = [str(outputName)]
            for name in outputName:
                inNode.disconnectOutput(name)
        self._changed(self)
    
        
    def set_param(self, nodeName, param, value):
        node = getattr(self, nodeName)
        node.set_param(param, value)
        self._changed(self)
    
    def graph_init(self, name):
        self.graph = graphviz.GRAPH(name, self)
    
    def show_graph(self):
        if not hasattr(self,'graph'):
            self.graph_init('no_name')
        self.graph.updateGraph()
        self.graph.show()
    
    def not_connected_inputs(self, verbose = 1):
        out = []
        for name in self.list_nodes():
            node = getattr(self, name)
            inp = node.inputs
            for i in inp.iteritems():
                if i[1] is None:
                    out.append((name, i[0]))
        if verbose:
            if len(out) == 0:
                print 'All inputs of %s are connected'%self.name
            else:
                print 'Not connected inputs of %s'%self.name
                for line in out:
                    print '%s in %s'%(line[1], line[0])
        return out
    
    def save(self, name = None, force = 0):
        print 'Saving tree'
        import datetime
        if name is not None:
            if name.endswith('.py'):
                name = name[:-3]
            # name = ressources.path.toPath(name)
            path, name = os.path.split(name)
            if os.path.isfile(os.path.join(path,name)):
                print 'File %s.py already exist, use force to replace'%path+name
                return
            self._name = name
            self._home = path
        else:
            
            name = self.name
            path = self.home
            if name.endswith('.py'):
                name = name[:-3]
        
        txtfile = file(os.path.join(self.home,name+'.py'), 'w')
        txtfile.write("'''File generated by tree.py\n%s saved on %s'''\n"%(
                      self.name, str(datetime.date.today())))
        txtfile.write("\n#import:\nfrom neuropype.tree import *\nfrom neuropype import parameter")
        txtfile.write("\n#create tree:\n")
        # toWrite = ressources.path.toSaveString(path)
        # print name
        # print toWrite
        # from __main__ import PATH_DICT
        # print PATH_DICT
        # txtfile.write("from __main__ import PATH_DICT\n")
        txtfile.write("t = Tree('%s', '%s')\n"%(name, path))
        txtfile.write("t.checkParams = 0\n")
        
        txtfile.write("\n#creating nodes:\n\n")
        for nodeName in self.list_nodes():
            node = getattr(self, nodeName)
            className = node.__class__.__name__
            txtfile.write("t.addNode('%s','%s')\n"%(nodeName, className))
            if hasattr(node, '_save'):
                node._save(txtfile)
        
        txtfile.write("\n#connecting nodes and setting params:\n\n")
        #must create then connect to make sure the node you want to connect 
        #exists
        for nodeName in self.list_nodes():
            node = getattr(self, nodeName)
            for input, out in node.inputs.items():
                if out is None:
                    continue
                (outNode, output) = out
                txtfile.write("t.Connect('%s','%s','%s','%s')\n"%(nodeName, 
                               input, outNode, output))
            for key, val in node._params.iteritems():
                # if type(val) == parameter.parameter:
                #     typeName = val.Type.__name__
                #     if typeName in parameter.__dict__.keys():
                #         txtfile.write("p = parameter.%s()\n"%typeName)
                #         txtfile.write("d = %s\n"%repr(val.value.__dict__))
                #         txtfile.write("p.__dict__.update(d)\n")
                #     else:
                #        txtfile.write("p = %s\n"%repr(val.value))
                    
                #else:
                txtfile.write("p = %s\n"%repr(node.get_param(key)))
                txtfile.write("t.set_param('%s', '%s', p)\n\n"%(nodeName,key))
        txtfile.write("t.checkParams = 0\n")
        txtfile.write("print 'autoLoading ...'\n")
        for nodeName in self.autoLoad:
            txtfile.write("t.autoLoad.append('%s')\n"%nodeName)
            txtfile.write("print '            ... %s ...'\n"%nodeName)
            txtfile.write("try:\n    t.%s.load()\n"%nodeName)
            txtfile.write("except Exception:\n    print 'Error cannot load %s'\n"%nodeName)
        txtfile.write('t._dirty = False')
        txtfile.close()
        self._dirty = False
    
    def startGUI(self, newWindow = False, style = None):
        """Open the main window
        
        If newWindow, create a new window even if self.mw is already defined
        !!! The new window will replace the old one, create your own reference
        if you still want to access it !!!
        
        Set the IPython PyOS_InputHook to Qt4
        Get/create the app and start the event loop if needed
        
        TODO: See what happens if a non-Qt4 GUI was enabled
        """
        import sys
        from IPython.lib import guisupport, inputhook
        
        try:
            import PyQt4
        except ImportError:
            print "Cannot find PyQt4, GUI will not start"
            return
        print 'importing gui'
        from neuropype.gui.MainWindow import MainWindow
        
        if inputhook.current_gui() is not None:
            print "A GUI is already supported"
            if inputhook.current_gui() == 'qt4':
                print "It's qt4 so it should work"
                if self.app is None:
                    print 'Lost the app somewhere? Try to re-catch'
                    self.app = guisupport.get_app_qt4()
            else:
                print "ipython support for %s was enabled"%inputhook.current_gui()
                print "Maybe I should disable it before proceding, but we will try without"
                self.app = guisupport.get_app_qt4()
                print 'set PyOS_INputHook for Qt4'
                inputhook.enable_qt4(self.app)
        else:
            self.app = guisupport.get_app_qt4()
            print 'set PyOS_INputHook for Qt4'
            inputhook.enable_qt4(self.app)
        if CONFIG.STYLE is not None:
            from PyQt4.QtGui import QStyleFactory
            self.app.setStyle(QStyleFactory.create(CONFIG.STYLE))
        
        if not newWindow and self.mw is not None:
            if self.mw.isVisible():
                print "The main window should be visible."
                print "If you want to start another main window, use startGUI(newWindow=True)."
                return
            print "re-open main window"
            self.mw.show()
            return
        
        print 'Creating form'
        self.mw = MainWindow(tr = self)
        
        self.mw.show()
        
        if not guisupport.is_event_loop_running_qt4():
            print "Starting the event loop"
            guisupport.start_event_loop_qt4(self.app)
        print "GUI seems OK"


def get_class( kls ):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)            
    return m
