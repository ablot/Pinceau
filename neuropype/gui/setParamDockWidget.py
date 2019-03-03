# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_setParamDockWidget
import neuropype.parameter as p
import os
import sys

class setParamDockWidget(QDockWidget, ui_setParamDockWidget.Ui_DockWidget):
    """ Dialog use to change parameters of nodes
    
    Each parameter type is showed given its displayType and modified given its
    setType. So for each subclass of parameter.parameter, three functions must
    be defined, 
    one that return a list of widget that will be displayed, 
    one that is called when changed are applied and returns the value of the 
        parameter
    one that changed the value of the parameter in the display, and calls
    """
    def __init__(self, parent = None):
        super(setParamDockWidget, self).__init__(parent)
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.mw = parent
        self.selectNodeComboBox.setModel(parent.nodeNameModel)
        self.changed = []
        self.node = None
        self.displayTypes = {p.integer: self._integerFunc,
                             p.path2file: self._path2fileFunc,
                             p.boolean: self._booleanFunc,
                             p.combobox: self._comboboxFunc,
                             p.float_param: self._floatFunc}
        self.getTypes = {p.integer: self._getInteger, 
                         p.path2file: self._getPath2file,
                         p.boolean: self._getBoolean,
                         p.combobox: self._getCombobox,
                         p.float_param: self._getFloat}
        self.setTypes = {p.integer: self._setInteger, 
                         p.path2file: self._setPath2file,
                         p.boolean: self._setBoolean,
                         p.combobox: self._setCombobox,
                         p.float_param: self._setFloat}
        self.connect(self.selectNodeComboBox, SIGNAL("activated(int)"),
                     self.nodeChanged)
        self.nodeChanged()
    
    # def updateSelectNodeComboBox(self):
    #     self.selectNodeComboBox.clear()
    #     listNodes = list(self.mw.tree.list_nodes())
    #     listNodes.sort()
    #     self.listNodes = listNodes
    #     self.selectNodeComboBox.addItems(QStringList(listNodes))
        
    def nodeChanged(self):
        currentNodeName = str(self.selectNodeComboBox.currentText())
        currentNode = getattr(self.mw.tree, currentNodeName)
        if self.node == currentNode:
            return
        else:
            self.node = currentNode
            self.changed = []
            self.reDoScrollArea()
        
    def cleanScrollArea(self):
        if hasattr(self,'listLayout'):
        #just to avoid the deletion before the initialisation
            for paramName, listWidget in self.listWidget.iteritems():
                for widget in listWidget:
                    widget.deleteLater()
                self.listLayout[paramName].deleteLater()
    
    def reDoScrollArea(self):
        self.cleanScrollArea()
        self.listLayout = {}
        self.listWidget = {}
        listParam = sorted(self.node.params)
        for paramName in listParam:
            self.listWidget[paramName] = []
            label = QLabel()
            label.setText(paramName)
            label.setObjectName(paramName+"Label")
            label.setMaximumWidth(150)
            label.setMinimumWidth(50)
            self.listWidget[paramName].append(label)
            try:
                error = False
                widgetList = self.doLine(paramName)
            except Exception as e:
                error = True
                widgetList = self._errorLine(paramName, e)
            self.listWidget[paramName] += widgetList
            
            
            self.listLayout[paramName] = QHBoxLayout()
            for widget in self.listWidget[paramName]:
                self.listLayout[paramName].addWidget(widget)
            self.verticalLayout.addLayout(self.listLayout[paramName])
            if not error:
                self.updateValue(paramName)
    
    def updateValue(self, paramName, value =None):
        """Update the value of paramName. If value is None use value
        stored in the node
        """
        parameter = self.node._params[paramName]
        if value is None:
            value = self.node.get_param(paramName)
        if not self.setTypes.has_key(type(parameter)):
            self._setUnknownType(paramName, value)
        else:
            self.setTypes[type(parameter)](paramName, value)
        return
        

    def doLine(self, paramName):
            parameter = self.node._params[paramName]
            if not self.displayTypes.has_key(type(parameter)):
                widgetList = self._unknownType(paramName)
            else:
                widgetList = self.displayTypes[type(parameter)](paramName)
            return widgetList
            
            
    def valChanged(self, *args, **kwargs):
        if kwargs.has_key('paramName'):
            paramName = kwargs['paramName']
        else:
            paramName = '_'.join(str(self.sender().objectName()).split('_')[:-1])
        if paramName not in self.changed:
            self.changed.append(paramName)
            #TODO: change the icon on the toolButton
        pass
    
    def Apply(self):
        for paramName in self.changed:
            parameter = self.node._params[paramName]
            if  type(parameter) not in self.displayTypes.keys():
                value = self._getUnknownType(paramName)
            else:
                value = self.getTypes[type(parameter)](paramName)
            self.node.set_param(paramName, value)
        self.changed = []
        self.reDoScrollArea()
    
    def Cancel(self):
        self.changed = []
        self.reDoScrollArea()
    
    def Default(self):
        default = self.node.default_param(reset = False)
        
        self.reDoScrollArea()
        
    #######################################################################
    ####### Type specific functions (in displayTypes and setTypes) ########
    #######################################################################
    def _errorLine(self, paramName, error):
        label = QLabel()
        label.setObjectName(paramName+"_label")
        label.setText('Error with parameter %s (see tooltip for more info)'%paramName)
        msg = 'There was an error. It is often a non-connected input preventing'
        msg+= ' the widget to be properly initialized.\n The error was: \n"%s"'%error
        label.setToolTip(msg)
        toolButton = QToolButton()
        toolButton.setObjectName(paramName+"toolButton")
        #self._setUnknownType(paramName, value)
        return [label, toolButton]
    
    def _unknownType(self, paramName):
        parameter = self.node._params[paramName]
        value = self.node.get_param(paramName)
        lineEdit = QLineEdit()
        lineEdit.setObjectName(paramName+"_lineEdit")
        self.connect(lineEdit, SIGNAL("editingFinished()"), self.valChanged)
        toolButton = QToolButton()
        toolButton.setObjectName(paramName+"toolButton")
        #self._setUnknownType(paramName, value)
        return [lineEdit, toolButton]
    
    def _getUnknownType(self, paramName):
        lineEdit = self.listWidget[paramName][1]
        return str(lineEdit.text())

    def _setUnknownType(self, paramName, value):
        lineEdit = self.listWidget[paramName][1]
        lineEdit.setText(str(value))
    

    ## Integer
    def _integerFunc(self, paramName):
        parameter = self.node._params[paramName]
        spinBox = QSpinBox()
        spinBox.setObjectName(paramName+"_spinBox")
        self.connect(spinBox, SIGNAL("valueChanged(int)"), self.valChanged)
        
        maxVal = parameter.maxVal()
        if maxVal is None: maxVal = sys.maxint
        
        minVal = parameter.minVal()
        if minVal is None: minVal = -sys.maxint-1
        
        spinBox.setRange(minVal,maxVal)
        toolButton = QToolButton()
        toolButton.setObjectName(paramName+"toolButton")
        #self._setInteger(paramName, value)
        return [spinBox, toolButton]
    
    def _setInteger(self, paramName, value):
        spinBox = self.listWidget[paramName][1]
        spinBox.setValue(int(value))
    
    def _getInteger(self, paramName):
        spinBox = self.listWidget[paramName][1]
        return int(spinBox.value())
    
    ## Boolean
    def _booleanFunc(self, paramName):
        """private function.
        
        used in DoLine to create the widgets
        Arguments:
        - `paramName`: key of the parameter in node
        """
        checkBox = QCheckBox()
        checkBox.setObjectName(paramName+'_checkBox')
        self.connect(checkBox, SIGNAL("stateChanged(int)"), self.valChanged)
        
        toolButton = QToolButton()
        toolButton.setObjectName(paramName+"toolButton")
        
        return [checkBox, toolButton]
    
    def _getBoolean(self, paramName):
        checkBox = self.listWidget[paramName][1]
        state = checkBox.isChecked()
        return bool(state)
    
    def _setBoolean(self, paramName, value):
        """change the displayed value
        """
        checkBox = self.listWidget[paramName][1]
        checkBox.setChecked(value)

    ## Path2file
    def _path2fileFunc(self, paramName):
        lineEdit = QLineEdit()
        lineEdit.setObjectName(paramName+"_lineEdit")
        self.connect(lineEdit, SIGNAL("editingFinished()"), self.valChanged)
        
        openButton = QPushButton()
        openButton.setObjectName(paramName+'_openButton')
        openButton.setText('Open')
        self.connect(openButton, SIGNAL("clicked()"), self._openfile)
        
        toolButton = QToolButton()
        toolButton.setObjectName(paramName+"toolButton")
        #self._setPath2file(paramName, path)
        return [lineEdit, openButton, toolButton]
        
    def _openfile(self):
        paramName = '_'.join(str(self.sender().objectName()).split('_')[:-1])
        param = self.node._params[paramName]
        path = param.value
        directory = os.path.dirname(path[0]) if len(path)>0 else "."
        
        
        self._msgBox = QFileDialog(self, "Neuropype - Choose File")
        self._msgBox.setDirectory(directory)
        self._msgBox.setViewMode(QFileDialog.Detail)
        self._msgBox.setModal(True)
        self._msgBox.setNameFilters(param.ext)
        if param.mpl:
            self._msgBox.setFileMode(QFileDialog.ExistingFiles)
        else:
            self._msgBox.setFileMode(QFileDialog.ExistingFile)
        if self._msgBox.exec_():
            fname = self._msgBox.selectedFiles()[:]
            name = [str(i) for i in fname]
            name = str(name).strip("[], ")
            name = name.replace("'","")
            lineEdit = self.listWidget[paramName][1]
            # Default MaxLength of 32k truncates long lists.
            lineEdit.setMaxLength(len(name)+1)
            lineEdit.setText(name)
            self.valChanged(paramName)
            return name
        
    def _getPath2file(self, paramName):
        lineEdit = self.listWidget[paramName][1]
        listfiles = str(lineEdit.text()).split(',')
        listfiles = [i.strip(', ') for i in listfiles]
        return listfiles
    
    def _setPath2file(self, paramName, value):
        lineEdit = self.listWidget[paramName][1]
        lineEdit.setText(str(value).strip('[]').replace("'",''))

    ## Combobox
    def _comboboxFunc(self, paramName):
        """private function.
        
        used in DoLine to create the widgets
        Arguments:
        - `paramName`: key of the parameter in node
        """
        comboBox = QComboBox()
        parameter = self.node._params[paramName]
        comboBox.setObjectName(paramName+'_comboBox')
        comboBox.addItems(QStringList([QString(str(i)) for i in 
                                       parameter.universe]))
        comboBox.setCurrentIndex(comboBox.findText(QString(parameter.value)))
        self.connect(comboBox, SIGNAL("currentIndexChanged(int)"), 
                     self.valChanged)
        
        toolButton = QToolButton()
        toolButton.setObjectName(paramName+"toolButton")
        
        return [comboBox, toolButton]
    
    def _getCombobox(self, paramName):
        comboBox = self.listWidget[paramName][1]
        value = comboBox.currentText()
        return str(value)
    
    def _setCombobox(self, paramName, value):
        """change the displayed value
        """
        comboBox = self.listWidget[paramName][1]
        comboBox.setCurrentIndex(comboBox.findText(QString(value)))
    
    ## Float
    def _floatFunc(self, paramName):
        parameter = self.node._params[paramName]
        doubleSpinBox = QDoubleSpinBox()
        doubleSpinBox.setObjectName(paramName+"_doubleSpinBox")
        self.connect(doubleSpinBox, SIGNAL("valueChanged(int)"), 
                     self.valChanged)
        
        maxVal = parameter.maxVal()
        if maxVal is None:
            if hasattr(sys, 'float_info'):
                maxVal = sys.float_info.max
            else:
                maxVal = 1e15

        minVal = parameter.minVal()
        if minVal is None:
            if hasattr(sys, 'float_info'):
                minVal = -sys.float_info.max
            else:
                minVal = -1e15
        doubleSpinBox.setRange(float(minVal),float(maxVal))
        
        decimals = parameter.decimals()
        if decimals is None: 
            decimals = 10
        doubleSpinBox.setDecimals(int(decimals))
        
        singleStep = parameter.singleStep()
        if singleStep is None: 
            singleStep = 1e-3
        doubleSpinBox.setSingleStep(float(singleStep))
        
        toolButton = QToolButton()
        toolButton.setObjectName(paramName+"toolButton")
        #self._setFloat(paramName, value)
        return [doubleSpinBox, toolButton]
    
    def _setFloat(self, paramName, value):
        doubleSpinBox = self.listWidget[paramName][1]
        doubleSpinBox.setValue(float(value))
    
    def _getFloat(self, paramName):
        doubleSpinBox = self.listWidget[paramName][1]
        return float(doubleSpinBox.value())
    
    @pyqtSignature("")
    def on_applyPushButton_clicked(self):
        self.Apply()
    
    @pyqtSignature("")
    def on_cancelPushButton_clicked(self):
        self.Cancel()
    
    @pyqtSignature("")
    def on_closePushButton_clicked(self):
        self.close()
