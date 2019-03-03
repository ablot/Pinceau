# -*- coding: utf-8 -*-

#import numpy as np
from neuropype import node
#from itertools import imap, repeat
#from copy import deepcopy, copy

#from bisect import bisect_left
#from neuropype.ressources._common import boxfilter, findextrema, cross_threshold, flatenList
#import neuropype.ressources.progressbar as pgb
#from neuropype.datatypes import Time_list, Sweep

# Node name.
class NodeTemplate(node.Node):
    def __init__(self, name, parent):
        #inputs
        self.in_sweep = node.Input('Sweep')
        self.in_numSweeps = node.Input('int')
        self.in_chanNames = node.Input('list')
        self.in_origin = node.Input('list')
        self.in_tag = node.Input('list')
        self.in_sweepInfo = node.Input('SweepInfo')
        
        #outputs
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
        self._params={'chan': 'Ch_0',
                      'maximum': True,
                      'threshold': 0, 
                      'cross_threshold': False,
                      'pointinterval': 1e-3,
                      'baseline' : 'floating',
                      'verbose' : 1,
                      'win0':5e-3,
                      'win1' : None,
                      'win2' : None,
                      'dt0' : 0,
                      'dt1' : 0,
                      
                      'baseline_window': ['begin', 'end'],
                      
                      'memory': 'store',
                      'snip_window' : [-2e-3,2e-3],
                      'dtype' : 'int16',
                      'props' : ['max', 'min', 'std', 'ptp', 'mean', 
                                 'argmax', 'median', 'argmin', 'trapz'],
                      'snip_memory' : ('store', 'all'),
                      'filter':[],
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
        params = self._params
        f0, f1, f2, dt0, dt1 = None, None, None, None, None
        dtype = None
        if data.dtype == 'int':
            dtype = data.dtype
            data = np.asarray(data, dtype ='float64')
        dt = float(time[1]-time[0])
        #try:
            #1/dt
        #except:
            #dt = 1
        #substracting baseline:
        if params['baseline'] == 'window':
            if params['baseline_window'][0] == 'begin': 
                beg =0
            else: 
                baseline_window0 = float(params['baseline_window'][0])
                beg  = bisect_left(time, baseline_window0)
            if params['baseline_window'][1] == 'end':
                end = -1
            else: 
                baseline_window1 = float(params['baseline_window'][1])
                end = bisect_left(time,baseline_window1)
            baseline = np.mean(data[beg:end])
            data-=baseline
        elif isinstance(params['baseline'], float):
            baseline = float(params['baseline'])
            data-=baseline
        elif params['baseline']=='floating':
            cumsum = data.cumsum()
            win0 = int(params['win0']/dt)
            f0 = boxfilter(data, win0, cumsum)
            if params['win1'] is None:
                #simply substract baseline
                data-=f0
            else:
                #kind of first order derivative
                dt0=int(float(params['dt0']/dt))
                if dt0 == 0: dt0 = 1
                win1 = int(self.get_param('win1')/dt)
                f1 = boxfilter(data, win1, cumsum)
                if params['win2'] is None:
                    data = np.zeros_like(data)
                    data[dt0/2:-dt0/2] = f1[dt0:] - f0[:-dt0]
                else:
                    #kind of 2nd order derivative
                    win2 = int(params['win2']/dt)
                    dt1=int(float(params['dt1']/dt))
                    if dt1 == 0: dt1=1
                    f2 = boxfilter(data, win2, cumsum)
                    data = np.zeros_like(data)
                    data[dt1/2:-dt1/2] = f2[dt1:]-2*f1[dt0:-dt1+dt0]-f0[:-dt1]
        elif params['baseline']:
            baseline=np.mean(data)
            data-=baseline
        if dtype is not None:
            data = np.asarray(data, dtype = dtype)
        if debug:
            return data, f0, f1, f2, dt0, dt1
        return data

    def _detect(self, trace, time):
        '''Filter the trace, do the detection on it, filter the values and 
        return them'''
        params = self._params
        dt=time[1]-time[0]
        pointinterval=int(float(params['pointinterval']/dt))
        
        if not params['cross_threshold']:
            temp = findextrema(trace, params['maximum'], params['threshold'], 
                               pointinterval)
        else:
            temp = cross_threshold(trace, params['maximum'], params['maximum'], 
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
            dtype = self.get_param('dtype')
            sweep = self._get_input_sweep(index_sweep, dtype = dtype)
            time = self._get_time(index_sweep)
            trace = self._ready_trace(deepcopy(sweep._data[1]), time)
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
                b0, b1 = self._sweepBorder(i)
                data = data[mask[b0: b1]]
            out.append(data)
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
        for i in xrange(self.in_numSweeps()):
            length = len(func(i))
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
    
    def _sweepBorder(self, index):
        """index of first and last spikes of sweep in numSpikes"""
        if not self._cache.has_key('borders'): self._cache['borders'] = {}
        bord = self._cache['borders']
        out = bord.get(index)
        if out is not None:
            return out
        out = (self.findSpikeFromSweep(index, True), 
               self.findSpikeFromSweep(index+1, True))
        bord[index] = out
        return out
    
    def _borders(self):
        for i in range(self.numSweeps()):
            self._sweepBorder(i)
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
        if verbose: pbar = pgb.ProgressBar(maxval=len(list_sweep), 
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
        dtype = self.get_param('dtype')
        
        beg = time.searchsorted(sp_times + win0)
        end = time.searchsorted(sp_times + win1)
        midl = time.searchsorted(sp_times)
        length = (end-beg).max()
        out = np.zeros((len(beg), length), dtype = dtype)
        for i ,(s, b,e) in enumerate(zip(midl, beg, end)):
            if e - b == length:
                out[i] = trace[b:e]
            else:
                border0 = length/2
                if s - b > border0 or border0+e -s > length:
                    raise ValueError('ca bug')
                out[i, border0 - (s - b): border0 + (e-s)] = trace[b:e]
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
                               dtype = self.get_param('dtype'))
                self._cache['snippet_'+sniptype] = out
                
            if not self._cache.has_key('snippet_index_'+sniptype):
                out = np.zeros(self.numSpikes(keepMasked=True), dtype = 'bool')
                self._cache['snippet_index_'+sniptype] = out
            
            b0, b1 = self._sweepBorder(index_sweep)
            self._cache['snippet_'+sniptype][b0:b1,:] = snippet
            self._cache['snippet_index_'+sniptype][b0:b1] = np.ones(b1-b0, 
                                                                dtype = 'bool')
    
    def _extract_all_snippet(self, sniptype):
        pbar = pgb.ProgressBar(maxval=self.numSweeps(), term_width = 79).start()
        for index_sweep in range(self.numSweeps()):
            time = self._get_time(index_sweep)
            spike = self._spikeTimes(index_sweep)
            if not spike.size:
                continue
            sweep = self._get_input_sweep(index_sweep, dtype =self.get_param(
                                          'dtype'))._data[1]
            if sniptype == 'filtered':
                sweep = self._ready_trace(sweep, time)
            elif sniptype != 'raw':
                raise ValueError('Unknown sniptype: %s'%sniptype)
            snip = self._extract_snippet(spike, sweep, time)
            self._saveSnip(index_sweep, snip, sniptype)
            pbar.update(index_sweep)
        pbar.finish()
    
    def _getSnip(self, listindex, sniptype):
        if not isinstance(listindex, list):
            listindex = [int(listindex)]
        
        snip_memory = self.get_param('snip_memory')
        if snip_memory[0] == 'store':
            if snip_memory[1] != 'all':
                raise NotImplementedError()
                # out = {}
                # sweep_saved = self.get_cache('snippet_'+sniptype)
                # if not sweep_saved is None:
                #     for i in listindex:
                #         swind, spind = self.findOriginFromIndex(i)
                #         not_saved = []
                #     for i in list_index:
                #         sweep
                #         saved_ind =[i for i in listindex if i in sweep_saved]
            else:
                inds = self.get_cache('snippet_index_'+sniptype)
                if inds is None or any([not inds[i]  for i in listindex]):
                    self._extract_all_snippet(sniptype)
                return np.array(self._cache['snippet_'+sniptype][listindex,:])
        raise NotImplementedError()
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
        if self._cache.has_key('PCA_'+sniptype):
            return self.get_cache('PCA_'+sniptype)
        
        all_props = self.get_param('props')
        PCAnode = mdp.nodes.PCANode(input_dim=len(all_props), output_dim=len(all_props)-1)
        
        arr = self._getFilterArray(sniptype)
        

        PCAnode.train(arr)
        out = PCAnode(arr)
        self.set_cache('PCA_'+sniptype, out)
        return out
        
    def _getFilterArray(self, sniptype):
        if not self._cache.has_key('properties'):
            self._cache['properties'] = {}
        if self._cache['properties'].has_key(sniptype):
            return self.get_cache('properties')[sniptype]
        props = copy(self.get_param('props'))
        out = np.zeros((self.numSpikes(keepMasked = True), len(props)), 
                       dtype = 'float')
        list_sweep = range(self.numSweeps())
        pbar = pgb.ProgressBar(maxval=len(list_sweep), term_width = 79).start()
        
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
            print 'error'
            pass
        for i in list_sweep:
            b0, b1 = self._sweepBorder(i)
            if b0 != b1:
                data = self._value_around_pic(range(b0,b1), props, sniptype)
                out[b0:b1,inds] = data.T
            pbar.update(i)

        self._cache['properties'][sniptype] = out
        return out
    
    def _mask(self):
        if self._cache.has_key('mask'):
            return self._cache['mask']
        mask = np.ones(self.numSpikes(keepMasked = True), dtype = bool)
        
        Filter = self.get_param('filter')
        
        for sniptype, prop, comp, value in Filter:
            val = self._getDataToPlot(keepMasked=True, prop=prop,
                                      sniptype=sniptype)
            val -= value
            if not comp: val *= -1
            mask = np.logical_and(mask, val >= 0)
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
        sweep = self._get_input_sweep(index_sweep, dtype = self.get_param('dtype'))
        time = self._get_time(index_sweep)
        sweep._data = np.asarray(sweep._data, dtype = 'float64')
        sweep._data[1] = self._ready_trace(sweep._data[1], time)
        sweep._data[0] = time
        sweep.tag = self.tag(index_sweep)
        return sweep
    
    def snippet_chanNames(self, index = 0):
        return [self.get_param('chan')+i for i in ['_raw', '_filtered']]
    
    def snippet_origin(self, index):
        ind_sw, ind_sp = self.findOriginFromIndex(index)
        return self.in_origin(ind_sw)+ ['Spike_'+str(ind_sp)]
    
    def snippet_sweepInfo(self, index, keepMasked = False):
        if not keepMasked:
            index = self._findNotMaskedFromMaskedIndex(index)
        sw_ind, sp_ind = self.findOriginFromIndex(index)
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
        sw_ind, sp_ind = self.findOriginFromIndex(index)
        snipRaw = self._getSnip(index, 'raw')[0]
        snipFiltered = self._getSnip(index, 'filtered')[0]
        
        data = np.zeros((3, snipRaw.size), dtype = self.get_param(
                                                                   'dtype'))
        data[0] = np.arange(data.shape[1])
        data[1] = snipRaw
        data[2] = snipFiltered
        snipinf = self.snippet_sweepInfo(index, keepMasked)
        return Sweep.Sweep('Snippet_'+str(index)+'in_'+self.name, data, 
                           snipinf.channelInfo, tag = self.tag(index))
    
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
            time = self.in_sweep(index_sweep)._data[0]
            self.set_cache('lasttime', (index_sweep, time), force =1)
            return copy(time)
        return copy(lasttime[1])
    
    def save(self, what = ['SpikeTimes', 'Border', 'Mask', 'Prop'],
             path = None, force = 0):
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
        if name is None:
            name = self.parent.name+'_'+self.name+'_spikeTimes'
        if name[0] != '/':
            path = self.parent.home + name
        
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
                    timelist = self._time_list(index_sweep)
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
            np.savetxt(path, data, delimiter = delimiter)
        else:
            print 'unknown mode %s'%mode
    
    def saveBorder(self, name = None, force =0):
        import os
        if name is None:
            name = self.parent.name+'_'+self.name+'_borders'
        if name[0] != '/':
            path = self.parent.home + name
        
        data = self._borders()
        path += '.npz'
        if not force:
            if os.path.isfile(path):
                print 'File %s already exist, change name or force'%path
                return
        kwargs = {}
        for i, value in data.iteritems():
            kwargs['Sw_'+str(i)] = value
        np.savez(path, **kwargs)
    
    def saveMask(self, name = None, force = 0):
        import os
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
    
    def saveProp(self, sniptype = ['raw', 'filtered'], name = None, force = 0):
        if not isinstance(sniptype, list):
            sniptype = [str(sniptype)]
        
        import os
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
        if len(args) == 2:
            kwargs[args[0]] = args[1]
        for val in ['filter', 'props']:
            if kwargs.has_key('filter'):
                self._params['filter'] = kwargs.pop('filter')
                if self._cache.has_key('mask'):
                    self._cache.pop('mask')
        if not kwargs:
            return
            # topop =  ['snippet_indexraw', 'snippet_indexfiltered', 'snippetraw',
            #          'snippetfiltered']
            # [self._cache.pop(i) for i in topop if self._cache.has_key(i)]
        return super(DetectSpike, self).set_param(*args, **kwargs)
    
    def loadAll(self, force = 0):
        self.loadProp(force= force)
        self.loadSpikes(force= force)
        self.loadMask(force= force)
        self.loadBorders(force= force)
    
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
        '''load spikes from a .npz file

        if memory is write, just load the path of the file
        if memory is store, store spike times from the file in cache'''
        if path is None:
            path = self.parent.home + self.parent.name + '_' + self.name +    \
                   '_borders.npz'
        self.set_cache('borders', {}, force = force)
        cached = self._cache['borders']
        if self.get_param('memory') == 'store':
            File = np.load(path)
            for name in File.files:
                cached[int(name[name.rfind('_')+1:])]= File[name]
        
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
    
    def all_val(self, sniptype, list_sweep = None, groupbysweep = False,
                keepMasked = False):
        if list_sweep is None:
            list_sweep = range(self.numSweeps())
    
    def _getDataToPlot(self, prop, sniptype, keepMasked):
        if prop.split('_')[0] == 'PCA':
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
                
