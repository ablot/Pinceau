# -*- coding: utf-8 -*-

import numpy as np
from neuropype import node
#from itertools import imap, repeat
#from copy import deepcopy, copy

#from bisect import bisect_left
#from neuropype.ressources._common import boxfilter, findextrema, cross_threshold, flatenList
#import neuropype.ressources.progressbar as pgb
#from neuropype.datatypes import Time_list, Sweep

# Node name.
class SweepToInt(node.Node):
    def __init__(self, name, parent):
        #inputs
        self.in_sweep = node.Input('Sweep')
        self.in_numSweeps = node.Input('int')
        self.in_chanNames = node.Input('list')
        self.in_origin = node.Input('list')
        self.in_tag = node.Input('list')
        self.in_sweepInfo = node.Input('SweepInfo')
        
        #outputs

        self.out_numSweeps = node.Output('int')
        self.out_sweep = node.Output('Sweep')
        self.out_chanNames = node.Output('list')
        self.out_origin = node.Output('list')
        self.out_sweepInfo = node.Output('SweepInfo')
        self.out_tag = node.Output('list')
        
        super(SweepToInt, self).__init__(name, parent)
        self._inputGroups['sweep'] = {'sweep': 'in_sweep',
                                      'numSweeps': 'in_numSweeps',
                                      'chanNames': 'in_chanNames',
                                      'origin': 'in_origin',
                                      'tag' : 'in_tag',
                                      'sweepInfo': 'in_sweepInfo'}
        
        self._outputGroups = {'sweep': {'sweep': 'out_sweep',
                                                'numSweeps': 'out_numSweeps',
                                                'chanNames': 'out_chanNames',
                                                'origin': 'out_origin',
                                                'tag': 'out_tag',
                                                'sweepInfo': 'out_sweepInfo'}}
        self._params={}
        
        #connecting outputs:
        
        self.out_numSweeps.output = self.numSweeps
        self.out_chanNames.output = self.chanNames
        self.out_sweep.output = self.sweep
        self.out_origin.output = self.origin
        self.out_sweepInfo.output = self.sweepInfo
        self.out_tag.output = self.tag
    
   
    def sweep(self, sweep_index, chan = None):
        in_sw = self.in_sweep(sweep_index, chan)
        factor = np.array([getattr(in_sw, cname).factor for cname in in_sw.chanNames()], ndmin = 2)
        in_sw._data[1:] /= factor.T
        in_sw._data[0] = np.arange(in_sw._data.shape[1])
        in_sw._data = np.array(in_sw._data, dtype = 'int16')
        return in_sw
    
    def tag(self, index_sweep):
        return self.in_tag(index_sweep)
    
    def numSweeps(self):
        return self.in_numSweeps()
    
    def chanNames(self, sweep_index = 0):
        return self.in_chanNames(sweep_index)
    
    def origin(self, sweep_index):
        return self.in_origin(sweep_index)
    
    def sweepInfo(self, sweep_index):
        return self.in_sweepInfo(sweep_index)
