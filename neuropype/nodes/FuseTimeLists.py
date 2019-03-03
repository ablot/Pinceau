# -*- coding: utf-8 -*-

from neuropype import node
from neuropype import parameter
import numpy as np
from neuropype.tag import combine
from neuropype.datatypes.Time_list import Time_list

class FuseTimeLists(node.Node):
    """Fuse two time lists in one"""
    
    def __init__(self, name, parent):
        # Inputs
        self.in_time1 = node.Input('Time_list')
        self.in_numSweeps1 = node.Input('int')
        self.in_tagTimeList1 = node.Input('list')
        
        self.in_time0 = node.Input('Time_list')
        self.in_numSweeps0 = node.Input('int')
        self.in_tagTimeList0 = node.Input('list')
            
        # Outputs
        self.out_time = node.Output('Time_list')
        self.out_numSweeps = node.Output('int')
        self.out_tagTimeList = node.Output('list')
        
        super(FuseTimeLists, self).__init__(name, parent)

        # Groups
        self._inputGroups = {'time_list0': {'time_list': 'in_time0',
                                            'numSweeps': 'in_numSweeps0',
                                            'tag': 'in_tagTimeList0'},
                             'time_list1': {'time_list': 'in_time1',
                                            'numSweeps': 'in_numSweeps1',
                                            'tag': 'in_tagTimeList1'}
                            }
        
        self._outputGroups = {'time_list':  {'time_list': 'out_time',
                                             'numSweeps': 'out_numSweeps',
                                             'tag': 'out_tagTimeList'}}
        
        # Default parameters:
        
        #connecting outputs:
        
        self.out_time.output = self.time_list
        self.out_numSweeps.output = self.numSweeps
        self.out_tagTimeList.output = self.tag

    def time_list(self, index_sweep):
        tl0, tl1 = None, None
        SweepIndex = index_sweep
        nodeOfSweep = 'unknown'
        name = 'fused_%s'%index_sweep
        if index_sweep < self.in_numSweeps0():
            tl0 = self.in_time0(index_sweep)
        if index_sweep < self.in_numSweeps1():
            tl1 = self.in_time1(index_sweep)
        if tl0 is None and tl1 is None:
            raise ValueError('wrong index')
        if tl0 is None:
            return tl1
        if tl1 is None:
            return tl0
        tag = combine(tl1.tag, tl0.tag)
        data = np.sort(np.hstack((tl1._data,tl0._data)))
        origin = tl0.origin + tl1.origin
        out = Time_list(name, data, origin, SweepIndex, nodeOfSweep)
        out.tag = tag
        return out

    def numSweeps(self):
        return max(self.in_numSweeps0(), self.in_numSweeps1())

    def tag(self, index_sweep):
        if index_sweep < self.in_numSweeps0():
            tl0 = self.in_tagTimeList0(index_sweep)
        if index_sweep < self.in_numSweeps1():
            tl1 = self.in_tagTimeList1(index_sweep)
        if tl0 is None and tl1 is None:
            raise ValueError('wrong index')
        if tl0 is None:
            return tl1
        if tl1 is None:
            return tl0
        return combine(tl1, tl0)
