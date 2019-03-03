# -*- coding: utf-8 -*-
import os

class parameter(object):
    '''Parameter class. Need to be sublclassed ofr each parameter type
    
    Store the value, the default value, the type checking function, a 
    dynamic parameter implementation and GUI information to change parameter
    '''
    def __init__(self, Name, Parent, Default, dirtyList = 'all'):
        """Initiate a new parameter instance
        
        - `name`: is the key of the dictionary param from parent node
        - `parent`: is the node in wich the parameter is used
        - `Default`: is the default value
        - `dirtyList`: is the list of outputs from parent that are dirty when
          value is changed
        """
        self.doc = 'No Documentation'
        self._name = Name
        self._parent = Parent
        self._default = Default
        self._value = Default
        self.dynamic = False
        self._dirtyList = 'all'

    #making properties
    def name():
        doc = """name of the parameter. Is the key in param dict"""
        def fget(self):
            return self._name
        def fset(self, value):
            print 'name cannot be changed.' 
            print 'If you know what you\'re doing, change self._name'
        return locals()
    name = property(**name())
    def parent():
        doc = """Node in wich the parameter is used"""
        def fget(self):
            return self._parent
        def fset(self, value):
            print 'parent cannot be changed.' 
            print 'If you know what you\'re doing, change self._parent'
        return locals()
    parent = property(**parent())
    def default():
        doc = """default value. Value of the parameter when it is created"""
        def fget(self):
            return self._default
        def fset(self, value):
            self.checkType(value)
            self._default = value
        def fdel(self):
            del self._default
        return locals()
    default = property(**default())
 
    def get_value(self):
        if self.dynamic:
            value = self.dynamic()
            if value != self._value:
                self.checkType(value)
                # self.dirty()
                self._value = value
        return self._value
    
    def set_value(self, value, check = 1):
        if hasattr(self.parent.parent, 'checkParams'):
            check = self.parent.parent.checkParams and check
        if check and value is not None:
            self.checkType(value)
        # self.dirty()          
        self._value = value
    value = property(fget = get_value, fset = set_value, 
                     doc = """Current value of the parameter""")
    
    def checkType(self, value = 'currentVal'):
        """checkType should raise ValueError if value is not correct,
        and return a the value (or a corrected value) if correct"""
        raise NotImplementedError('checkType needs to be reimplemented!')
    
###############################################################################
#################### Defining various parameter types #########################
###############################################################################

class path2file(parameter):
    '''Path to file(s)
    
    Value is a list of path to files. Default value is []
    
    ext is the list of supported extensions, used by GUI only. ext must be a
    list of strings with the appropriate filter(s) formated like this:
    'PClamp files (*.abf *.dat)'
    
    mpl (bool) allows the selection of more than one file in the GUI'''
    
    def __init__(self, name, parent, Default = [], dirtyList = 'all', ext = {},
                 mpl = True):
        Default = self.checkType(Default)
        super(path2file, self).__init__(name, parent, Default)
        # for name in path:
        #     if not os.path.isfile(name):
        #         path.remove(name)
        #         print '%s is not a valid file name and will be skipped'%name
        
        if not isinstance(ext, list):
            raise ValueError('Ext must be a list')
        
        self.ext = []
        for n in ext:
            n.strip()
            self.ext.append(str(n))
        self.mpl = bool(mpl)
    
    def checkType(self, value):
        """check if the new value is correct, ie if it is a list of path
        to existing files and return a corrected value if possible
        
        Arguments:
        - `value`: value to check
        """
        if isinstance(value, str):
            value = [value]
        elif not hasattr(value, '__iter__'):
            raise ValueError('Value %s of %s has an incorrect type'%(
                             value, self.name))
        for name in value:
            if not os.path.isfile(name):
                value.remove(name)
                print '%s is not a valid file name and will be skipped'%name
        return value

    def __str__(self):
        return 'path2file instance with path: %s'%self.value

class boolean(parameter):
    """One boolean
    
    Parameter subclass used to hold a single boolean
    """
    
    def __init__(self, name, parent, Default = False, dirtyList = 'all'):
        """
        
        Arguments:
        - `name`: is the key of the dictionary param from parent node
        - `parent`: is the node in wich the parameter is used
        - `Default`: is the default value
        - `dirtyList`: is the list of outputs from parent that are dirty when
          value is changed     
        """
        super(boolean,self).__init__(name, parent, Default, dirtyList)
    
    def checkType(self, value):
        """test if the value can be converted into a boolean
        """
        try:
            value = bool(value)
        except Exception:
            raise ValueError('Value %s of %s has an incorrect type'%(
                             value, self.name))
        return value       
     
