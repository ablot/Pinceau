# -*- coding: utf-8 -*-
'''This module contains the container and connection framework'''

#import exceptions
from copy import deepcopy
#import sys
import parameter

class ConnectionError(Exception):
    pass

# I think Input and Output don't need names, as they will be found be searching
# by node attributes.
class Connector(object):
    '''Callable connector class providing typed data.'''
    def __init__(self, Type):
        # TODO: include check that Type exists in the datatypes module?
        self.Type = Type
    # Indirection via output is required as __call__ is a class method not an 
    # instance method, so cannot be reset as we wish.
    def __call__(self, *args, **kwargs):
        #ipshell()
        node = self.output.im_self
        ## if 'tag' not in kwargs.keys():
        ##     raise NotImplementedError('Call without tag!')
        # raise Error to make sure all nodes are transmitting down the tag.
        # each node should deal with the tag it created 
        out = self.output(*args, **kwargs)
        if hasattr(out, 'way'):
            out.way.append(node.name)
            
        if node.parent.interactif_graph:
            #ipshell()
            node.parent.graph.select_node(node.name, 'r')
            node.parent.graph.select_node(node.name, 'g')
        
        return out
    
    def output(self, *args, **kwargs):
        self._unconnected(*args, **kwargs)
        return
    def _unconnected(self, *args, **kwargs):
        raise ConnectionError('Connector not connected!')
    
class Output(Connector):
    def __init__(self, Type):
        super(Output, self).__init__(Type)
        return

class Input(Connector):
    def __init__(self, Type):
        super(Input, self).__init__(Type)
        self.source = 'NotConnected'
        return
    

