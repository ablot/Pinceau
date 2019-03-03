# -*- coding: utf-8 -*-

from neuropype import node
from neuropype.datatypes.Sweep import Sweep
#from neuropype.datatypes import Time_list, Sweep
from numpy import ones, hstack, arange, mean, array
#from neuropype.ressources._common import boxfilter, findextrema, cross_threshold
from neuropype import parameter
import neuropype.ressources.progressbar as pgb
from itertools import imap, repeat
from neuropype import tag as tagModule
from copy import deepcopy

##debuging tool!
#from IPython.Shell import IPShellEmbed
#banner = '\n*** Nested interpreter *** \n\nYou are now in a nested ipython'
#exit_msg = '*** Closing embedded IPython ***'
##paramv = ['-noconfirm_exit', '-pi1','Neuropype In <\\#>:','-pi2','     .\\D.:','-po','Out<\\#>:']
#paramv = ['-pi1','Neuropype In <\\#>:','-pi2','     .\\D.:','-po','Out<\\#>:']
#ipshell = IPShellEmbed(paramv, banner=banner,exit_msg=exit_msg)
##end of debuging tool

class TTS(node.Node):
    """Time Triggered Snippet return a snippet of sweep corresponding to a
    time_list input
    
    Iterate over a time_list input and return one sweep per spike.
    If the index of the sweep data is not the index of the time_list, connect
    self.in_sweep_index input
    
    Parameters:
    - `chan`: (str or lst of str), Channel of sweep that can be returned
    (is basically a way to 'forget' about the other channels after this node,
    can be removed, but in that case, making cache a bit smarter would be wise)
    
    - `window`: (lst of 2 floats), Part of the sweep to keep around time, in
    seconde, relative to the time (negative value before, postive after)
    
    - `zero_time`: (bool) If True, the time of the output goes from window[0]
    to window[1], else, the time is inchanged
    
    - `partialTraces`: ('Ignore', 'Keep', 'ZeroPad' or 'FlatPad') 
     * `Ignore`, return a sweep only for time where the whole `window` is 
       defined.
     * 'Keep', return troncated sweep where `window` is not defined. 
     * 'ZeroPad', pad with 0 so that every output has the same length, 
     * 'FlatPad', bad with the nearest defined value, or 0 if nothing defined
    
    - `substract_mean`: (bool) If True, center the sweep values on 0
    
    - `cache`: (None, 'all', int) Snippet to keep in cache, if None, don't keep
    if 'all', keep them all, if int, keep the int last used
    
    - `graphviz`: display properties for the graph
    """
    
        
    ## Warning !!! partialTraces is always True, even if you set it to False
    ## TODO: decide the policy to use, zero padding, cut trace, mean padding,
    ## first/last point value padding
    
    def __init__(self, name, parent):
        """constructor doc. See class documentation
        """
        self.in_time = node.Input(['Time_list', 'Time'])
        self.in_timenumSweeps = node.Input('int')
        self.in_tag_time_list = node.Input('list')
        
        self.in_sweep = node.Input('Sweep')
        self.in_numSweeps = node.Input('int')
        self.in_chanNames = node.Input('list')
        self.in_origin = node.Input('list')
        self.in_tag_sweep = node.Input('list')
        self.in_sweepInfo = node.Input('SweepInfo')
        
        self.in_sweep_index = node.Input('int')
        
        self.out_numSweeps = node.Output('int')
        self.out_sweep = node.Output('Sweep')
        self.out_chanNames = node.Output('list')
        self.out_origin = node.Output('list')
        self.out_tag = node.Output('list')
        self.out_sweepInfo = node.Output('SweepInfo')
        
        super(TTS, self).__init__(name, parent)
        
        self._inputGroups['time_list'] = {'time_list': 'in_time',
        'numSweeps': 'in_timenumSweeps', 'tag': 'in_tag_time_list'}
        self._inputGroups['sweep'] = {'sweep': 'in_sweep', 'numSweeps': 
        'in_numSweeps', 'chanNames': 'in_chanNames', 'origin': 'in_origin',
        'tag': 'in_tag_sweep', 'sweepInfo' : 'in_sweepInfo'}
        self._inputGroups['sweep_index'] = {'sweep_index': 'in_sweep_index'}
        
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
        
        #defining parameters:
        partialTraces = parameter.combobox('partialTraces', self, ['Ignore', 
                                      'Keep', 'ZeroPad', 'FlatPad'], 'FlatPad')
        zero_time = parameter.boolean('zero_time', self, True)
        substract_mean = parameter.boolean('substract_mean', self, False)
        self._params = {'chan': 'Ch_0', 
                        'window': [-0.1,0.1], 
                        'zero_time' : zero_time,
                        'partialTraces': partialTraces, 
                        'graphviz': {'fillcolor':'thistle',
                                     'style': 'filled'},
                        'substract_mean': substract_mean,
                        'cache': None}
        
    def _get_input_sweep(self, sweep_index, chan):
        ind = self.get_cache('last_sweep_ind')
        if ind != sweep_index:
            sw = self.in_sweep(sweep_index, chan = self.get_param('chan'))
            self.set_cache('last_sweep_ind', sweep_index, force =1)
            self.set_cache('last_sweep', sw, force =1)
        else:
            sw = self.get_cache('last_sweep')
            if sw is None:
                raise ValueError('Last sweep is None')
        if chan is None:
            return sw
        return sw._keepOnlyChan(chan)
    
    def _validTime(self, index, beg_spikes = None):
        """Return the time_list with valid times (if partialTraces is True it
        can be different from in_time)
        
        Arguments:
        - `index`: (int) index of the time list to consider
        - `beg_spikes`: (None or else) if not None return the number of non
          valid times before the first valid
        """
        in_time = self.in_time(index)
        if self.get_param('partialTraces') != 'Ignore':
            if beg_spikes is not None:
                return (in_time, 0)
            return in_time
        # partialTraces == Ignore
        index_sweep = self.findSweepFromTimeList(index)
        swInfo = self.in_sweepInfo(index_sweep)
        w = self.get_param('window')
        first = swInfo.t0 - w[0]
        last = swInfo.tend - w[1]
        data = in_time._data[:]
        data = data[data > first]
        if beg_spikes is not None:
            n_beginspikes = len(in_time) - data.size
        data = data[data < last]
        in_time._data = data
        if beg_spikes is not None:
            return (in_time, n_beginspikes)
        return in_time
        
    def findSweepFromTimeList(self, index_time_list):
        """Return the index of the sweep corresponding to time_list
        
        Arguments:
        - `index_time_list`: (int) index of the time_list
        """
        if self.inputs['in_sweep_index'] is None:
            return index_time_list
        return self.in_sweep_index(index_time_list)
    
    def findSweepFromSnippet(self, index):
        """return the index of the sweep of snippet `index`
        
        Arguments:
        - `index`: (int) index of the snippet
        """
        
        ind_of_tlist, ind_in_tlist = self.findTimeListFromSnippet(index)
        return self.findSweepFromTimeList(ind_of_tlist)
        
        
    def findSnippetFromTimeList(self, index):
        """Find the index of the first spike of time_list `index_time_list`
        """
        n = 0
        print 'Counting snippets in node %s'%self.name
        pbar = pgb.ProgressBar(maxval= index + 1, term_width = 79).start()
        iterator = imap(self._validTime, xrange(index-1), repeat(True))
        
        for index_time_list, (time_list, n_beginspikes) in enumerate(iterator):
            nspike = len(time_list) #number of valid spikes
            for index_spike in range(nspike):
                index_in_time_list = index_spike + n_beginspikes
                # real index in in_time
                index_snippet = n + index_spike
                self.set_cache(index_snippet, (index_time_list, 
                                               index_in_time_list), force  = 1)
            n += nspike
            pbar.update(index_time_list+1)
        pbar.finish()
        return n
        
    
    def findTimeListFromSnippet(self, snippet_index):
        '''Return the index of the sweep and the index of the spike in this 
        sweep'''
        indices = self.get_cache(snippet_index)
        # indices should be (index of the time_list, index of the snippet in the
        # time list)
        if indices is not None:
            return indices
        
        tempind = 0
        
        for i in xrange(self.in_timenumSweeps()):
            time_list, n_beginspikes = self._validTime(i, beg_spikes = True)
            length = len(time_list)
            if snippet_index >= (tempind + length):
                #if it's not in this sweep
                tempind += length #note: add only the # of valid spikes
            else:
                index_trace = i
                index_time_list = snippet_index - tempind + n_beginspikes
                # index_time_list is the index of the spike in the time_list
                # with all its spike (even if partialTraces is Ignore)
                self.set_cache(snippet_index, (index_trace, index_time_list))
                #ipshell()
                return index_trace, index_time_list
        raise ValueError('I haven\'t found snippet %s'%snippet_index)
        
        
    def numSweeps(self):
        n = self.get_cache('numSweeps')
        if n is not None:
            return n
        n = 0
        length = self.in_timenumSweeps()
        print 'Counting snippets in node %s'%self.name
        pbar = pgb.ProgressBar(maxval=length,term_width = 79 ).start()
        for index_time_list in xrange(length):
            time_list, n_beginspikes = self._validTime(index_time_list, 
                                                       beg_spikes = True)
            nspike = len(time_list)
            for index in xrange(nspike):
                index_spike = index + n_beginspikes
                self.set_cache(n+index, (index_time_list, index_spike), 
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
        
        ind_of_tlist, ind_in_tlist = self.findTimeListFromSnippet(index)
        index_trace = self.findSweepFromTimeList(ind_of_tlist)
        
        #chan_index = [self.in_chanNames().index(c)+1 for c in chan]
        #ipshell()
        if self.get_cache('sw_'+str(index)) is not None:
            data = self.get_cache('sw_'+str(index))
        else:
            trace = deepcopy(self._get_input_sweep(index_trace, None))
            
            time = array(trace._data[0])
            t0 = time[0]
            dt = float(time[1] - t0)
            
            time_list = self.in_time(ind_of_tlist)
            spikeTime = time_list.get_data('s')
            
            st = spikeTime[ind_in_tlist]
            
            w = self.get_param('window')
            length = int(round((w[1] -w[0])/dt))
            indbeg = int(round((st + w[0] - t0)/dt))
            indend = indbeg + length
            lastInd = time.size - 1
            
            if indbeg >= 0 and indend < time.size:
                #trace is full
                data = trace._data[:,indbeg:indend]
            else:
                policy = self.get_param('partialTraces')
                if policy == 'Ignore':
                    raise IOError('Got a partial spike index with `Ignore`')
                if policy == 'Keep':
                    if indbeg < 0:
                        indbeg = 0
                    if indend > lastInd:
                        indend = lastInd
                    data = trace._data[:,indbeg:indend]
                else:
                    data = self._createPadArrays(trace._data, indbeg, indend)
                    
            # setting time:
            data[0] = arange(length)*dt + w[0]
            if not self.get_param('zero_time'):
                data[0] += st
                
            #reseting mean if needed:
            if self.get_param('substract_mean'):
                data[1:] -= mean(data[1:], axis = 1)
            self._cacheSnippet(data, index)
        
        # trace._data = data
        # trace.tag = self.tag(index)
        swInf = self.in_sweepInfo(index_trace)
        chName = [c.name for c in swInf.channelInfo]
        
        chInf = [swInf.channelInfo[chName.index(i)] for i in chan]
        chInd = [self.get_param('chan').index(i)+1 for i in chan]
        data = data[[0]+chInd,:]
        out = Sweep('Snippet_'+str(index), data, chInf, self.tag(index))
        return out
    
    def _createPadArrays(self, data, indbeg, indend):
        """creating arrays used for padding
        
        Arguments:
        - `data`: array to pad
        - `indbeg`: index of first value we'd like
        - `indend`: index of last value we'd like
        """
        #creating pad arrays
        ndim, nvalues = data.shape
        lastInd = nvalues - 1
        if nvalues == 0:
            # no data, return ones
            return ones((ndim,indend-indbeg))
        
        if indbeg < 0:
            padBeg = ones((ndim, -indbeg))
            indbeg = 0
        else:
            padBeg = ones((ndim, 0))
        n = indend - lastInd
        
        if n > 0:
            padEnd = ones((ndim, n))
            indend = lastInd
        else:
            padEnd = ones((ndim, 0))
        
        policy = self.get_param('partialTraces')
        
        # populating pad arrays
        if policy == 'ZeroPad':
            out = data[:,indbeg:indend]
            out = hstack((padBeg*0, out, padEnd*0))
        elif policy == 'FlatPad':
            firsts = array(data[:,indbeg], ndmin = 2).T
            lasts = array(data[:,indend], ndmin = 2).T
            if padBeg.size != 0: padBeg *= firsts
            if padEnd.size != 0: padEnd *= lasts
            out = data[:,indbeg:indend]
            out = hstack((padBeg, out, padEnd))
        else:
            raise NotImplementedError('%s is not a valid policy'%policy)
        return out
    
    def _cacheSnippet(self, trace, index):
        """put a snippet in cache according to policy
        
        Arguments:
        - `trace`: snippet to cache
        - `index`: index of this snippet
        """
        policy = self.get_param('cache')
        if policy is None:
            return
        elif policy == 'all':
            self.set_cache('sw_'+str(index), trace)
            return
        elif isinstance(policy, int):
            lst_cached = self.get_cache('cached_sw')
            if lst_cached is None:
                lst_cached = [index]
            else:
                while len(lst_cached) >= policy:
                    ind = lst_cached.pop(0)
                    self._cache.pop['sw_'+str(ind)]
            lst_cached.append(index)
            self.set_cache('sw_'+str(index), trace)
            return
        
    def tag(self, index):
        
        #finding tags from inputs
        ind_of_tlist, ind_in_tlist = self.findTimeListFromSnippet(index)
        ind_of_sw = self.findSweepFromTimeList(ind_of_tlist)
        sweepTag = self.in_tag_sweep(ind_of_sw)
        time_listTag = self.in_tag_time_list(ind_of_tlist)
        out = tagModule.combine(sweepTag, time_listTag, AND = 1, OR = 1)
        #adding tag for spike
        tagMg = self.parent.tagManager
        typeName = 'Sweep_index_in_'+self.name
        tagName = 'Sw_'+str(index)
        out.append(tagMg.tagInstance(typeName, tagName, value = index, 
                    universe = int))
        return out
        
    def sweepInfo(self, index):
        ind_of_tlist, ind_in_tlist = self.findTimeListFromSnippet(index)
        ind_of_sw = self.findSweepFromTimeList(ind_of_tlist)
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
    
        
    def chanNames(self, index_spike = 0, tag = None):
        chan = self.get_param('chan')
        if not hasattr(chan, '__iter__'):
            chan = [chan]
        return chan
    
    def origin(self, index, tag = None):
        ind_of_tlist, ind_in_tlist = self.findTimeListFromSnippet(index)
        ind_of_sw = self.findSweepFromTimeList(ind_of_tlist)
        origin = self.in_origin(ind_of_sw)
        return origin + [str(self.name)+'_Sw_'+ str(index)]
