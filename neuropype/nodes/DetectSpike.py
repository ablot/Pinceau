# -*- coding: utf-8 -*-

try:
    import mdp
    use_mdp = True
except ImportError:
    print 'mdp (modular data processing) module not installed. Cannot do PCA'
    use_mdp = False
import numpy as np
from neuropype import node
from itertools import imap, repeat
from copy import deepcopy, copy
from neuropype import parameter
import os

from bisect import bisect_left
from neuropype.ressources._common import boxfilter, findextrema, cross_threshold
from neuropype.ressources._common import flatenList, filterValues
import neuropype.ressources.progressbar as pgb
from neuropype.datatypes import Time_list, Sweep
from neuropype.gui.lassoExempl import  LassoManager

class DetectSpike(node.Node):
    """Detect events in a sweep
    
    
    
    * filter is a list of 4-tuples, (sniptype, property, comp, value)
             sniptype can be 'raw' or 'filtered',
             property can be any of the 'props' param or one PCA componant,
             comp can be 0 -- for < --, 1 -- for > --, 'in' or 'out',
             if comp is 0 or 1, value is a float
             if comp is 'in' or 'out', value must be a list of 2 floats,
             defining the window to keep/exclude"""
    def __init__(self, name, parent):
        # Inputs
        self.in_sweep = node.Input(['Sweep', 'SweepData'])
        self.in_numSweeps = node.Input('int')
        self.in_chanNames = node.Input('list')
        self.in_origin = node.Input('list')
        self.in_tag = node.Input('list')
        self.in_sweepInfo = node.Input('SweepInfo')
        
        # Outputs
        self.out_time = node.Output('Time_list')
        self.out_numSweeps = node.Output('int')
        self.out_sweep = node.Output('Sweep')
        self.out_chanNames = node.Output('list')
        self.out_origin = node.Output('list')
        self.out_tagTimeList = node.Output('list')
        self.out_sweepInfo = node.Output('SweepInfo')
        self.out_numSpikes = node.Output('int')
        
        self.out_snip_tag = node.Output('list')
        self.out_snip_sweepInfo = node.Output('SweepInfo')
        self.out_snip = node.Output('Sweep')
        self.out_snip_origin = node.Output('list')
        self.out_snip_chanNames = node.Output('list')
        
        super(DetectSpike, self).__init__(name, parent)
        self._inputGroups['sweep'] = {'sweep': 'in_sweep',
                                      'numSweeps': 'in_numSweeps',
                                      'chanNames': 'in_chanNames',
                                      'origin': 'in_origin',
                                      'tag' : 'in_tag',
                                      'sweepInfo': 'in_sweepInfo'}
        
        self._outputGroups = {'time_list':  {'time_list': 'out_time',
                                             'numSweeps': 'out_numSweeps',
                                             'tag': 'out_tagTimeList'},
                              'filteredSweep': {'sweep': 'out_sweep',
                                                'numSweeps': 'out_numSweeps',
                                                'chanNames': 'out_chanNames',
                                                'origin': 'out_origin',
                                                'tag': 'out_tagTimeList',
                                                'sweepInfo': 'out_sweepInfo'},
                              'snippet': {'sweep': 'out_snip',
                                          'numSweeps': 'out_numSpikes',
                                          'chanNames': 'out_snip_chanNames',
                                          'origin': 'out_snip_origin',
                                          'tag': 'out_snip_tag',
                                          'sweepInfo': 'out_snip_sweepInfo'}}
        # Default parameters:
        baseline = parameter.combobox('baseline', self, ['fixed', 'floating', 
                                      'mean', 'window', None], 'floating')
        fixed_baseline = parameter.float_param('fixed_baseline', self, 0, decimals= 9,
                                               singleStep= 1e-3)
        createUniv = CreateUniv(self)
        self.cU = createUniv
        
        chan = parameter.combobox('chan', self, [], 'None', func = createUniv)
        padding = parameter.combobox('padding', self, ['flatPad', 'zeroPad', 'keep'], 'flatPad')
        win0 = parameter.float_param('win0', self, 5e-3, minVal= 0, decimals= 9,
                                     singleStep= 1e-3)
        win1 = parameter.float_param('win1', self, 1e-3, minVal= 0, decimals= 9,
                                     singleStep= 1e-3)
        win2 = parameter.float_param('win2', self, 1.5e-3, minVal= 0, decimals=
                                     9, singleStep= 1e-3)
        dt0 = parameter.float_param('dt0', self, 1.5e-3, minVal= 0, decimals=
                                     9, singleStep= 1e-3)
        dt1 = parameter.float_param('dt1', self, 1.5e-3, minVal= 0, decimals=
                                     9, singleStep= 1e-3)
        pointinterval = parameter.float_param('pointinterval', self, 1e-3, minVal= 0, decimals=
                                     9, singleStep= 0.1e-3)
        numWins = parameter.integer('numWins', self, 1, minVal= 1, maxVal= 3)
        threshold = parameter.float_param('threshold', self, 0, decimals=
                                     9, singleStep= 1e-3)
        maximum = parameter.boolean('maximum', self, Default = True)
        upwards = parameter.boolean('upwards', self, Default = True)
        cross_threshold_param = parameter.boolean('cross_threshold', self, Default = False)
        
        self._params={'chan': chan,
                      'maximum': maximum,
                      'upwards': upwards,
                      'threshold': threshold, 
                      'cross_threshold': cross_threshold_param,
                      'pointinterval': pointinterval,
                      'baseline' : baseline,
                      'verbose' : 1,
                      'numWins': numWins,
                      'win0': win0,
                      'win1' : win1,
                      'win2' : win2,
                      'dt0' : dt0,
                      'dt1' : dt1,
                      'baseline_window': ['begin', 'end'],
                      'fixed_baseline': fixed_baseline,
                      'memory': 'store',
                      'snip_window' : [-2e-3,2e-3],
                      'props' :['sw_ind', 'max', 'min', 'median', 'mean',
                                'ptp', 'std', 'sum'],
                      'snip_memory' : ('store', 'all'),
                      'filter':[],
                      'padding': padding,
                      'graphviz':{'style': 'filled', 'fillcolor': 
                                  'lightyellow'}}
        #connecting outputs:
        self.out_time.output = self.time_list
        self.out_numSweeps.output = self.numSweeps
        self.out_chanNames.output = self.chanNames
        self.out_sweep.output = self.filteredSweep
        self.out_origin.output = self.origin
        self.out_tagTimeList.output = self.tag
        self.out_sweepInfo.output = self.sweepInfo
        self.out_numSpikes.output = self.numSpikes
        self.out_snip_tag.output = self.snip_tag
        self.out_snip.output = self.snippet
        self.out_snip_origin.origin = self.snippet_origin
        self.out_snip_sweepInfo.origin = self.snippet_sweepInfo
        self.out_snip_chanNames.output = self.snippet_chanNames
        
    def _ready_trace(self, data, time, debug = 0):
        '''do the filtering'''
        f0, f1, f2, dt0, dt1 = None, None, None, None, None
        dtype = None
        if data.dtype == 'int':
            dtype = data.dtype
            data = np.asarray(data, dtype ='float64')
        dt = float(time[1]-time[0])
        
        #substracting baseline:
        baseline = self.get_param('baseline')
        if baseline == 'window':
            if self.get_param('baseline_window')[0] == 'begin': 
                beg =0
            else: 
                baseline_window0 = float(self.get_param('baseline_window')[0])
                beg  = bisect_left(time, baseline_window0)
            if self.get_param('baseline_window')[1] == 'end':
                end = -1
            else: 
                baseline_window1 = float(self.get_param('baseline_window')[1])
                end = bisect_left(time,baseline_window1)
            baseline = np.mean(data[beg:end])
            data-=baseline
        elif baseline == 'fixed':
            baseline = float(self.get_param('fixed_baseline'))
            data-=baseline
        elif baseline == 'floating':
            numWins = self.get_param('numWins')
            cumsum = data.cumsum()
            win0 = int(self.get_param('win0')/dt)
            biggestWin = win0
            f0 = boxfilter(data, win0, cumsum)
            if numWins==1:
                #simply substract baseline
                data-=f0
            else:
                #kind of first order derivative
                dt0=int(float(self.get_param('dt0')/dt))
                if dt0 == 0: dt0 = 1
                win1 = int(self.get_param('win1')/dt)
                biggestWin = max(win1, biggestWin)
                f1 = boxfilter(data, win1, cumsum)
                if numWins==2:
                    data = np.zeros_like(data)
                    data[dt0/2:-dt0/2] = f1[dt0:] - f0[:-dt0]
                elif numWins==3:
                    #kind of 2nd order derivative
                    win2 = int(self.get_param('win2')/dt)
                    biggestWin = max(win2, biggestWin)
                    dt1=int(float(self.get_param('dt1')/dt))
                    if dt1 == 0: dt1=1
                    f2 = boxfilter(data, win2, cumsum)
                    data = np.zeros_like(data)
                    data[dt1/2:-dt1/2] = f2[dt1:]-2*f1[dt0:-dt1+dt0]-f0[:-dt1]
                else:
                    raise ValueError('wrong numWins: %s'%numWins)
            padding = self.get_param('padding')
            if padding == 'zeroPad':
                data[:biggestWin] = np.zeros(biggestWin)
                data[-biggestWin:] = np.zeros(biggestWin)
            elif padding == 'flatPad':
                data[:biggestWin] = np.ones(biggestWin)*data[biggestWin]
                data[-biggestWin:] = np.ones(biggestWin)*data[biggestWin]
                
        elif baseline == 'mean':
            baseline=np.mean(data)
            data-=baseline
        if dtype is not None:
            data = np.asarray(data, dtype = dtype)
        if debug:
            return data, f0, f1, f2, dt0, dt1
        return data
        
    def _detect(self, trace, time):
        '''Do the detection on trace, delete values in pointinterval and 
        return the other'''
        params = self.params
        dt=time[1]-time[0]
        pointinterval=int(float(params['pointinterval']/dt))
        
        if not params['cross_threshold']:
            temp = findextrema(trace, params['maximum'], params['threshold'], 
                               pointinterval)
        else:
            temp = cross_threshold(trace, params['upwards'], params['maximum'],
                                   params['threshold'], pointinterval)
        
        out = np.array([time[i] for i in temp])
        return out
    def _spikeTimes(self, index_sweep):
        '''Return the list of spike times detected in sweep 'index_sweep' '''
                
        if self.get_param('memory') == 'write':
            data, dataTot = None, None
            path = self.get_cache('path')
            if path is not None:
                dataTot = np.load(path)
                if 'Sw_'+str(index_sweep) in dataTot.files:
                    data = dataTot['Sw_'+str(index_sweep)]
                    
        
        elif self.get_param('memory') == 'store':
            if not self._cache.has_key('sp_times'): self._cache['sp_times']={}
            data = self._cache['sp_times'].get(index_sweep)
        elif self.get_param('memory') is None:
            data = None
        else:
            print 'param %s for memory not '%self.get_param('memory') + \
                  'recognised, won\'t memorise anything'
            data = None
        
        if data is None:
            sweep = self._get_input_sweep(index_sweep)
            time = self._get_time(index_sweep)
            swdata = sweep._data[1] if sweep._data.shape[0]>1 else sweep._data[0]
            trace = self._ready_trace(deepcopy(swdata), time)
            data = self._detect(trace, time)
            
            if self.get_param('memory') == 'store':
                self._cache['sp_times'][index_sweep] = data
            elif self.get_param('memory') == 'write':
                if dataTot is not None:
                    temp = {}
                    for  i in dataTot.files:
                        temp[i]= dataTot[i]
                    temp['Sw_'+str(index_sweep)] = data
                else:
                    temp = {'Sw_'+str(index_sweep) : data}
                path = self.parent.home + self.parent.name + '_' +self.name + \
                       '_spikeTimes.npz'
                
                np.savez(path, **temp)
                self.set_cache('path', self.parent.home + self.parent.name +
                                '_' + self.name + '_spikeTimes.npz', force = 1)
                dataTot.close()
            
            # if self.get_param('snip_memory') is not None:
            #     snippet = self._extract_snippet(data, sweep._data[1], time)
            #     self._saveSnip(index_sweep, snippet, 'raw')
            #     snippet = self._extract_snippet(data, trace, time)
            #     self._saveSnip(index_sweep, snippet, 'filtered')
                                
        return data
    def all_times(self, list_sweep=None, groupbysweep=False, keepMasked = False):
        out = []
        
        if list_sweep is None:
            list_sweep = xrange(self.numSweeps())
        
        if not keepMasked:
            mask = self._mask()
        
        for i, sweep in enumerate(list_sweep):
            data = self._spikeTimes(sweep)
            if not keepMasked:
                b0, b1 = self._sweepBorder(sweep)
                data = data[mask[b0: b1]]
            out.append(data)
        if not groupbysweep:
            out = flatenList(out)
        return out          
        
    def ISI(self,list_sweep=None, groupbysweep=False, keepMasked = False):
        out = []
        
        if list_sweep is None:
            list_sweep = xrange(self.numSweeps())
        
        if not keepMasked:
            mask = self._mask()
        
        for i, sweep in enumerate(list_sweep):
            data = self._spikeTimes(sweep)
            if not keepMasked:
                b0, b1 = self._sweepBorder(i)
                data = data[mask[b0: b1]]
            out.append(np.diff(data))
        if not groupbysweep:
            out = flatenList(out)
        return out          
        
    def time_list(self, index_sweep, keepMasked = False):
        sp_times = self._spikeTimes(index_sweep)
        if not keepMasked:
            b0, b1 = self._sweepBorder(index_sweep)
            mask = self._mask()[b0:b1]
            sp_times = sp_times[mask]
        name = 'SpikesOfSweep'+str(index_sweep)
        origin = self.in_origin(index_sweep)+ [str(self.get_param('chan'))]
        out = Time_list.Time_list(name, sp_times, origin, SweepIndex = index_sweep,
                                  nodeOfSweep = self, title = 'NoTitle', units
                                  = 's')
        out.tag = self.tag(index_sweep)
        return out
        
    def findOriginFromIndex(self, index, keepMasked = False):
        """return the index of the sweep and the spike in that sweep
        corresponding to spike index"""
        tempind = 0
        func = self._spikeTimes if keepMasked else self.time_list
        if not keepMasked:
            for i in xrange(self.in_numSweeps()):
                length = len(self.time_list(i))
                if index >= (tempind + length):
                    #if it's not in this sweep
                    tempind += length #note: add only the # of valid spikes
                else:
                    index_trace = i
                    index_time_list = index - tempind
                    # index_time_list is the index of the spike in the time_list
                    # with all its spike (even if partialTraces is Ignore)
                    
                    return index_trace, index_time_list
            raise ValueError('I haven\'t found snippet %s'%index)
        else:
            borders =  self._borders()
            sortedSecondIndex = [borders[i][1] for i in range(self.in_numSweeps())]
            index_trace = np.searchsorted(sortedSecondIndex, index)
            if index_trace == 0:
                return index_trace, index
            if index_trace >= len(sortedSecondIndex):
                raise ValueError('I haven\'t found snippet %s'%index)
            index_time_list = index - sortedSecondIndex[index_trace - 1]
    def _sweepBorder(self, index, borderbefore = None):
        """index of first and last spikes of sweep in numSpikes"""
        if not self._cache.has_key('borders'): self._cache['borders'] = {}
        bord = self._cache['borders']
        out = bord.get(index)
        if out is not None:
            return out
        if borderbefore is None:
            out = (self.findSpikeFromSweep(index, True), 
                   self.findSpikeFromSweep(index+1, True))
        else:
            out = (borderbefore[1], self._spikeTimes(index).size+borderbefore[1])
        bord[index] = out
        return out
    def _borders(self):
        borderbefore = None
        for i in range(self.numSweeps()):
            borderbefore = self._sweepBorder(i, borderbefore)
        return self.get_cache('borders')
    def numSpikes(self, list_sweep = None, keepMasked = False, verbose =1):
        """Count the number of spikes in list_sweep.
        
        if list_sweep is None, count on all the sweeps,
        if countMaskedSpikes, count the spikes before applying filter"""
        if list_sweep is None:
            list_sweep = xrange(self.numSweeps())
        elif not list_sweep:
            return 0
        if not hasattr(list_sweep, '__iter__'):
            list_sweep = [int(list_sweep)]
        if keepMasked:
            iterator = imap(self._spikeTimes, list_sweep)
        else:
            iterator = imap(self.time_list, list_sweep, repeat(False))
        if verbose:
            print 'numSpikes in %s:'%self.name
            pbar = pgb.ProgressBar(maxval=len(list_sweep), 
                                           term_width = 79).start()
        n=0
        nspikes=len(iterator.next())
        for i in iterator:
            n+=1
            nspikes += len(i)
            if verbose: pbar.update(n)
        if verbose: pbar.finish()
        return nspikes
    def findSpikeFromSweep(self, index, keepMasked = False):
        return self.numSpikes(range(index), keepMasked, verbose = 0)
    def _extract_snippet(self, sp_times, trace, time):
        if not sp_times.size:
            return np.array([])
        
        win0, win1 = self.get_param('snip_window')
        
        beg = time.searchsorted(sp_times + win0)
        end = time.searchsorted(sp_times + win1)
        midl = time.searchsorted(sp_times)
        length = int(np.ceil((win1-win0)/(time[1]-time[0])))
        # ceil and have the smallest window that include totally the interval
        out = np.zeros((len(beg), length), dtype = trace.dtype)
        for i ,(s, b,e) in enumerate(zip(midl, beg, end)):
            if e - b == length:
                out[i] = trace[b:e]
            else:
                border0 = int(length/2)
                if s - b > border0 or border0+e -s > length:
                    raise ValueError('ca bug')
                out[i, border0 - (s - b): border0 + (e-s)] = trace[b:e]
                out[i, :border0 - (s - b)]=trace[b]
                out[i, border0 + (e-s):] = trace[max(0,e-1)]
                #minus 1 cause e can be len(trace)
        return out
    def _saveSnip(self, index_sweep, snippet, sniptype):
        snip_memory = self.get_param('snip_memory')
        if snip_memory[0] != 'store':
            return
        if snip_memory[1] != 'all':
            saved = self.get_cache('snippet_'+sniptype)
            if saved is None: saved = {}
            if saved.has_key(index_sweep):
                return
            saved_index = self.get_cache('snippet_index_'+sniptype)
            if saved_index is None: saved_index = []
            if isinstance(snip_memory[1], int): 
                while len(saved_index) >= snip_memory:
                    first = saved_index.pop(0)
                    saved.pop(first)
            elif snip_memory[1] != 'all':
                return
            saved_index.append(index_sweep)
            saved[index_sweep] = snippet
            self.set_cache('snippet_'+sniptype, saved, force =1)
            self.set_cache('snippet_index_'+sniptype, saved_index, 
                           force =1)
        else:
            if not self._cache.has_key('snippet_'+sniptype):
                out = np.zeros((self.numSpikes(keepMasked = True),
                                snippet.shape[1]),
                               dtype = snippet.dtype)
                self._cache['snippet_'+sniptype] = out
                
            if not self._cache.has_key('snippet_index_'+sniptype):
                out = np.zeros(self.numSpikes(keepMasked=True), dtype = 'bool')
                self._cache['snippet_index_'+sniptype] = out
            
            b0, b1 = self._sweepBorder(index_sweep)
            self._cache['snippet_'+sniptype][b0:b1,:] = snippet
            self._cache['snippet_index_'+sniptype][b0:b1] = np.ones(b1-b0, 
                                                                dtype = 'bool')
    def _extract_one_sweep(self, index_sweep, sniptype):
        time = self._get_time(index_sweep)
        spike = self._spikeTimes(index_sweep)
        if not spike.size:
            return None
        sweep = self._get_input_sweep(index_sweep)
        sweep = sweep._data[1] if sweep._data.shape[0]>1 else sweep._data[0]
        if sniptype == 'filtered':
            sweep = self._ready_trace(sweep, time)
        elif sniptype != 'raw':
            raise ValueError('Unknown sniptype: %s'%sniptype)
        snip = self._extract_snippet(spike, sweep, time)
        return snip
        
    def _extract_all_snippet(self, sniptype):
        print 'extracting %s snippets in %s'%(sniptype, self.name)
        pbar = pgb.ProgressBar(maxval=self.numSweeps(), term_width = 79).start()
        for index_sweep in range(self.in_numSweeps()):
            snip = self._extract_one_sweep(index_sweep, sniptype)
            if snip is None:
                continue
            self._saveSnip(index_sweep, snip, sniptype)
            pbar.update(index_sweep)
        pbar.finish()
    def _getSnip(self, listindex, sniptype):
        
        if not isinstance(listindex, list):
            listindex = [int(listindex)]
        
        snip_memory = self.get_param('snip_memory')
        
        if snip_memory is not None and snip_memory[0] == 'store':
            if snip_memory[1] == 'last_sweep':
                arg_sort = np.argsort(listindex)
                saved_ind = self.get_cache('last_sweep_snip_ind_'+sniptype)
                saved = self.get_cache('last_sweep_snip_'+sniptype)
                if saved is None or saved_ind is None:
                    saved = []
                    saved_ind = []
                out = []
                for arg in arg_sort:
                    try:
                        ind = saved_ind.index(listindex[arg_sort])
                        out.append(saved[ind])
                    except ValueError:
                        index_sweep, indSpinSw = self.findOriginFromIndex(listindex[arg_sort], keepMasked = 1)
                        time = self._get_time(index_sweep)
                        spike = self._spikeTimes(index_sweep)
                        sweep = self._get_input_sweep(index_sweep)
                        sweep = sweep._data[1] if sweep._data.shape[0]>1 else sweep._data[0]
                        if sniptype == 'filtered':
                            sweep = self._ready_trace(sweep, time)
                        snip = self._extract_snippet(spike, sweep, time)
                        snipinds = np.arange(*self._borders()[index_sweep])
                        self.set_cache('last_sweep_snip_ind_'+sniptype, snipinds)
                        self.set_cache('last_sweep_snip_'+sniptype, snip)
                        out.append[snip[indSpinSw]]
                return out
                # out = {}
                # sweep_saved = self.get_cache('snippet_'+sniptype)
                # if not sweep_saved is None:
                #     for i in listindex:
                #         swind, spind = self.findOriginFromIndex(i)
                #         not_saved = []
                #     for i in list_index:
                #         sweep
                #         saved_ind =[i for i in listindex if i in sweep_saved]
            elif snip_memory[1] == "all":
                inds = self.get_cache('snippet_index_'+sniptype)
                if inds is None or any([not inds[i]  for i in listindex]):
                    self._extract_all_snippet(sniptype)
                return np.array(self._cache['snippet_'+sniptype][listindex,:])
            else:
                raise NotImplementedError()
                
        elif snip_memory is not None:
            raise NotImplementedError()
        
        out = None
        
        for index_snip in listindex:
            index_sweep, indSpinSw = self.findOriginFromIndex(index_snip, keepMasked = 1)
            time = self._get_time(index_sweep)
            spike = self._spikeTimes(index_sweep)
            if not spike.size:
                continue
            sweep = self._get_input_sweep(index_sweep)
            sweep = sweep._data[1] if sweep._data.shape[0]>1 else sweep._data[0]
            if sniptype == 'filtered':
                sweep = self._ready_trace(sweep, time)
            elif sniptype != 'raw':
                raise ValueError('Unknown sniptype: %s'%sniptype)
            snip = self._extract_snippet(spike, sweep, time)
            if out is None:
                out = snip[indSpinSw]
            else:
                out = np.vstack((out, snip[indSpinSw]))
        return snip
        # not saved
        # indices = [self.findOriginFromIndex(i) for i in listindex]
        # time = self._get_time(index_sweep)
        # time_list =self._time_list(index_sweep)
        # spike = time_list._data
        # sweep = self._get_input_sweep(index_sweep, dtype =self.get_param(
        #                               'dtype'))._data[1]
        # if sniptype == 'filtered':
        #     sweep = self._ready_trace(sweep, time)
        # elif sniptype != 'raw':
        #     raise ValueError('Unknown sniptype: %s'%sniptype)
        # snip = self._extract_snippet(spike, sweep, time)
        # self._saveSnip(index_sweep, snip, sniptype)
        
    def _value_around_pic(self, list_index, props, sniptype):
        snip = self._getSnip(list_index, sniptype)
        if not isinstance(props, list):
            props = [props]
        
        out = np.zeros((len(props),snip.shape[0]), dtype = 'float')       
        for i, v in enumerate(props):
            func = getattr(np, v)
            if hasattr(func, '__call__'):
                val = func(snip, axis = 1)
            else:
                print 'Prop is not callable, it might not be what you wanted'
            out[i] = val
        return out
    
    def PCA(self, sniptype):
        if not use_mdp:
            print 'mdp is not installed'
            return
        if self._cache.has_key('PCA_'+sniptype):
            return self.get_cache('PCA_'+sniptype)
        
        all_props = self.get_param('props')
        PCAnode = mdp.nodes.PCANode(input_dim=len(all_props), output_dim=len(all_props)-1)
        
        arr = self._getFilterArray(sniptype)
        
        
        PCAnode.train(arr)
        out = PCAnode(arr)
        self.set_cache('PCA_'+sniptype, out)
        return out
        
    def _getFilterArray(self, sniptype, list_sweep = None):
        if not self._cache.has_key('properties'):
            self._cache['properties'] = {}
        if self._cache['properties'].has_key(sniptype):
            return self.get_cache('properties')[sniptype]
        props = copy(self.get_param('props'))
        wasNone = False
        if list_sweep is None:
            wasNone = True
            list_sweep = range(self.numSweeps())
        elif not isinstance(list_sweep, list):
            list_sweep = list(list_sweep)
        
        out = np.zeros((self.numSpikes(list_sweep, keepMasked = True),
                        len(props)), dtype = 'float')
        
        print 'getting filter array for %s in %s'%(sniptype, self.name)
        inds = range(len(props))
        try:
            indSw = props.index('sw_ind')
            props.pop(indSw)
            inds.pop(indSw)
            N = 0
            for i in list_sweep:
                n = len(self._spikeTimes(i))
                out[N:N+n, indSw] = np.ones(n, dtype = 'float')*i
                N+=n
        except ValueError:
            print 'sw_ind not in prop'
            pass
        if wasNone:
            out[:,inds] = self._value_around_pic(range(out.shape[0]), props, sniptype).T
        else:
            pbar = pgb.ProgressBar(maxval=len(list_sweep), term_width = 79).start()
            for i in list_sweep:
                b0, b1 = self._sweepBorder(i)
                if b0 != b1:
                    data = self._value_around_pic(range(b0,b1), props, sniptype)
                    out[b0:b1,inds] = data.T
                pbar.update(i)
            
        self._cache['properties'][sniptype] = out
        return out[:]
    
    def _mask(self):
        if self._cache.has_key('mask'):
            return self._cache['mask']
        mask = np.ones(self.numSpikes(keepMasked = True), dtype = bool)
        
        Filter = self.get_param('filter')
        if Filter:
            for sniptype, prop, comp, value in Filter:
                val = np.array(self._getDataToPlot(keepMasked=True, prop=prop,
                                          sniptype=sniptype))
                val = filterValues(val, comp, value)
                mask = np.logical_and(mask, val)
                
        if self._cache.has_key('lasso'):
            Lasso = self.get_cache('lasso')
            if Lasso:
                for ms in Lasso.values():
                    mask = np.logical_and(mask,ms)
        self._cache['mask'] = mask
        return mask
        
    def numSweeps(self):
        '''return the number of sweeps'''
        return self.in_numSweeps()
    
    def chanNames(self, index = 0):
        '''return the name of the channel used for the detection'''
        return [self.get_param('chan')]
    
    def origin(self, index):
        return self.in_origin(index)
    
    def filteredSweep(self, index_sweep, chan = None):
        '''return the trace on wich the detection is done'''
        sweep = self._get_input_sweep(index_sweep)
        time = self._get_time(index_sweep)
        swdata = sweep._data[1] if sweep._data.shape[0]>1 else sweep._data[0]
        data = np.array(self._ready_trace(swdata, time), dtype = 'float')
        chinf = [getattr(sweep, cname) for cname in sweep.chanNames()]
        
        out = Sweep.Sweep(sweep.name+'_filtered', np.vstack((time, data)), chinf,self.tag(index_sweep))
        return out
    
    def snippet_chanNames(self, index = 0):
        return [self.get_param('chan')+i for i in ['_raw', '_filtered']]
    
    def snippet_origin(self, index, keepMasked = False):
        ind_sw, ind_sp = self.findOriginFromIndex(index, keepMasked = keepMasked)
        return self.in_origin(ind_sw)+ ['Spike_'+str(ind_sp)]
    
    def snippet_sweepInfo(self, index, keepMasked = False):
        if not keepMasked:
            index = self._findNotMaskedFromMaskedIndex(index)
        sw_ind, sp_ind = self.findOriginFromIndex(index, keepMasked = True)
        sw_inf = self.sweepInfo(sw_ind)
        sw_inf.numChans = 2
        chInf = [copy(sw_inf.channelInfo[0]) for i in (0,1)]
        chInf[0].name = chInf[0].name + '_raw' 
        chInf[1].name = chInf[1].name + '_filtered'
        sw_inf.channelInfo = chInf
        dt = sw_inf.dt
        win = self.get_param('snip_window')
        sw_inf.numPoints = int((win[1] - win[0])/dt)
        sw_inf.tend = sw_inf.numPoints
        sw_inf.t0 = 0
        sw_inf.dt = 1
        return sw_inf
       
    def snippet(self, index, chan = None, keepMasked = False):
        """return a snippet
        
        Arguments:
        - `index`:
        - `chan`:
        """
        if not keepMasked:
            index = self._findNotMaskedFromMaskedIndex(index)
        sw_ind, sp_ind = self.findOriginFromIndex(index, keepMasked = True)
        snipRaw = self._getSnip(index, 'raw')[0]
        snipFiltered = self._getSnip(index, 'filtered')[0]
        
        data = np.zeros((3, snipRaw.size), dtype = snipRaw.dtype)
        data[0] = np.arange(data.shape[1])
        data[1] = snipRaw
        data[2] = snipFiltered
        snipinf = self.snippet_sweepInfo(index, keepMasked)
        return Sweep.Sweep('Snippet_'+str(index)+'in_'+self.name, data, 
                           snipinf.channelInfo, tag = self.tag(sw_ind))
    
    def snip_tag(self, index, keepMasked = False):
        '''Return the tags of sweep or time_list'''
        if not keepMasked:
            index = self._findNotMaskedFromMaskedIndex(index)
        sw_ind, sp_ind = self.findOriginFromIndex(index)
        
        return self.in_tag(sw_ind)
        
    def tag(self, index):
        '''Return the tags of sweep or time_list'''
        return self.in_tag(index)
    
    def sweepInfo(self, index):
        sw_inf = self.in_sweepInfo(index)
        cname = self.get_param('chan')
        ind = [i.name for i in sw_inf.channelInfo].index(cname)
        sw_inf.channelInfo = [sw_inf.channelInfo[ind]]        
        sw_inf.numChans = 1
        return sw_inf
    
    def _findNotMaskedFromMaskedIndex(self, maskedIndex):
        mask = self._mask()
        index = np.arange(mask.size)
        return index[mask][maskedIndex]
        
    def _get_input_sweep(self, sw_ind, *args, **kwargs):
        last = self.get_cache('last')
        if last is None or last[0] != sw_ind:
            if not kwargs.has_key('chan') and not args:
                kwargs['chan'] = self.get_param('chan')
            sw = self.in_sweep(sw_ind, *args, **kwargs)
            self.set_cache('last', (sw_ind, sw), force = 1)
            return copy(sw)
        return copy(last[1])
    
    def _get_time(self, index_sweep):
        lasttime = self.get_cache('lasttime')
        if lasttime is None or lasttime[0] != index_sweep:
            node, out = self.inputs['in_sweep']
            time = self.in_sweep(index_sweep, self.get_param('chan'))._data[0]
            if time.dtype == np.dtype('int16'):
                # no time line, need to create time, assume that dt
                # is constant on the sweep, does it matter?
                swinf = self.sweepInfo(index_sweep)
                time = np.arange(swinf.t0, swinf.tend, swinf.dt,dtype = 'float')
            self.set_cache('lasttime', (index_sweep, time), force =1)
            return copy(time)
        return copy(lasttime[1])
    
    def save(self, what = None, path = None, force = 0):
        if what is None:
            what = ['SpikeTimes', 'Border', 'Mask', 'Prop', 'Lasso']
        for i in what:
            getattr(self, 'save'+i)(force = force, name = path)
    
    def saveSpikeTimes(self, name = None, force = 0, mode = 'bn', delimiter = 
                       ',', keepMasked = True):
        '''Save spike times in file 'name' (can only save ALL the spike times at
        once)
        
        'name' is absolute or relative to parent.home
        if 'force', replace existing file
        'mode' can be 'bn', 'csv', 'txt' or 'vert_csv':
            'bn': binary, saved in .npz
            'csv' or 'txt': text file, value separeted by 'delimiter' (default 
            ',') saved in lines 
            'vert_csv': text file, value and separeted by 'delimiter' (default
            ',') saved in columns '''
        import os
        path = name
        if path is None:
            path = self.parent.name+'_'+self.name+'_spikeTimes'
        if path[0] != '/':
            path = self.parent.home + path
        
        data = self.all_times(keepMasked = True, groupbysweep = True)
        if mode == 'bn':
            path += '.npz'
            if not force:
                if os.path.isfile(path):
                    print 'File %s already exist, change name or force'%path
                    return
            kwargs = {}
            for i, value in enumerate(data):
                kwargs['Sw_'+str(i)] = value
            np.savez(path, **kwargs)
        elif mode == 'vert_csv':
            path += '_vertical.csv'
            if not force:
                if os.path.isfile(path):
                    print 'File %s already exist, change name or force'%path
                    return
            
            nspike = self.numSpikes()
            out = file(path, 'w')
            totspike = 0
            index_spike = 0
            while totspike < nspike:
                for index_sweep in range(self.numSweeps()):
                    timelist = self.time_list(index_sweep)
                    if len(timelist) > index_spike:
                        out.write(str(timelist._data[index_spike]))
                        totspike+=1
                    out.write(str(delimiter))
                out.write('\n')
                index_spike += 1
                totspike += 1
            out.close()
        elif mode == 'csv' or mode =='txt':
            path += '.'+mode
            if not force:
                if os.path.isfile(path):
                    print 'File %s already exist, change name or force'%path
                    return
            out = file(path, 'w')
            for line in data:
                out.write(delimiter.join(np.array(line, dtype = 'str'))+'\n')
            out.close()
        else:
            print 'unknown mode %s'%mode
    
    def saveBorder(self, name = None, force =0):
        import os
        if name is None:
            name = self.parent.name+'_'+self.name+'_borders'
        if name[0] != '/':
            path = self.parent.home + name
        
        data = self._borders()
        outdata = np.zeros((self.numSweeps(), 2), dtype = 'int')
        for i, v in data.iteritems():
            outdata[i] = v
        path += '.npy'
        if not force:
            if os.path.isfile(path):
                print 'File %s already exist, change name or force'%path
                return
        np.save(path, outdata)
    
    def saveMask(self, name = None, force = 0):
        if name is None:
            name = self.parent.name+'_'+self.name+'_mask'
        if name[0] != '/':
            path = self.parent.home + name
        
        path += '.npy'
        if not force:
            if os.path.isfile(path):
                print 'File %s already exist, change name or force'%path
                return
        data = self._mask()
        np.save(path, data)
        
    def saveLasso(self, name = None, force = 0):
        if name is None:
            name = self.parent.name+'_'+self.name+'_lasso'
        if name[0] != '/':
            path = self.parent.home + name
        
        path += '.npz'
        if not force:
            if os.path.isfile(path):
                print 'File %s already exist, change name or force'%path
                return
        data = self._lasso()
        if data:
            np.save(path, data)
    
    def saveProp(self, sniptype = ['raw', 'filtered'], name = None, force = 0):
        if not isinstance(sniptype, list):
            sniptype = [str(sniptype)]
        if name is None:
            name = self.parent.name+'_'+self.name+'_prop'+'_'
        if name[0] != '/':
            path = self.parent.home + name
        for sntp in sniptype:
            p = path+sntp+ '.npy'
            if not force:
                if os.path.isfile(p):
                    print 'File %s already exist, change name or force'%p
                    continue
            data = self._getFilterArray(sntp)
            np.save(p, data)
    
    def set_param(self, *args, **kwargs):
        if args:
            if len(args) == 2:
                kwargs[args[0]] = args[1]
            else:
                raise ValueError('set_param accept 0 or 2 positionnal arguments')
        for val in ['filter', 'props', 'lasso']:
            if kwargs.has_key('filter'):
                self.dirty('all', selfDirty = False)
                self._params['filter'] = kwargs.pop('filter')
                if self._cache.has_key('mask'):
                    self._cache.pop('mask')
            if kwargs.has_key('lasso'):
                self._params['lasso'] = kwargs.pop('lasso')
                if self._cache.has_key('mask'):
                    self._cache.pop('mask')
        for wn in ['win'+str(i) for i in [0,1,2]]:
            if kwargs.has_key(wn):
                if kwargs[wn] is None:
                    kwargs[wn]=1e-5
                    
        if not kwargs:
            return
            # topop =  ['snippet_indexraw', 'snippet_indexfiltered', 'snippetraw',
            #          'snippetfiltered']
            # [self._cache.pop(i) for i in topop if self._cache.has_key(i)]
        return super(DetectSpike, self).set_param(**kwargs)
    
    def load(self, force = 0):
        self.loadSpikes(force= force)
        self.loadMask(force= force)
        self.loadBorders(force= force)
        try:
            self.loadProp(force= force)
            self.loadLasso(force= force)
        except Exception:
            print 'Could load only spike times and mask'
    
    def loadSpikes(self, path = None, force = 0):
        '''load spikes from a .npz file
        
        if memory is write, just load the path of the file
        if memory is store, store spike times from the file in cache'''
        if path is None:
            path = self.parent.home + self.parent.name + '_' + self.name +    \
                   '_spikeTimes.npz'
        self.set_cache('sp_times', {}, force = force)
        cached = self._cache['sp_times']
        if self.get_param('memory') == 'store':
            File = np.load(path)
            for name in File.files:
                cached[int(name[name.rfind('_')+1:])]= File[name]
        elif self.get_param('memory') == 'write':
            self.set_cache('path', path)
    
    def loadBorders(self, path = None, force = 0):
        '''load spikes from a .npz file or a .npy
        
        if memory is write, just load the path of the file
        if memory is store, store spike times from the file in cache'''
        if path is None:
            path = self.parent.home + self.parent.name + '_' + self.name +    \
                   '_borders'
        if os.path.isfile(path+'.npy'):
            path+='.npy'
        elif os.path.isfile(path+'.npz'):
            path+='.npz'
        else:
            raise IOError('no file with npy or npz extension on this path:\n%s'%
                          path)
        self.set_cache('borders', {}, force = force)
        cached = self._cache['borders']
        if self.get_param('memory') == 'store':
            File = np.load(path)
            if path.split('.')[-1] == 'npz':
                for name in File.files:
                    cached[int(name[name.rfind('_')+1:])]= File[name]
            else:
                for i, line in enumerate(File):
                    cached[i] = line
        else:
            raise NotImplementedError()
        
    def loadProp(self, sniptype = ['raw', 'filtered'], path = None, force=0):
        if path is None:
            path = self.parent.home + self.parent.name + '_' + self.name +    \
                   '_prop_'
        if not isinstance(sniptype, list):
            sniptype = [str(sniptype)]
        for sntp in sniptype:
            p = path + sntp+'.npy'
            File = np.load(p)
            if not self._cache.has_key('properties'): 
                self._cache['properties'] = {}
            self._cache['properties'][sntp] = File
    
    def loadMask(self,  path = None, force =0):
        if path is None:
            path = self.parent.home + self.parent.name + '_' + self.name +    \
                   '_mask'+'.npy'
        
        File = np.load(path)
        self._cache['mask'] = File
        
    def loadLasso(self,  path = None, force =0):
        import os
        if path is None:
            path = self.parent.home + self.parent.name + '_' + self.name +    \
                   '_lasso'+'.npz'
        if os.path.isfile(path):
            File = np.load(path)
            self._cache['lasso'] = dict([(i, File[i]) for i in File.files])
        
    def all_val(self, sniptype, list_sweep = None, groupbysweep = False,
                keepMasked = False):
        if list_sweep is None:
            list_sweep = range(self.numSweeps())
    
    def _getDataToPlot(self, prop, sniptype, keepMasked):
        if prop.split('_')[0] == 'PCA':
            if not use_mdp:
                print 'mdp is not installed'
                return
            indPCA = prop.split('_')[1]
            data= self.PCA(sniptype=sniptype)[:,indPCA]
        else:
            props = self.get_param('props')
            indprop = props.index(prop)
            data = self._getFilterArray(sniptype)[:,indprop]
        if not keepMasked:
            mask = self._mask()
            data = data[mask]
        return data
    
    def prop_hist(self, fig, prop = 'props', sniptype = 'raw', 
                  keepMasked = False, **kwargs):
        fig.clear()
        ax = fig.add_subplot(111)
        if prop == 'props':
            data = self._getFilterArray(sniptype)
            if not keepMasked:
                data = data[self._mask(),:]
            labels = self.get_param('props')
        elif prop == 'PCA':
            if not use_mdp:
                print 'mdp is not installed'
                return
            labels = ['PCA_'+str(i) for i in range(len(self.get_param('props')))]
            data = self.PCA(sniptype)
            if not keepMasked:
                data = data[self._mask(),:]
                
        else:
            labels = prop
            data = None
            for i,p in enumerate(prop):
                out = self._getDataToPlot(p, sniptype, keepMasked)
                if data is None:
                    data = np.zeros((out.size, len(prop)))
                data[:,i] = out
        out = ax.hist(data, label = labels, **kwargs)
        fig.canvas.draw()
        return out
        
    def select_snip(self, sniptype, prop, comp, value, keepMasked = True):
        allsnip = self._getSnip(range(self.numSpikes(keepMasked = True)), 
                                sniptype)
        p = self._getDataToPlot(prop, sniptype, keepMasked)
        toKeep = p >= value
        if not comp: 
            toKeep = np.invert(toKeep)
            
        return allsnip[toKeep,:]
    
    def plot_selectedsnip(self, fig, sniptype, prop=None, comp=None, value=
                          None, keepMasked = True, maxnum = 5000, **kwargs):
        if any([i is None for i in [prop, comp, value]]):
            snip = self._getSnip(range(self.numSpikes(keepMasked = True)), 
                                sniptype)
            if not keepMasked:
                snip = snip[self._mask(),:]
        else:
            snip = self.select_snip(sniptype,prop,comp, value, keepMasked)
        totnum = snip.shape[0]
        fig.clear()
        ax = fig.add_subplot(111)
        if snip.shape[0]> maxnum:
            snip = snip[:maxnum,:]
            
        ax.plot(snip.T, **kwargs)
        mean = snip.mean(axis = 0)
        ax.plot(mean, 'r')
        ax.set_title('%s snippets of %s\n(%s/%s plotted)'%(sniptype, self.name,
                                                           snip.shape[0],totnum
                                                           ))
        fig.canvas.draw()
        return snip, mean
        
    def prop_plot(self, figure, propx= 'min', propy = 'max', sniptype = 'raw',
                  clear = True, keepMasked = False, **kwargs):
        print 'ploting properties in %s'%self.name
        
        self._fig = figure
        self._sniptype = sniptype
        self._keepMasked = keepMasked
        if clear: self._fig.clear()
        ax = self._fig.add_subplot(111)
        ax.set_xlabel(propx)
        ax.set_ylabel(propy)
        X = self._getDataToPlot(propx, sniptype, keepMasked)
        Y = self._getDataToPlot(propy, sniptype, keepMasked)
        
        if not kwargs.has_key('marker'):
            kwargs['marker']='.'
        ax.plot(X, Y, 'k',ls = '', picker = 5, label = '_nolegend_',
                **kwargs)
        ax.set_title('Properties of spikes from %s \n%s spikes plotted'%(
                     self.name, X.size))
        self._fig.canvas.mpl_connect('pick_event', self._picked)
        self._last_event = None
        self._fig.canvas.draw()
        self._temp = None
        return X, Y
    
    def _picked(self, event):
        if self._last_event is not None:
            if self._last_event.mouseevent is event.mouseevent: return
            line = self._last_event.artist
            line.set_mfc('k')
            line.set_zorder(1)
        self._last_event = event
        line = self._last_event.artist
        
        line.set_zorder(0)
        i = event.ind[0]
        x = np.array([line.get_xdata()[i]])
        y = np.array([line.get_ydata()[i]])
        
        if self._temp is None:
            self._temp, = self._fig.axes[0].plot(x, y, 'yo', ms = 10, 
                                                 alpha = .5)
            self._temp.set_zorder(2)
            self._temp.set_label('Spike %s'%i)
            
        else:
            self._temp.set_xdata(x)
            self._temp.set_ydata(y)
            self._temp.set_label('Spike %s'%i)
        self._fig.axes[0].legend((line, self._temp),(line.get_label(),
                                  self._temp.get_label()), loc = 2)
        self._fig.canvas.draw()
        
        ax = self._fig.add_axes([0.6,0.6,0.25,0.25], facecolor = 'none')
        ax.clear()
        index_sweep, index_spike = self.findOriginFromIndex(i, keepMasked = 
                                                            self._keepMasked)
        ax.set_title('Spike %s (%s in sweep %s)'%(i, index_spike, index_sweep))
        ax.set_xlabel('index')
        ax.set_ylabel(self._sniptype + ' snippet')
        if not self._keepMasked:
            i = self._findNotMaskedFromMaskedIndex(i)
        snip = self._getSnip(i, self._sniptype)
        
        line = ax.plot(snip.T, 'k')
        self._fig.canvas.draw()
    
    def multi_prop_plot(self, fig, prop, sniptype = 'raw', keepMasked = False,
                        **kwargs):
        """Plot all prop[i] vs prop[j] combination in one figure
        
        Use prop = PCA to plot all PCA components
            prop = props to plot all other properties"""
        if prop == 'PCA':
            prop = ['PCA_'+str(i) for i in range(len(self.get_param("props"))-2)]
        elif prop == 'props':
            prop = self.get_param('props')
        size = len(prop)
        fig.clear()
        
        data = [self._getDataToPlot(keepMasked=keepMasked,sniptype=sniptype, prop = i) for i in prop]
        axes =[]
        for line in range(1,size):
            datay = data[line]
            axes.append([fig.add_subplot(size-1,size-1,(line-1)*(size-1)+1+i) for i in range(line)])
            [ax.plot(data[j],datay, **kwargs) for j,ax in enumerate(axes[-1])]
        [ax[0].set_ylabel(prop[i+1]) for i, ax in enumerate(axes)]
        [ax.set_xlabel(prop[i]) for i, ax in enumerate(axes[-1])]
        fig.canvas.draw()
        return fig
        
    def _lasso(self):
        if not self._cache.has_key('lasso'):
            self._cache['lasso'] = {}
        return self._cache['lasso']
        
        
    def lasso_prop_plot(self, figure, propx= 'min', propy = 'max', sniptype = 'raw',
                        clear = True, keepMasked = False, **kwargs):
        print 'ploting properties in %s'%self.name
        
        if clear: figure.clear()
        ax = figure.add_subplot(111)
        ax.set_xlabel(propx)
        ax.set_ylabel(propy)
        X = self._getDataToPlot(propx, sniptype, keepMasked)
        Y = self._getDataToPlot(propy, sniptype, keepMasked)
        self._lassoMask = self._mask()
        self._lassoManager = LassoManager(ax, np.vstack((X,Y)).T, sizes = (5,), **kwargs)
        ax.set_xlim(X.min(),X.max())
        ax.set_ylim(Y.min(),Y.max())
        figure.canvas.draw()
        return X, Y
    
    def keep_in_lasso(self, name = None):
        isinside = self._lassoManager.isinside
        mask = np.array(self._lassoMask)
        mask[mask] = np.logical_and(mask[mask], isinside)
        
        Lasso = self._lasso()
        if name is None:
            n = 0
            while 'lasso_%s'%n in Lasso.keys():
                n+=1
            name = 'lasso_%s'%n
        self._cache['lasso'][name] = mask
        if self._cache.has_key('mask'):
            self.set_cache('mask', np.logical_and(self._mask(), mask), force = 1)
        return mask
        
    def exlude_lasso(self, name =None):
        isinside = self._lassoManager.isinside
        mask = np.array(self._lassoMask)
        mask[mask] = np.logical_and(mask[mask], np.logical_not(isinside))
        Lasso = self._lasso()
        if name is None:
            n = 0
            while 'lasso_%s'%n in Lasso.keys():
                n+=1
            name = 'lasso_%s'%n
        self._cache['lasso'][name] = mask
        if self._cache.has_key('mask'):
            self.set_cache('mask', np.logical_and(self._mask(), mask), force = 1)
        return mask
        
class CreateUniv:
    def __init__(self, node):
        self.node = node
      
    def __call__(self):
            a = self.node.in_chanNames()
            a.append('None')
            return a