class Node(object):
    '''Hosts input and output connectors, analysis functions; housekeeping for 
    connections, saving, updating.
    
    Propeties'''
    
    def __init__(self, name, parent = None, autoLoad = False):
        self._name = name
        self._parent = parent
        self._params= dict()
        self._cache = dict()
        self._outputGroups = dict()
        self._inputGroups = dict()
        self._inGrConnection = dict()
        self._outGrConnection = dict()
        #######################################################################
        # In subclasses, instantiate the required inputs and outputs **before** 
        # calling the base class constructor (__init__).
        # Subclasses also need to link the output __call__s to the appropriate 
        # internal functions.
        #######################################################################
        self.inputs = dict()
        self.outputs = dict()
        self.tagCreated = dict() #keys are tagClass that this node needs to 
        # handle himself. Value are parameters used by the node to create the 
        # tag. 
        for i in vars(self).keys():
            m = getattr(self, i)
            if isinstance(m, Input):
                self.inputs[i] = None
            elif isinstance(m, Output):
                self.outputs[i] = set()
        return
    
    #make name and parent read only properties:
    @property
    def name(self):
        'Read only property. Name of the node'
        return self._name
    @property
    def parent(self):
        'Read only property. Tree in wich is the node'
        return self._parent
    
    @property
    def params(self):
        'Read only property. Parameters of the node'
        return dict([(k, self.get_param(k)) for k in self._params.keys()])
    
    def set_param(self, *args, **kwargs):
        '''Change the parameters of the node and erase cache
        
        Accept two positionnal arguments: 'param_name', 'value'
        and any number of keyword arguments param_name = 'value'
        '''
        # checking syntax call
        if args:
            if len(args) == 2:
                kwargs[args[0]] = args[1]
            else:
                raise ValueError('set_param accept 0 or 2 positionnal arguments')
        dirty_list = []
        for param_name, value in kwargs.iteritems():
            if self._params.get(param_name, 'Error') == 'Error':
                print 'Error!!! \n There is no parameter named %s'%param_name
                return
            param = self._params[param_name]
            #is param of a parameter subclass?
            if type(param).__base__ == parameter.parameter:
                param.value = value
                dirty_list.append(param._dirtyList)
            else:
                #old type:
                #print '%s in %s is old type parameter. Needs to be updated'%(
                #                                       param_name, self.name)
                self._params[param_name] = value
                dirty_list.append('all')
                
        self.dirty(dirty_list)        
       
    
    def get_param(self, param_name):
        out = self._params.get(param_name)
        if type(out).__base__ == parameter.parameter:
            out = out.value
        return out

    def default_param(self, param_name = None, reset = True):
        """Return default values of params (if defined)
        
        - `param_name`: name of the param to reset, if None reset all
          the parameters
        - `reset`: if False, don't set the param, just return the values"""
        if param_name is None:
            param_name = self.params
        elif not isinstance(param_name, list):
            param_name = [param_name]
        default = {}
        for name in param_name:
            param = self._params.get(name)
            if type(param).__base__ == parameter.parameter:
                default[name] = param.default
        if reset:
            for name, value in default.iteritems():
                self.set_param(name, value)
        return default
    
    def get_cache(self, key):
        '''Return cached value if defined, None else'''
        return self._cache.get(key)
    def cache(self):
        '''return all the data in cache'''
        return self._cache
    def iscached(self, key):
        return self._cache.has_key(key)
    def chge_cache(self, key, value):
        '''Change an already existing cached value'''
        self._cache.pop(key)
        self._cache[key] = value
    def set_cache(self, key, value, force = 0):
        '''Try to set cache key to value and return the value
        
        if not force set it only if key is not already cached'''
        if force:
            self._cache[key]=value
        else:
            if self._cache.has_key(key):
                raise ValueError('%s is already in cache. Use force to '%key  \
            +'replace it')
            self._cache.setdefault(key, value)
    
    def Connect(self, inputName, upstreamNodeName, upstreamOutputName, force=0):
                
        upstreamNode = getattr(self.parent, upstreamNodeName)
        if inputName in self.inputs.keys():
            self._disconnectInput(inputName)
            self._connect(inputName, upstreamNode, upstreamOutputName)
        elif inputName in self._inputGroups.keys():
            
            
            upGroup = upstreamNode._outputGroups[upstreamOutputName]
            inGroup = self._inputGroups[inputName]
            if force:
                pass
            elif sorted(upGroup.keys()) != sorted(inGroup.keys()):
                raise ConnectionError('Groups are different!')
            self.disconnectInput(inputName)
            for inptype, inpName in inGroup.iteritems():
                upOutName = upGroup[inptype]
                self._connect(inpName, upstreamNode, upOutName)
            self._inGrConnection[inputName] = (upstreamNodeName, 
                                                    upstreamOutputName)
            grpSet = upstreamNode._outGrConnection.get(upstreamOutputName)
            if grpSet is None:
                upstreamNode._outGrConnection[upstreamOutputName] = set()
                grpSet = upstreamNode._outGrConnection.get(upstreamOutputName)
            grpSet.add((self.name, inputName))
        else:
            print 'No input named %s in node %s'%(inputName, self.name)
        
    def disconnectInput(self, inputName, verbose = 1):
        
        if inputName in self.inputs.keys():
            self._disconnectInput(inputName)
        elif inputName in self._inputGroups.keys():
            for inptype, inpName in self._inputGroups[inputName].iteritems():
                self._disconnectInput(inpName)
            if self._inGrConnection.get(inputName) is not None:
                upNodeName, upGr = self._inGrConnection.pop(inputName)
                upNode = getattr(self.parent, upNodeName)
                upNode._outGrConnection[upGr].remove((self.name, inputName))
        else:
            print 'No input named %s in node %s'%(inputName, self.name)
    
    def disconnectOutput(self, outputName, verbose = 1):
        
        if outputName in self.outputs.keys():
            self._disconnectOutput(outputName)
        elif outputName in self._outputGroups.keys():
            for outtype, outName in self._outputGroups[outputName].iteritems():
                self._disconnectOutput(outName)
            if self._outGrConnection.get(outputName) is not None:
                outSet = self._outGrConnection[outputName]
                for connected in outSet:
                    
                    downNodeName, downGr = connected
                    downNode = getattr(self.parent, downNodeName)
                    downNode._inGrConnection[downGr] = None
                outSet.clear()
        else:
            print 'No output named %s in node %s'%(outputName, self.name)
    
    def _connect(self, thisNodeInputName, upstreamNode, upstreamOutputName):
        # Check if Types agree
        inputType = getattr(self, thisNodeInputName).Type
        outputType = getattr(upstreamNode, upstreamOutputName).Type
        if not self._checkType(inputType, outputType):
            raise ValueError('Error while connecting %s'%thisNodeInputName + \
                             '\nTypes disagree, expect "%s"'%inputType +  \
                             '\ngot "%s"'%outputType)
        # Make the connection.
        getattr(self, thisNodeInputName).output = getattr(upstreamNode,       \
        upstreamOutputName).output
        getattr(self, thisNodeInputName).source = getattr(upstreamNode,       \
        upstreamOutputName)
        # Only record connection afterwards, in case of error.
        self.inputs[thisNodeInputName]=(upstreamNode.name, upstreamOutputName)
        
        upstreamNode.outputs[upstreamOutputName].add((self.name,              \
        thisNodeInputName))
        self.updateNode()
        return
    
    def _disconnectInput(self, thisNodeInputName, verbose = 0):
        if not self.inputs.has_key(thisNodeInputName):
            raise AttributeError('%s has no input named %s'%(self.name,       \
        thisNodeInputName))
        if self.inputs[thisNodeInputName] is not None:
            # Get the output set of the upstream node in its outputs dict.
            upstreamNodeName, upstreamOutputName=self.inputs[thisNodeInputName]
            upstreamNode = getattr(self.parent, upstreamNodeName) 
            upstreamOutputs = upstreamNode.outputs[upstreamOutputName]
            if verbose: print '%s is connected to %s from %s'%(               \
            thisNodeInputName, upstreamOutputName, upstreamNode.name)
            try:
                upstreamOutputs.remove((self.name, thisNodeInputName))
            except KeyError:
                raise AttributeError('Error %s is not connected to %s from %s'\
                %(thisNodeInputName, upstreamOutputName, upstreamNode.name))
            # if it worked: remove the connection from self.inputs
            self.inputs[thisNodeInputName] = None
            getattr(self, thisNodeInputName).output =  \
                                     getattr(self, thisNodeInputName)._unconnected
            getattr(self, thisNodeInputName).source = 'NotConnected'
            if verbose: print 'disconnected!'
        elif verbose: print '%s is not connected'%thisNodeInputName
        return
    
    def _checkType(self, inputType, outputType):
        """check if types agree before connecting

        type can be 'any', to accept any connection, a string to accept
        only this kind of input or a list of string to accept any of
        these inputs
        
        Arguments:
        - `inputType`: type of the input
        - `outputType`: type of the output
        """
        if inputType == 'any' or outputType == 'any':
            return True
        
        if not isinstance(inputType, list): inputType= [str(inputType)]
        if not isinstance(outputType, list): outputType= [str(outputType)]

        if any([inp in outputType for inp in inputType]):
            return True
        
        return False
        

    def _disconnectOutput(self, thisNodeOutputName, verbose = 0):
        if not self.outputs.has_key(thisNodeOutputName):
            raise AttributeError('%s has no output named %s'%(self.name,      \
        thisNodeOutputName))
        if len(self.outputs[thisNodeOutputName]) > 0:
            for downstreamNodeName, downstreamNodeInputName in self.outputs[  \
            thisNodeOutputName].copy():
                #copy is needed since set size while be changed during iteration
                downstreamNode = getattr(self.parent, downstreamNodeName)
                downstreamNode.disconnectInput(downstreamNodeInputName,  \
                verbose)
        elif verbose: print '%s is not connected'%thisNodeOutputName
        return

    def dirty(self, dirty_list, selfDirty = True, verbose = 0):
        '''dirty a node and linked outputs

        dirty_list is the list of outputs to dirty. If 'all', all linked output
        receive dirty('all'), if None, none of them, if a list of name is supplied
        outputs in this list only'''
        # self.isDirty = True
        if selfDirty:
            self._cache.clear()
        if not isinstance(dirty_list,list):
            dirty_list= [dirty_list]
        dirt = []
        if 'all' in dirty_list:
            for outputName, connectedSet in self.outputs.iteritems():
                for NodeName, InName in connectedSet:
                    if NodeName not in dirt:
                        getattr(self.parent, NodeName).dirty('all')
                        dirt.append(NodeName)
                        if verbose:
                            print '%s call dirty of %s'%(self.name, NodeName)
            return
        for name in dirty_list:
            if name is not None:
                for NodeName, InName in self.outputs[name]:
                    getattr(self.parent, NodeName).dirty('all')
        self._parent.dirty = True
        
    
    def updateNode(self):
        self.dirty('all')
    
    def clone(self, name):
        """Create a new node with same paramters and input connectivity in the parent tree"""
        t = self.parent
        if name in t.list_nodes():
            print 'A node named %s already exist'%name
            return
        t.addNode(name, type(self).__name__)
        newNode = getattr(t, name)
        for inputName, key  in self.inputs.iteritems():
            if key:
                nodeName, outputName = key
                newNode.Connect(inputName, nodeName, outputName)
        for k, v in self.params.iteritems():
            newNode.set_param(k, deepcopy(v))
        return newNode
        

