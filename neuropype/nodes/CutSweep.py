# -*- coding: utf-8 -*-

from neuropype import node
from neuropype.datatypes import Sweep
from neuropype.ressources._common import boxfilter
from scipy.signal import order_filter, medfilt
from numpy import ones, vstack
from math import ceil

##debuging tool!
#from IPython.Shell import IPShellEmbed
#banner = '\n*** Nested interpreter *** \n\nYou are now in a nested ipython'
#exit_msg = '*** Closing embedded IPython ***'
##paramv = ['-noconfirm_exit', '-pi1','Neuropype In <\\#>:','-pi2','     .\\D.:','-po','Out<\\#>:']
#paramv = ['-pi1','Neuropype In <\\#>:','-pi2','     .\\D.:','-po','Out<\\#>:']
#ipshell = IPShellEmbed(paramv, banner=banner,exit_msg=exit_msg)
##end of debuging tool

class CutSweep(node.Node):
    '''Cut part of a sweep

    Parameters:

    beg: beginnig of the part to keep (s), 'beg' to start from first point
    end: end of the part to keep (s), 'end' to end with last point
    zero_time: put the time of the first point to 0 (boolean), else the initial
               value will be kept
    
    
    '''
    
    def __init__(self, name, parent):
        self.in_sweep = node.Input('Sweep')
        self.in_numSweeps = node.Input('int')
        self.in_chanNames = node.Input('list')
        self.in_origin = node.Input('list')
        self.in_tag = node.Input('list')
        self.in_sweepInfo = node.Input('SweepInfo')
        
        self.out_sweep = node.Output('Sweep')
        self.out_numSweeps = node.Output('int')
        self.out_chanNames = node.Output('list')
        self.out_origin = node.Output('list')
        self.out_tag = node.Output('list')
        self.out_sweepInfo = node.Output('SweepInfo')
        
        super(CutSweep, self).__init__(name, parent)
        
        self._inputGroups['sweep'] = {'sweep': 'in_sweep', 'numSweeps':
        'in_numSweeps', 'chanNames': 'in_chanNames', 'origin': 'in_origin', 
        'tag': 'in_tag', 'sweepInfo': 'in_sweepInfo'}
        self._outputGroups['sweep'] = {'sweep': 'out_sweep', 'numSweeps': 
        'out_numSweeps', 'chanNames': 'out_chanNames', 'origin': 'out_origin', 
        'tag': 'out_tag', 'sweepInfo': 'out_sweepInfo'}
        
        self._params = {'beg' : 'beg','end':'end', 'zero_time': False}
        
        self.out_sweep.output = self.sweep
        self.out_numSweeps.output = self.numSweeps
        self.out_chanNames.output = self.chanNames
        self.out_origin.output = self.origin
        self.out_tag.output = self.tag
        self.out_sweepInfo.output = self.sweepInfo
        
    def tag(self, index):
        return self.in_tag(index)
    
    def origin(self, index):
        return self.in_origin(index)
    
    def chanNames(self, index = 0):
        return self.in_chanNames(index)
            
    def numSweeps(self):
        return self.in_numSweeps()
    
    def sweepInfo(self, index):
        sw_inf = self.in_sweepInfo(index)
        beg = self.get_param('beg')
        end = self.get_param('end')
        end = end if end != 'end' else sw_inf.tend
        beg = beg if beg != 'beg' else sw_inf.t0
        if end < beg:
            raise ValueError('Trying cutting trace with end < beg')
        sw_inf.time_recorded  = end - beg
        
        if self.get_param('zero_time'):
            sw_inf.t0 = 0
            sw_inf.tend = end - beg
        else:
            sw_inf.t0 = beg
            sw_inf.tend = end
        return sw_inf
    
    def sweep(self, index_sweep, chan = None):
        sweep = self.in_sweep(index_sweep, chan)
        beg = self.get_param('beg')
        end = self.get_param('end')
        end = end if end != 'end' else sweep._data[0,-1]
        beg = beg if beg != 'beg' else sweep._data[0,0]
        b,e = sweep._data[0].searchsorted((beg,end))
        sweep._data = sweep._data[:,b:e]
        return sweep
