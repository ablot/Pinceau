# -*- coding: utf-8 -*-
'''Time_list datatype'''

## from itertools import imap, repeat
from neuropype import datatype
from neuropype.ressources._common import conv_dict

class Time_list(datatype.Datatype):
    '''Time_list data, contain a list of time and their properties (units,
    origin  ...)

    '''
    def __init__(self, name, data, origin, SweepIndex, nodeOfSweep,
                 title = 'NoTitle', units = 's', conv_dict = conv_dict):
        '''name is usually 'SpikeOfSweep_'+str(index), data must be a array of 
        time, origin is [File, Sweep, Chan], title is optional
        '''
        super(Time_list, self).__init__(name)
        self._data = data
        self._conv_dict = conv_dict
        if units not in self._conv_dict.keys():
            raise Exception, 'Error while creating Time_list\n Unknown unit:'+\
            ' got %s, can accept %s.'%(units, ', '.join(self._conv_dict.keys))
        self.units = units
        if not isinstance(origin, list):
            origin = [origin]
        self.origin = [str(i) for i in origin]
        self.title = title
        self.nodeOfSweep = nodeOfSweep
        self.SweepIndex = SweepIndex
    
    def __len__(self):
        return len(self._data)
    
    def get_data(self, units = None):
        if units is not None:
            return self.convert(units)
        return self._data
    
    def convert(self, units):
        if units not in self._conv_dict.keys():
            print 'Unknown unit!'
            return
        if units == self.units:
            return self._data
        ratio = self._conv_dict[self.units]/self._conv_dict[units]
        return self._data * ratio
        



