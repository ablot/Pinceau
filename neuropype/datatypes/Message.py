# -*- coding: utf-8 -*-
'''exemple of datatype file'''

from neuropype import node

class Message(object):
    '''Is the object transmitted between two nodes
    (fake datatype to test)'''
    def __init__(self, message):
        self.text = message

#class Output(node.Output):
    #'''Is the output of type 'message', I wonder if it worth subclassing Output
    #or if a generic class would be enough'''
    #def __init__(self, name, parent):
        #super(Output, self).__init__(name, parent)
    #def message(self, index):
        #print 'function to reimplement in each node\n must return a message instance'\
        #+'if index is not None, a list of all messages instances otherwise'
    #def length(self):
        #print 'function to reimplement in each node\n must return the total number'\
        #+'of message self can return with its "message" function'
    #def origin(self, index):
        #print 'function to reimplement in each node\n must return the origin of'\
        #+'data used to create this message'
    
#class Input(node.Input):
    #'''Is the input of type 'message'''
    #def __init__(self, name, parent):
        #super(Input, self).__init__(name, parent, connector_type = Output)
        #self.linked_properties = set(['message', 'length'])
    
    ##def connect(self, entry):
        ##self._connect(entry)
        ##self.message = entry.message
        ##self.length = entry.length
