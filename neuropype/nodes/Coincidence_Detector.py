from neuropype import node
from neuropype.datatypes.Time_list import Time_list
import numpy as np
#from itertools import imap
from copy import deepcopy
from neuropype.ressources._common import checkInput
#import neuropype.ressources.progressbar as pgb

class Coincidence_Detector(node.Node):
    '''
    '''
    
    def __init__(self, name, parent):
        
        self.in_time0 = node.Input('Time_list')
        self.in_numSweeps0 = node.Input('int')
        self.in_tag_time_list0 = node.Input('list')
        
        self.in_time1 = node.Input('Time_list')
        self.in_numSweeps1 = node.Input('int')
        self.in_tag_time_list1 = node.Input('list')
        
        self.out_time0 = node.Output('Time_list')
        self.out_time1 = node.Output('Time_list')
        self.out_time_both = node.Output('Time_list')
        self.out_numSweeps = node.Output('int')
        self.out_tag_time_list = node.Output('list')
        
        super(Coincidence_Detector, self).__init__(name, parent)
        
        self._inputGroups['time_list0'] = {'time_list': 'in_time0',
                                           'numSweeps': 'in_numSweeps0',
                                           'tag': 'in_tag_time_list0'}
        self._inputGroups['time_list1'] = {'time_list': 'in_time1',
                                           'numSweeps': 'in_numSweeps1',
                                           'tag': 'in_tag_time_list1'}
        
        self._outputGroups['time_list0'] = {'time_list': 'out_time0',
                                            'numSweeps': 'out_numSweeps',
                                            'tag': 'out_tag_time_list'}
        
        self._outputGroups['time_list1'] = {'time_list': 'out_time1',
                                            'numSweeps': 'out_numSweeps',
                                            'tag': 'out_tag_time_list'}
        
        self._outputGroups['time_list_both'] = {'time_list': 'out_time_both',
                                                'numSweeps': 'out_numSweeps',
                                                'tag': 'out_tag_time_list'}
        
        self._params = {'win': [-.5e-3,.5e-3]}
        
        #connecting outputs:
        self.out_time0.output = self.time0
        self.out_time1.output = self.time1
        self.out_time_both.output = self.time_both
        self.out_numSweeps.output = self.numSweeps
        self.out_tag_time_list.output = self.tag
    
    def numSweeps(self):
        """Number of sweeps in node.

        Is equal to min(in_numSweeps0, in_numSweeps1)
        
        Arguments:
        - `list_index`: input time_list to consider, if None, use all the inputs
        """
        return min(self.in_numSweeps0(), self.in_numSweeps1())
    
    
    def tag(self, index):
        """Return the tags of time `index`
        
        Arguments:
        - `index`: index to consider, integer < self.numSweeps
        """
        
        inTag0 = self.in_tag_time_list0(index)
        inTag1 = self.in_tag_time_list1(index)
        outTag = inTag0 + inTag1
        return outTag

    def time0(self, sweep_index):
        tl0 = self.in_time0(sweep_index)
        tl1 = self.in_time1(sweep_index)
        ar0 = tl0.get_data('s')
        ar1 = tl1.get_data('s' )
        win = np.array(self.get_param('win'))
        out = []
                    
        for sp in ar0:
            temp = ar1.searchsorted(win+sp)

            if not ar1[temp[0]:temp[1]]:
                out.append(sp)
        tl0._data = np.array(out)
        tl0._tag = self.tag(sweep_index)
        return tl0
        
    def time1(self, sweep_index):
        tl0 = self.in_time0(sweep_index)
        tl1 = self.in_time1(sweep_index)
        ar0 = tl0.get_data('s')
        ar1 = tl1.get_data('s' )
        win = np.array(self.get_param('win'))
        out = []
        
        for sp in ar1:
            temp = ar0.searchsorted(win+sp)
            if not ar0[temp[0]:temp[1]]:
                out.append(sp)
        tl1._data = np.array(out)
        tl1._tag = self.tag(sweep_index)
        return tl1
        
    def time_both(self, sweep_index):
        tl0 = self.in_time0(sweep_index)
        tl1 = self.in_time1(sweep_index)
        ar0 = tl0.get_data('s')
        ar1 = tl1.get_data('s' )
        win = np.array(self.get_param('win'))
        out = []
        if ar0.size <= ar1.size:
            short = ar0
            long = ar1
        else:
            short = ar1
            long = ar0
            
        for sp in short:
            temp = long.searchsorted(win+sp)
            out.extend(long[temp[0]:temp[1]])
        tl0._data = np.array(out)
        tl0._tag = self.tag(sweep_index)
        return tl0

