# -*- coding: utf-8 -*-

from neuropype import node
from neuropype.datatypes import Sweep
import numpy as np
from itertools import imap
from neuropype.ressources._common import filterValues

##debuging tool!
#from IPython.Shell import IPShellEmbed
#banner = '\n*** Nested interpreter *** \n\nYou are now in a nested ipython'
#exit_msg = '*** Closing embedded IPython ***'
##paramv = ['-noconfirm_exit', '-pi1','Neuropype In <\\#>:','-pi2','     .\\D.:','-po','Out<\\#>:']
#paramv = ['-pi1','Neuropype In <\\#>:','-pi2','     .\\D.:','-po','Out<\\#>:']
#ipshell = IPShellEmbed(paramv, banner=banner,exit_msg=exit_msg)
##end of debuging tool

import neuropype.ressources.progressbar as pgb

class FilterValue(node.Node):
    '''filter a sweep output
    
    listOfCond is a list of tuple with the name of the property, the condition,
    the value, the channel and the time
    
    property can be:
    max, min, sd, std, cv, sw_ind
    
    condition can be 0 for inferior to, 1 for superior to, 'in', or 'out' to select a
         window of value and 'among' to keep only specific values
    value is a float if comp is 0 or 1 and a doublet of float if comp is 'in' or
         'out', a list of values if comp is 'among'    
    chan is a list of channel names, if nothing is set, check cond on all the 
         channels
    time is a list [time_min, time_max], and condition is check only on this 
    window. If nothing is set, check cond one the whole trace'''
    
    def __init__(self, name, parent):
        
        self.in_sweep = node.Input(['Sweep', 'SweepData'])
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
        
        super(FilterValue, self).__init__(name, parent)
        self._inputGroups['sweep'] = {'sweep': 'in_sweep', 'numSweeps': 
        'in_numSweeps', 'chanNames': 'in_chanNames', 'origin': 'in_origin', 
        'tag': 'in_tag', 'sweepInfo': 'in_sweepInfo'}
        self._outputGroups['sweep'] = {'sweep': 'out_sweep', 'numSweeps': 
        'out_numSweeps', 'chanNames': 'out_chanNames', 'origin': 'out_origin',
        'tag': 'out_tag', 'sweepInfo': 'out_sweepInfo'}
        
        self._params={'listOfCond':None, 'tag' : None}
        
        #connecting outputs:
        self.out_numSweeps.output = self.numSweeps
        self.out_chanNames.output = self.chanNames
        self.out_sweep.output = self.sweep
        self.out_origin.output = self.origin
        self.out_tag.output = self.tag
        self.out_sweepInfo.output = self.sweepInfo
        
        #create tag instance
        self.parent.tagManager.add_tagType(self.name)
    
    def isValid(self, index_sweep):
        listOfCond = self.get_param('listOfCond')
        if self.get_param('tag') is not None:
            tag = self.get_param('tag')
            if not isinstance(tag, list):
                tag = [tag]
            for tagType, tagValue in tag:
                #ipshell()
                if not isinstance(tagValue, list):
                    tagValue = [tagValue]
                current_tag = self.in_tag(index_sweep)
                type_name = [type(i).__name__ for i in current_tag]
                if tagType not in  type_name:
                    return False
                    
                current_values = current_tag[type_name.index(tagType)].value
                if not any([i in tagValue for i in current_values]):
                    #if current_values don't include one tag defined in tagValue
                    return False
        if listOfCond is None:
            return True
        
        in_sw = self.in_sweep(index_sweep)
        
        if not isinstance(listOfCond, list):
            listOfCond = [listOfCond]
        
        for cond in listOfCond:
            if cond[0] == 'sw_ind':
                val = index_sweep
            else:
                val = self._findVal(cond, in_sw, index_sweep)
                
            if not filterValues(val, cond[1],cond[2]):
                return False
        return True
    
    def _findVal(self, cond, in_sw, index_sweep):
        time = None
        if len(cond) == 3:
            prop, comp, value = cond
            chan = self.in_chanNames(index_sweep)
        elif len(cond) == 4:
            prop, comp, value, chan = cond
            if not isinstance(chan, list):
                chan =[chan]
        elif len(cond) == 5:
            prop, comp, value, chan, time = cond
            if not isinstance(chan, list):
                chan =[chan]
            time = [float(i) for i in time]
        else:
            raise IOError('Condition can only have 3, 4 or 5 elements')
        
        chanInd = [in_sw._name2index[name] for name in chan]
        if time is None:
            beg = 0
            end = in_sw._data.shape[1]
        else:
            if self.in_sweep.source.Type == 'Sweep':
                t0 = in_sw._data[0][0]
                dt = in_sw._data[0][1] - t0
            else:
                swinf = self.sweepInfo(index_sweep)
                t0 = swinf.t0
                dt = swinf.dt
            beg = int(round((time[0] - t0)/dt))
            end = int(round((time[1] - t0)/dt))
        relative = False
        if prop[0] == 'r':
            prop = prop[1:]
            relative = True
        val = getattr(in_sw._data[chanInd,:][:,beg:end], prop)
        if hasattr(val, '__call__'):
            val = val()
        if relative:
            val -= in_sw._data[chanInd,:][:,beg:end].mean()
        return val
        
    def eqIndex(self, index):
        '''find the index in the input corresponding'''
        eqInd = self.get_cache(index)
        if eqInd is not None:
            return eqInd
        
        n = 0
        nValid = 0
        while nValid <= index:
            if self.isValid(n):
                self.set_cache(nValid, n, force = 1)
                nValid += 1
            n+=1
        return n - 1 #-1 cause n is the number of sweep, we want the index
    
    def sweep(self, index, chan = None):
        sw= self.in_sweep(self.eqIndex(index), chan)
        sw.tag = self.tag(index)
        return sw
        
    def sweepInfo(self, index):
        return self.in_sweepInfo(self.eqIndex(index))
    
    def tag(self, index):
        base = self.in_tag(self.eqIndex(index))
        return base + [self.parent.tagManager.tagInstance(self.name, 'Tag_%s'%index, True)]
    
    def chanNames(self, index = 0):
        return self.in_chanNames(self.eqIndex(index))
    
    def origin(self, index):
        return self.in_origin(self.eqIndex(index))
    
    def numSweeps(self):
        nsweeps = self.get_cache('nsweeps')
        if nsweeps is not None:
            return nsweeps
        
        print 'Counting valid sweeps in %s ...'%self.name
        pbar = pgb.ProgressBar(maxval=self.in_numSweeps(), 
        term_width = 79).start()
        n=0
        nsweeps = 0
        for i in range(self.in_numSweeps()):
            isValid = self.isValid(i)
            n+=1
            if isValid:
                self.set_cache(nsweeps, i, force = 1)
                nsweeps += 1
            pbar.update(n)
        pbar.finish()
        self.set_cache('nsweeps', nsweeps)
        return nsweeps
    
    
    def indexOutfromIn(self, index_sweep):
        '''Return the index of the out_sweep corresponding to index_seep of 
        in_sweep, if in_sweep(index_sweep) is not valid, return the index of the first
        valid sweep before, None if there is no valid sweep before index_sweep'''
        if self.get_param('tag') is None and self.get_param('listOfCond') is None:
            return index_sweep
        if self.numSweeps() == 0:
            return None
        i = 0
        #print index_sweep
        #print '__________________'
        while i < self.numSweeps():
            #print i
            ind = self.eqIndex(i)
            if  ind < index_sweep:
                i +=1
            elif ind == index_sweep:
                return i
            else: #ind > index_sweep
                return i - i
        return i - 1
 
