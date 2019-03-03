# -*- coding: utf-8 -*-
from neuropype import node
from neuropype.datatypes.Sweep import Sweep
#from neuropype.datatypes import Time_list, Sweep
#from neuropype.ressources._common import boxfilter, findextrema, cross_threshold
from neuropype import tag as tagModule
import numpy as np

from neuropype import parameter


class RunningAverage(node.Node):
    '''Average sweeps'''
    
    def __init__(self, name, parent):
        self.in_sweep = node.Input('Sweep')
        self.in_numSweeps = node.Input('int')
        self.in_chanNames = node.Input('list')
        self.in_origin = node.Input('list')
        self.in_tag = node.Input('list')
        self.in_sweepInfo = node.Input('SweepInfo')
        
        self.out_numSweeps = node.Output('int')
        self.out_sweep = node.Output('Sweep')
        self.out_chanNames = node.Output('list')
        self.out_origin = node.Output('list')
        self.out_tag = node.Output('list')
        self.out_sweepInfo = node.Output('SweepInfo')
        
        super(RunningAverage, self).__init__(name, parent)
        
        self._inputGroups['sweep'] = {'sweep': 'in_sweep',
                                      'numSweeps': 'in_numSweeps',
                                      'chanNames': 'in_chanNames',
                                      'origin': 'in_origin',
                                      'tag' : 'in_tag',
                                      'sweepInfo': 'in_sweepInfo'}
        self._outputGroups['sweep'] = {'sweep': 'out_sweep',
                                       'numSweeps': 'out_numSweeps',
                                       'chanNames': 'out_chanNames',
                                       'origin': 'out_origin',
                                       'tag' : 'out_tag',
                                       'sweepInfo': 'out_sweepInfo'}
        
        #connecting outputs:
        self.out_numSweeps.output = self.numSweeps
        self.out_sweep.output = self.sweep
        self.out_chanNames.output = self.chanNames
        self.out_origin.output = self.origin
        self.out_tag.output = self.tag
        self.out_sweepInfo.output = self.sweepInfo
        
        #defining parameters:
        num_av = parameter.integer('num_av', self, 1, minVal = 1, 
                                   maxVal = self.numSweeps)
        padding = parameter.combobox('padding', self, ['nearest', 'less', 'bug'], 'nearest')
        memory = parameter.integer('memory', self, 1, minVal = 0,
                                   maxVal = self.numSweeps)
        self._params = {'graphviz': {'fillcolor':'thistle',
                                     'style': 'filled'},
                        'memory': memory,
                        'num_av': num_av,
                        'padding': padding
                        }
    
    def numSweeps(self):
        if self.get_param('padding') == 'bug':
            return self.in_numSweeps()-self.get_param('num_av')
        return self.in_numSweeps()
        
    def chanNames(self, index = 0):
        return self.in_chanNames(index)
    
    def tag(self, index, AND = 1, OR = 1):
        '''return the tag associated with the average
        
        if AND return tags present in all the averaged sweeps
        if OR return tags present in any of the averaged sweeps'''

        #tag = self._createTagFromParams(index)
        list_index = self._createListIndex(index)#, tag)
        cached = self.get_cache('cached_tag')
        if cached is None: cached = {}
        out = cached.get(str(index))
        if out is not None:
            return out
        if len(list_index) == 0:
            return []
        out = self.in_tag(list_index[0] )
        if len(list_index) != 1:
            for ind in list_index[1:]:
                out = tagModule.combine(out, self.in_tag(ind), AND, OR)
        mem = self.get_param('memory')
        if mem:
            order = self.get_cache('order_tag')
            if order is None: order =[]
            while len(order) >= mem:
                last = order.pop(-1)
                cached.pop(str(last))
            order.append(index)
            cached[str(index)] = out
            self.set_cache('order_tag', order, force =1)
            self.set_cache('cached_tag', cached, force = 1)
        return out
        
    def _createListIndex(self, index):
        #if int(index) >= self.numSweeps():
        #    raise ValueError('Index %s out of range in %s (max = %s)'%(
        #                           index, self.name, self.numSweeps()))
        index = int(index)
        num = self.get_param('num_av')
        policy = self.get_param('padding')
        missing = 0
        if index >= num/2:
            beg = index - num/2
        elif policy == 'bug':
            raise ValueError('index %s not compatible with policy "bug", pb at the beginning'%index)
        else:
            beg = 0
            missing = num/2 - index
        numSweeps = self.in_numSweeps()
        if index + num/2 + missing <= numSweeps:
            end = index + num/2 + missing
        elif policy == 'bug':
            raise ValueError('index %s not compatible with policy "bug", pb at the end'%index)
        else:
            end = numSweeps
            
        list_index = range(beg,end)
        return list_index
    
    def numAveraged(self, index):
        #tag= self._createTagFromParams(index)
        lst = self._createListIndex(index)#, tag)
        return len(lst)
    
    def sweep(self, index, chan = None):
        assert index < self.numSweeps()
        if chan is None:
            chan = list(sorted(self.chanNames()))
        if not isinstance(chan, list):
            chan = [str(chan)]
        list_index = self._createListIndex(index)#, tag)
        cached = self.get_cache('cached')
        if cached is None: cached = {}
        key = 'sw'+str(index)
        data = cached.get(key) if cached is not None else None
        
        swinf = self.in_sweepInfo(0)
        chanNames = [i.name for i in swinf.channelInfo]
        chanInd = [chanNames.index(c) for c in chan]
        chanInf = [swinf.channelInfo[i] for i in chanInd]
        name = 'Sw_%s_in_%s_%s_sweeps_averaged'%(index,self.name,len(list_index))
        if data is not None and data.shape[0] != len(chan):
            data = None
        if data is None:
            if list_index:
                for i, ind in enumerate(list_index):
                    in_sw = self.in_sweep(ind)
                    chanInd = [in_sw._name2index[name] for name in chan]
                    if data is None:
                        data = in_sw._data[[0]+chanInd,:]
                    else:
                        data += in_sw._data[[0]+chanInd,:]
                data/= float(len(list_index))
            else:
                data = np.array([])
                
            
        if data.size:
            out = Sweep(name = name, data = data, chan_info 
                        = chanInf)
        else:
            return None
        out.tag = self.tag(index)
        if self.get_param('memory'):
            order = self.get_cache('order')
            if order is None: order = []
            while len(cached) >= int(self.get_param('memory')):
                if len(cached) == len(order):
                    first = order.pop(0)
                    cached.pop(first)
                elif len(cached)<len(order):
                    raise ValueError('I have lost the order somehow')
                else:
                    cached.popitem()
            order.append(key)
            cached[key] = data
            self.set_cache('cached', cached, force  =1)
            self.set_cache('order', order, force = 1)
        return out

    def sweepInfo(self, index):
        return self.in_sweepInfo(index)
    
    def origin(self, index):
        return self.in_origin(index) + [self.name]

    def save(self, force = False, path = None):
        import os               
        if path is None:
            path = self.parent.name+'_'+self.name +'_cached.npz'
        if path[0] != '/':
            path = self.parent.home + path
        if not self._cache.has_key('cached'):
            print 'Nothing to save, nothing saved'
            return
        data = self._cache['cached']
        
        if not force:
            if os.path.isfile(path):
                print 'File %s already exist, change name or force'%path
                return
        kwargs = {}
        for i, value in data.iteritems():
            kwargs[i] = value
        np.savez(path, **kwargs)

    def load(self, force = 0, name = None):
        
        if name is None:
            name = self.parent.name+'_'+self.name +'_cached.npz'
        if name[0] != '/':
            path = self.parent.home + name
        if not path.endswith('.npz'):
            path += '.npz'
        data = np.load(path)
        if not self._cache.has_key('cached'):
            self._cache['cached'] = {}
        for k in data.files:
            if not force:
                if self._cache['cached'].has_key(k):
                    print 'Average already in cache. Use force to replace it'
                    continue
            self._cache['cached'][k] = data[k]
        
