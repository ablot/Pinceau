from neuropype import node
from neuropype.datatypes.Time_list import Time_list
import numpy as np
#from itertools import imap
from copy import deepcopy
from neuropype.ressources._common import checkInput
from node import ConnectionError
#import neuropype.ressources.progressbar as pgb

class RepeatTimeList(node.Node):
    '''Dummy node to repeat the same time_list over and over

    if it is connected, one can set the index of the time_list to be repeated
    else one can put an array in time_list_to_repeat'''
    
    def __init__(self, name, parent):
        
        self.in_time = node.Input('Time_list')
        self.in_numSweeps = node.Input('int')
        self.in_tag_time_list = node.Input('list')
        
        self.out_time = node.Output('Time_list')
        self.out_numSweeps = node.Output('int')
        self.out_tag_time_list = node.Output('list')
        
        super(RepeatTimeList, self).__init__(name, parent)
        self._inputGroups['time_list'] = {'time_list': 'in_time',
        'numSweeps': 'in_numSweeps', 'tag': 'in_tag_time_list'}
        self._outputGroups['time_list'] = {'time_list': 'out_time',
        'numSweeps': 'out_numSweeps', 'tag': 'out_tag_time_list'}
        
        self._params = {'ind2repeat': None,
                        'time_list_to_repeat': None,
                        'name': None,
                        'origin':None,
                        'units': 's',
                        'numSweeps': None
                        }
        
        
        #connecting outputs:
        self.out_time.output = self.time
        self.out_numSweeps.output = self.numSweeps
        self.out_tag_time_list.output = self.tag
    
      
    def numSweeps(self, list_index = None):
        v = self.get_param('numSweeps')
        if v is None:
            return np.inf
        return v
    
    def tag(self, index):
        """Return the tags of time `index`
        
        Arguments:
        - `index`: index to consider, integer < self.numSweeps
        """
        try:
            return self.in_tag_time_list(index)
        except ConnectionError:
            return []
        
    
    def time(self, index):
        """Return the time at `index`
        
        Arguments:
        - `index`: index to consider, integer < self.numSweeps
        """
        ind2repeat = self.get_param('ind2repeat')
        if ind2repeat is not None:
            return self.in_time(ind2repeat)
        data = self.get_param('time_list_to_repeat')
        if data is None:
            raise ValueError('You have to set at least one param')
        name= self.get_param('name')
        origin = self.get_param('name')
        units = self.get_param('units')
        return Time_list( name, np.array(data), origin, index, self, units = units)
