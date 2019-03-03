'''SweepData datatype. Like Sweep but with raw data, so no time, and strange unit'''

from neuropype import datatype
from neuropype.datafile import ChannelType
#from itertools import imap, repeat

class SweepData(datatype.Datatype):
    '''SweepData, contain an array and chan infos
    
    
    ###########################################################################
    Notes to create a Sweep, rather use the methods to access the data Sweep
    objects contain:
     - a single array without the time and one line per channel
     - a list of ChannelType objects (line[i] in the array has its info stored
     in chanInfo[i]
    
    see also ChannelType docstring
    ###########################################################################
    '''
    def __init__(self, name, data, chan_info, tag = None):
        '''data must be an array with one row for each channel  chan_info must
        be a list ChannelType objects, name is usually 'Sweep_'+str(index)'''
        super(SweepData, self).__init__(name)
        self._data = data
        if tag is not None:
            if not isinstance(tag, list):
                raise Exception, 'Error while creating Sweep\ntag is not a list'
            self.tag = tag
        if not isinstance(chan_info, list):
            chan_info = [chan_info]
        if len(chan_info) != len(data):
            raise Exception, 'Error while creating Sweep\n len(chan_info != '\
            +'numChans)'
        self._name2index = {}
        for i, chaninf in enumerate(chan_info):
            if chaninf.__class__ != ChannelType:
                raise TypeError, "Error while creating Sweep\nchan_info must "\
                + "be a list of ChannelType instances"
            #self._name2index['Ch_'+str(chaninf.name)] = i+1
            #setattr(self, 'Ch_'+str(chaninf.name), chaninf)
            self._name2index[chaninf.name] = i
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
        return self._data[[self._name2index[c] for c in chan]]
    
    def numChans(self):
        return len(self._name2index)
    def chanNames(self):
        return self._name2index.keys()
    def _keepOnlyChan(self, chan):
        if chan is None:
            return self
        if not isinstance(chan, list):
            chan = [chan]        
        data = self._data[[self._name2index[c] for c in chan]]
        chan_info = [getattr(self, c) for c in chan]
        return SweepData(self.name, data, chan_info, self.tag)
