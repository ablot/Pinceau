# -*- coding: utf-8 -*-

from neuropype import node
#from neuropype.datatypes.Sweep import Sweep
#from neuropype.datatypes import Time_list, Sweep
from numpy import logical_and, mean
#from neuropype.ressources._common import boxfilter, findextrema, cross_threshold
import neuropype.ressources.progressbar as pgb
from itertools import imap #, repeat
from neuropype import tag as tagModule

##debuging tool!
#from IPython.Shell import IPShellEmbed
#banner = '\n*** Nested interpreter *** \n\nYou are now in a nested ipython'
#exit_msg = '*** Closing embedded IPython ***'
##paramv = ['-noconfirm_exit', '-pi1','Neuropype In <\\#>:','-pi2','     .\\D.:','-po','Out<\\#>:']
#paramv = ['-pi1','Neuropype In <\\#>:','-pi2','     .\\D.:','-po','Out<\\#>:']
#ipshell = IPShellEmbed(paramv, banner=banner,exit_msg=exit_msg)
##end of debuging tool

class TTE(node.Node):
    '''Warning !!! fullTraceOnly is always True, even if you set it to False
    TODO: decide the policy to use, zero padding, cut trace, mean padding,
    first/last point value padding'''
    
    def __init__(self, name, parent):
        print 'Depreciation warning: Use TTS instead!!'
        self.in_time = node.Input(['Time_list', 'Time'])
        self.in_timenumSweeps = node.Input('int')
        self.in_tag_time_list = node.Input('list')
        
        self.in_sweep = node.Input('Sweep')
        self.in_numSweeps = node.Input('int')
        self.in_chanNames = node.Input('list')
        self.in_origin = node.Input('list')
        self.in_tag_sweep = node.Input('list')
        self.in_sweepInfo = node.Input('SweepInfo')
        
        self.out_numSweeps = node.Output('int')
        self.out_sweep = node.Output('Sweep')
        self.out_chanNames = node.Output('list')
        self.out_origin = node.Output('list')
        self.out_tag = node.Output('list')
        self.out_sweepInfo = node.Output('SweepInfo')

        
        
        super(TTE, self).__init__(name, parent)
        
        self._inputGroups['time_list'] = {'time_list': 'in_time',
        'numSweeps': 'in_timenumSweeps', 'tag': 'in_tag_time_list'}
        self._inputGroups['sweep'] = {'sweep': 'in_sweep', 'numSweeps': 
        'in_numSweeps', 'chanNames': 'in_chanNames', 'origin': 'in_origin',
        'tag': 'in_tag_sweep', 'sweepInfo' : 'in_sweepInfo'}
        self._outputGroups['sweep'] = {'sweep': 'out_sweep', 
        'numSweeps': 'out_numSweeps', 'chanNames': 'out_chanNames',
        'origin': 'out_origin', 'tag': 'out_tag', 'sweepInfo' : 'out_sweepInfo'}
        
        #connecting outputs:
        self.out_numSweeps.output = self.numSweeps
        self.out_sweep.output = self.sweep
        self.out_chanNames.output = self.chanNames
        self.out_origin.output = self.origin
        self.out_tag.output = self.tag
        self.out_sweepInfo.output = self.sweepInfo
        
        self._params = {'chan': 'Ch_0', 'window': [-0.1,0.1], 'zero_time' : 
                        True, 'fullTraceOnly': True, 'graphviz':{'fillcolor':
                       'thistle', 'style': 'filled'}, 'substract_mean': False,
                       'cache':None}

    def _getInSweep(self, index_sweep, chan= None):
        ind = self.get_cache('last_sweep_ind')
        if ind != index_sweep:
            sw = self.in_sweep(index_sweep)
            self.set_cache('last_sweep_ind', index_sweep, force =1)
            self.set_cache('last_sweep', sw, force =1)
        else:
            sw = self.get_cache('last_sweep')
            if sw is None:
                raise ValueError
        if chan is None:
            return sw
        return sw._keepOnlyChan(chan)
    
    def numSweeps(self):
        n = self.get_cache('numSweeps')
        if n is not None:
            return n
        n = 0
        length = self.in_timenumSweeps()
        print 'Detecting spikes in node %s'%self.name
        pbar = pgb.ProgressBar(maxval=length,term_width = 79 ).start()
        for index_time_list in xrange(length):
            j = self.in_time(index_time_list)
            if self.in_time.Type == 'Time':
                index_sweep = j.indexSweep
            else:
                index_sweep = index_time_list
            swInfo = self.in_sweepInfo(index_sweep)
            beg = swInfo.t0
            end = swInfo.tend
            beginvalid = j._data[j._data > beg-self.get_param('window')[0]]
            n_beginspikes = j._data.size - beginvalid.size
            validSpikes = beginvalid[beginvalid < end-self.get_param('window')[1]]
            nspike = validSpikes.size
            #ipshell()
            
            for index in range(nspike):
                index_spike = index + n_beginspikes
                self.set_cache( n+index, (index_sweep, index_spike, index_time_list),
                                force = 1)
            n += nspike
            pbar.update(index_time_list + 1)
        self.set_cache('numSweeps', n, force = 1)
        pbar.finish()
        return n
    
    def sweep(self, index, chan = None):
        if chan is None:
            chan = self.get_param('chan')
        if not isinstance(chan, list):
            chan = [str(chan)]
        
        #chan_index = [self.in_chanNames().index(c)+1 for c in chan]
        #ipshell()
        if self.get_cache('sw_'+str(index)) is not None:
            swp = self.get_cache('sw_'+str(index))
            return swp._keepOnlyChan(chan)
        index_trace, index_spike = self.findFromSpikeIndex(index)
        trace = self._getInSweep(index_trace, chan)
        
        t0 = trace._data[0][0]
        tend = trace._data[0][-1]
        dt = trace._data[0][1] - t0
        
        time_list = self.in_time(index_trace)
        spikeTime = time_list.get_data('s')
        
        #data = trace._data
        #
        #dt = time[1]-time[0]
        #length = int(-round(self.get_param('window')[0]/dt)+round(            \
        #self.get_param('window')[1]/dt))
        st = spikeTime[index_spike]
        data = None
        if (st + self.get_param('window')[0]> t0) & (st + self.get_param( \
        'window')[1] < tend):
            #if spike not at the edge of the sweep
            begin = (st - t0 + self.get_param('window')[0])/dt
            length = ((st - t0 + self.get_param('window')[1])/dt) - begin
            data = trace._data[:,int(begin):int(begin)+int(length)]
        elif not self.get_param('fullTraceOnly'):
            time = data[0]
            data = data[:, logical_and((time>=spikeTime[index_trace] +    \
            self.get_param('window')[0]),(time<= spikeTime[index_trace] + \
            self.get_param('window')[1]))]
        if data is None:
            raise ValueError
        #ipshell()
        #if len(data[0]) != length:
            #return 'Spike not in window'
        if self.get_param('zero_time'):
            data[0]-= data[0][0] - self.get_param('window')[0]
        if self.get_param('substract_mean'):
            data[1:]-= mean(data[1:], axis =1).reshape(data.shape[0]-1,1)
        trace._data = data
        trace.tag = self.tag(index)
        if self.get_param('cache') is not None:
            if self.get_param('cache') == 'all':
                self.set_cache('sw_'+str(index), trace)
            else:
                raise NotImplementedError
        return trace._keepOnlyChan(chan)
    
    def tag(self, index):
        
        #finding tags from inputs
        index_sweep, index_spike = self.findFromSpikeIndex(index)

        sweepTag = self.in_tag_sweep(index_sweep)
        time_listTag = self.in_tag_time_list(index_sweep)
        out = tagModule.combine(sweepTag, time_listTag, AND = 1, OR = 1)
        #adding tag for spike
        tagMg = self.parent.tagManager
        typeName = 'Sweep_index_in_'+self.name
        tagName = 'Sw_'+str(index)
        out.append(tagMg.tagInstance(typeName, tagName, value = index, 
                    universe = int))
        return out
        
    def sweepInfo(self, index):
        ind_of_tlist, ind_in_tlist = self.findFromSpikeIndex(index)
        ind_of_sw = ind_of_tlist
        st = self.in_time(ind_of_tlist)._data[ind_in_tlist]
        out = self.in_sweepInfo(ind_of_sw)
        chanNames = [i.name for i in out.channelInfo]
        chInf = [out.channelInfo[chanNames.index(name)] for name in self.get_param('chan')]
        out.channelInfo = chInf
        win = self.get_param('window')
        out.name = 'Sweep_'+str(index)
        out.duration = win[1] - win[0]
        out.absolute_t0 = out.absolute_t0-st+win[0] if out.absolute_t0 != 'nd' \
                                                    else 'nd'
        out.numPoints = int((win[1] - win[0])/out.dt) if out.dt != 'nd' \
                                                      else 'nd'
        if self.get_param('zero_time'):
            out.t0 = win[0]
            out.tend = win[0]+int(round((win[1] -win[0])/out.dt))*out.dt
        else:
            out.t0 = st + win[0]
            out.tend = st + win[0]+int(round((win[1] -win[0])/out.dt))*out.dt
        return out
        # index_trace, index_time_list = self.findFromSpikeIndex(index)
        # st = self.in_time(index_trace)._data[index_time_list]
        # out = self.in_sweepInfo(index_trace)
        # win = self.get_param('window')
        # out.name = 'Sweep_'+str(index)
        # out.duration = win[1] - win[0]
        # out.absolute_t0 = out.absolute_t0 - st + win[0] if out.absolute_t0 != 'nd' \
        #                                                 else 'nd'
        # out.numPoints = int((win[1] - win[0])/out.dt) if out.dt != 'nd' \
        #                                               else 'nd'
        # if self.get_param('zero_time'):
        #     out.t0 = win[0]
        #     out.tend = win[1]
        # return out
    
    def findSpikeIndexfromSweep(self, sweep_index):
        """Find the index of the first spike of sweep `sweep_index`
        """
        n = 0
        print 'Detecting spikes in node %s'%self.name
        pbar = pgb.ProgressBar(maxval=sweep_index+1, term_width = 79).start()
        iterator = imap(self.in_time, xrange(sweep_index-1))
        
        for (i,j) in enumerate(iterator):
            swInfo = self.in_sweepInfo(i)
            beg = swInfo.t0
            end = swInfo.tend
            temp= j._data
            temp2 = temp[temp > beg-self.get_param('window')[0]]
            n_beginspikes = temp.size-temp2.size
            temp = temp2[logical_and((temp2 > beg-self.get_param('window')  \
            [0]),(temp2 < end-self.get_param('window')[1]))]
            nspike = temp.size
            #ipshell()
            
            for index_spike in range(nspike):
                index_time_list = index_spike + n_beginspikes
                self.set_cache(n+index_time_list, (i, index_time_list), force \
                = 1)
            n += nspike
            pbar.update(i+1)
        pbar.finish()
        return n
        
    
    def findFromSpikeIndex(self, index_spike):
        '''Return the index of the sweep and the index of the spike in this 
        sweep'''
        index = self.get_cache(index_spike)
        if index is not None:
            return index[0], index[1]
        
        tempind = 0
        
        for i in xrange(self.in_timenumSweeps()):
            time_list = self.in_time(i)
            swInfo = self.in_sweepInfo(i)
            beg = swInfo.t0
            end = swInfo.tend
            temp= time_list._data
            length=temp[logical_and((temp > beg - self.get_param('window')\
            [0]),(temp < end - self.get_param('window')[1]))].size
            #length is the number of valid spikes (ie far from the ends)
            if index_spike >= (tempind + length):
                #if it's not in this sweep
                tempind += length #note: add only the # of valid spikes
            else:
                index_trace = i
                n_beginspikes = temp[temp <= beg-self.get_param('window') \
                [0]].size
               
                index_time_list = index_spike - tempind + n_beginspikes
                self.set_cache(index_spike, (index_trace, index_time_list))
                #ipshell()
                return index_trace, index_time_list
    
    def chanNames(self, index_spike = 0):
        #index_trace, index_time_list = self.findFromSpikeIndex(index_spike)
        #return self.in_chanNames(index_trace)
        chan = self.get_param('chan')
        if not hasattr(chan, '__iter__'):
            chan = [chan]
        return chan
    
    def origin(self, index):
        return [str(self.name), str(index)]
