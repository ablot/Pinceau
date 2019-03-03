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

class DownSample(node.Node):
    '''Down sample a sweep
    
    reduce the number of data point in sweep from "factor" using "method"
    factor is an int
    method can be mean, direct or maxmin
        mean: replace factor points by their mean, output has len(input)/factor
              points
        direct: take one point every factor, output has len(input)/factor
              points
        maxmin: keep the maximal and minimum value in a window of 2 factors,
              output has len(input)*2/factor points'''
    
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
        
        super(DownSample, self).__init__(name, parent)
        
        self._inputGroups['sweep'] = {'sweep': 'in_sweep', 'numSweeps':
        'in_numSweeps', 'chanNames': 'in_chanNames', 'origin': 'in_origin', 
        'tag': 'in_tag', 'sweepInfo': 'in_sweepInfo'}
        self._outputGroups['sweep'] = {'sweep': 'out_sweep', 'numSweeps': 
        'out_numSweeps', 'chanNames': 'out_chanNames', 'origin': 'out_origin', 
        'tag': 'out_tag', 'sweepInfo': 'out_sweepInfo'}
        
        self._params = {'factor' : 10, 'method' : 'direct', 'memory': None}
        
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
        out = self.in_sweepInfo(index)
        f = self.get_param('factor')
        listUneven = ['median', 'maxmin']
        if self.get_param('method') in listUneven:
            if f%2 ==0: f+=1
        out.numPoints = int(ceil(out.numPoints/float(f)))
        out.dt *= f
        out.tend = out.t0 + (out.numPoints-1) * out.dt
        out.duration = out.t0 - out.tend
        return out
    
    def sweep(self, index_sweep, chan = None, dtype = None):
        if self.get_cache(str(index_sweep)+str(chan)) is not None:
            return self.get_cache(str(index_sweep) + str(chan))
        
        sweep = self.in_sweep(index_sweep, chan, dtype)
        
        base_data = sweep._data
        if self.get_param('method') == 'mean':
            for (i, data) in enumerate(base_data[1:]):
                base_data[i+1] = boxfilter(data, self.get_param('factor'))
            sweep._data = base_data[:,::self.get_param('factor')]
        elif self.get_param('method') == 'median':
            f= int(self.get_param('factor'))
            if f % 2 ==0 : f+=1
            for (i, data) in enumerate(base_data[1:]):
                base_data[i+1] = medfilt(data, f)
            sweep._data = base_data[:,::f]
        elif self.get_param('method') == 'maxmin': 
                f= int(self.get_param('factor'))
                if f % 2 ==0 : f+=1
                out = base_data[0,::self.get_param('factor')]
                for (i, data) in enumerate(base_data[1:]):
                    maxi = order_filter(data, ones(f), f - 1)
                    mini = order_filter(data, ones(f), 0)
                    line = maxi[::self.get_param('factor')]
                    line[::2] = mini[::self.get_param('factor')][::2]
                    #line = vstack((mini[::self.get_param('factor')],
                           #maxi[::self.get_param('factor')]))
                    #line = line.reshape(line.size, order = 'FORTRAN')
                    #ipshell()
                    out = vstack((out,line))
                sweep._data = out
        else:
            if self.get_param('method') != 'direct':
                print 'unknown method in %s, will use direct'%self.name
            sweep._data = base_data[:,::self.get_param('factor')]
        sweep.dt = sweep._data[0][1] - sweep._data[0][0]
        if self.get_param('memory') == 'cache':
            self.set_cache(str(index_sweep)+str(chan), sweep)
        return sweep
