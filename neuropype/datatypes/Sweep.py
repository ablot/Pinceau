'''Sweep datatype. Used for all input/outputs returning traces'''

from neuropype import datatype
from neuropype.datafile import ChannelType
#from itertools import imap, repeat

class Sweep(datatype.Datatype):
    '''Sweep data, contain an array and chan infos
    
    
    ###########################################################################
    Notes to create a Sweep, rather use the methods to access the data Sweep
    objects contain:
     - a single array with a line for the time and one per channel
     - a list of ChannelType objects (line[i] in the array has its info stored
     in chanInfo[i]
    
    see also ChannelType docstring
    ###########################################################################
    '''
    def __init__(self, name, data, chan_info, tag = None):
        '''data must be an array with time on row 0 and one row for each 
        channel chan_info must be a list ChannelType objects, name is usually
        'Sweep_'+str(index)'''
        super(Sweep, self).__init__(name)
        self._data = data
        if tag is not None:
            if not isinstance(tag, list):
                raise Exception, 'Error while creating Sweep\ntag is not a list'
            self.tag = tag
        if not isinstance(chan_info, list):
            chan_info = [chan_info]
        if len(chan_info) != len(data)-1: #-1 because of time line
            raise Exception, 'Error while creating Sweep\n len(chan_info != '\
            +'numChans)'
        self._name2index = {}
        for i, chaninf in enumerate(chan_info):
            if chaninf.__class__ != ChannelType:
                raise TypeError, "Error while creating Sweep\nchan_info must "\
                + "be a list of ChannelType instances"
            #self._name2index['Ch_'+str(chaninf.name)] = i+1
            #setattr(self, 'Ch_'+str(chaninf.name), chaninf)
            self._name2index[chaninf.name] = i+1
            setattr(self, chaninf.name, chaninf)
            
        #create a method to return a dict with gains, maxval ...
        for prop in ['title', 'units', 'isinput', 'maxval', 'gain']:
            setattr(self, prop, lambda:dict([(c.name, getattr(c, prop)) for c in chan_info]))
    
    def get_data(self, chan = None):
        '''Return the data array
        
        if chan is None return the whole array, return only channels whose name
        is in chan otherwise'''
        if chan is None:
            return self._data
        
        if not isinstance(chan, list):
            chan = [chan]
        return self._data[[0]+[self._name2index[c] for c in chan]]
    
    def numChans(self):
        return len(self._name2index)
    def chanNames(self):
        return self._name2index.keys()
    def _keepOnlyChan(self, chan):
        if chan is None:
            return self
        if not isinstance(chan, list):
            chan = [chan]        
        data = self._data[[0]+[self._name2index[c] for c in chan]]
        chan_info = [getattr(self, c) for c in chan]
        return Sweep(self.name, data, chan_info, self.tag)