class integer(parameter):
    """One integer
    
    Parameter subclass used to hold single integer parameters
    """
    
    def __init__(self, name, parent, Default = None, dirtyList = 'all', 
                 minVal = None, maxVal = None):
        """
        
        Arguments:
        - `name`: is the key of the dictionnary param from parent node
        - `parent`: is the node in wich the parameter is used
        - `Default`: is the default value
        - `dirtyList`: is the list of outputs from parent that are dirty when
          value is changed     
        - `minVal`: minimal value the integer can take
        - `maxVal`: maximal value the integer can take
        """
        super(integer, self).__init__(name, parent, Default, dirtyList)
        self._minVal = minVal
        self._maxVal = maxVal
    
    def minVal(self):
        if hasattr(self._minVal, '__call__'):
            return int(self._minVal())
        return int(self._minVal) if self._minVal is not None else None
    
    def maxVal(self):
        if hasattr(self._maxVal, '__call__'):
            return int(self._maxVal())
        return int(self._maxVal) if self._maxVal is not None else None
    
    def checkType(self, value):
        try:
            value = int(value)
        except Exception:
            raise ValueError('Value %s of %s has an incorrect type'%(
                             value, self.name))
        return value


class float_param(parameter):
    """One float_param
    
    Parameter subclass used to hold single float_param parameters
    """
    
    def __init__(self, name, parent, Default= None, dirtyList= 'all', minVal=
                 None, maxVal= None, decimals= None, singleStep= None):
        """
        
        Arguments:
        - `name`: is the key of the dictionnary param from parent node
        - `parent`: is the node in wich the parameter is used
        - `Default`: is the default value
        - `dirtyList`: is the list of outputs from parent that are dirty when
          value is changed     
        - `minVal`: minimal value the float_param can take
        - `maxVal`: maximal value the float_param can take
        - `decimals`: precision of the float in decimals (used by GUI)
        - `singleStep`: minal step (speed of change) used by GUI
        """
        super(float_param, self).__init__(name, parent, Default, dirtyList)
        self._minVal = minVal
        self._maxVal = maxVal
        self._decimals = decimals
        self._singleStep = singleStep
    
    def minVal(self):
        if hasattr(self._minVal, '__call__'):
            return float(self._minVal())
        return float(self._minVal) if self._minVal is not None else None
    
    def maxVal(self):
        if hasattr(self._maxVal, '__call__'):
            return float(self._maxVal())
        return float(self._maxVal) if self._maxVal is not None else None

    def decimals(self):
        if hasattr(self._decimals, '__call__'):
            return float(self._decimals())
        return float(self._decimals) if self._decimals is not None else None

    def singleStep(self):
        if hasattr(self._singleStep, '__call__'):
            return float(self._singleStep())
        return float(self._singleStep) if self._singleStep is not None else None
    
    def checkType(self, value):
        try:
            value = float(value)
        except Exception:
            raise ValueError('Value %s of %s has an incorrect type'%(
                             value, self.name))
        return value


        
class combobox(parameter):
    """One string chosen among some possibilities
    """
    
    def __init__(self, name, parent, universe, Default = None,
                 dirtyList = 'all', func = None):
        """
        
        Arguments:
        - `name`: is the key of the dictionary param from parent node
        - `parent`: is the node in which the parameter is used
        - `universe`: is a list of str that the parameter can take as value
        - `Default`: is the default value
        - `dirtyList`: is the list of outputs from parent that are dirty when
          value is changed
        - `func`: is the getter of universe. Default (None) return universe
          set at initiation. Change it to have more complex behaviour 
          (dynamic universe)
        
        """
        super(combobox, self).__init__(name, parent, Default, dirtyList)
        self._universe = universe
        if func is None:
            self._func = lambda: self._universe
        else:
            self._func = func
        
        #self._universe = universe
    def universe():
        doc = """Possible value for parameter"""
        def fget(self):
            return self._func()
        def fset(self, value):
            self._universe = value
        def fdel(self):
            del self._universe
        return locals()
    universe = property(**universe())
    
    def checkType(self, value):
        try:
            value = str(value)
        except Exception:
            raise ValueError('Value %s of %s has an incorrect type'%(value,
                             self.name))
        if value not in self.universe:
            raise ValueError('Value %s of %s is not among possible values'%
                             (value, self.name))
    
    
