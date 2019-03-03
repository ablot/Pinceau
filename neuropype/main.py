# -*- coding: utf-8 -*-

#from PyQt4.QtCore import *

import os
try:
    import graphviz
    use_graphviz = True
except ImportError:
    print 'pygraphviz is not installed, will try to do without, but some options will be disabled'
    use_graphviz = False

import tree, imp, CONFIG

def new(name, path = None):
    return tree.Tree(str(name), path)

def load(filename):
    fname = str(filename)
    name = fname.split('/')[-1]
    try:
        mod = imp.load_source(name,fname)    
    except IOError:
        print "Cannot find file %s, maybe you forgot the extension"%fname
        return
    return mod.t

def startGUI():
    """Start an empty GUI
    
    Create mw and app, the main window and the qt4 app"""
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
            noApp = False
            try:
                if app is None:
                    noApp = True
            except UnboundLocalError:
                noApp = True
            if noApp:
                print 'Lost the app somewhere? Try to re-catch'
                app = guisupport.get_app_qt4()
        else:
            print "ipython support for %s was enabled"%inputhook.current_gui()
            print "Maybe I should disable it before proceding, but we will try without"
            app = guisupport.get_app_qt4()
            print 'set PyOS_INputHook for Qt4'
            inputhook.enable_qt4(app)
    else:
        app = guisupport.get_app_qt4()
        print 'set PyOS_INputHook for Qt4'
        inputhook.enable_qt4(app)
    if CONFIG.STYLE is not None:
        from PyQt4.QtGui import QStyleFactory
        app.setStyle(QStyleFactory.create(CONFIG.STYLE))
    
    print 'Creating form'
    mw = MainWindow(tr = None)
    mw.show()
    
    if not guisupport.is_event_loop_running_qt4():
        print "Starting the event loop"
        guisupport.start_event_loop_qt4(app)
    print "GUI seems OK"
    get_ipython().push(('mw', 'app'))
    return mw

msg = """\nWelcome to Neuropype

Use new to create a new tree, load to open an existing tree
Take care 'tree' is the name of the module, don't erase it

To start the GUI with the tree t use t.startGUI()
"""

#t = None
#def set_current_tree():
    #global t
    #t = mw.tree
    #That doesn't work. I'll have to do with mw.tree for now.
__version__ = "0.0.1"

if __name__ == "__main__":
    print 'Running neuropype ...'
    import sys
    import numpy as np
    
    try:
        import IPython
    except ImportError:
        sys.exit("Cannot find IPython, make sure it is installed and try again") 
    
    mainDir, _ = os.path.split(__file__)

    if float(IPython.__version__[:4]) > 0.10:
        local_ns = {'tree' : tree, 'new':new, 'load':load, 'startGUI':startGUI}
        try:
            get_ipython
            print "already in ipython, do you want to use current session?"
            resp = raw_input('y/N: ')
            while resp.lower() not in ['', 'y', 'n']:
                resp = raw_input('y for yes, n for no: ')
            if resp.lower() == 'y':
                newShell = False
            else:
                newShell = True
        except NameError:
            newShell = True
        if newShell:
            cfg = IPython.config.loader.Config()
            cfg.PromptManager.in_template = 'Neuropype In <\\#>:  '
            cfg.PromptManager.in2_template = '   .\\D.: '
            cfg.PromptManager.out_template = 'Neuropype Out<\\#>: '
            from IPython.frontend.terminal.embed import InteractiveShellEmbed
            ipshell = InteractiveShellEmbed(config=cfg,
                       banner1 = 'Dropping into IPython\n'+msg,
                       exit_msg = 'Leaving Interpreter, good bye!')
            ipshell()
        else:
            if mainDir not in sys.path:
                sys.path.append(str(mainDir))
                print "Adding %s in path"%mainDir
            print msg

    else:
        sys.exit("need IPython version >0.11") 

