# -*- coding: utf-8 -*-
from neuropype import node
from neuropype.datatypes.Sweep import Sweep
#from neuropype.datatypes import Time_list, Sweep
#from neuropype.ressources._common import boxfilter, findextrema, cross_threshold
import neuropype.ressources.progressbar as pgb
from neuropype import tag as tagModule
import numpy as np
from neuropype.ressources._common import uniquify, flatenList

from neuropype import parameter


class Average(node.Node):
    '''Average sweeps
    
    Default output sweep(index) is the average from sweep "begin_average" to 
    index-1 if index is integer, if index is a list of int, output is the
    average of all sweeps whose index is in that list
    
    TagNames can be a list of tag types names. Those names must be defined in
    the tagManager, so you might need to call one tag function to create them
    first
    If it's the case, average's first sweep is the average of input sweeps
    tagged 
    with the first value of the universe of the first tagType of the TagNames 
    list.
    
    So numSweeps is sum([len(tagType.universe) for tagType in TagNames]), if one
    of the tagType's universe is "int", then Average needs to loop on all inputs
    to count the number sweeps it can return
    
    if jackKnife is True do the average of all the inputs except index
    TODO change jackKnife to make it a bit smarter'''
    
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
        
        super(Average, self).__init__(name, parent)
        
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
        beg_av = parameter.integer('beg_av', self, 0, minVal = 0, 
                                   maxVal = self.numSweeps)
        jack = parameter.boolean('jackKnife', self, False)
        memory = parameter.integer('memory', self, 1, minVal = 0,
                                   maxVal = self.numSweeps)
        self._params = {'begin_average': beg_av,
                        'graphviz': {'fillcolor':'thistle',
                                    'style': 'filled'},
                        'memory': memory,
                        'TagNames': None,
                        'jackKnife': jack,
                        }
    
    def set_param(self, *args, **kwargs):
        args = [a for a in args]
        if len(args) >0:
            if args[0] == 'TagNames':
                if not isinstance(args[1], list) and args[1] is not None:
                    args[1] = [args[1]]
        if 'TagNames' in kwargs.keys():
            if not isinstance(kwargs['TagNames'], list) and kwargs['TagNames'] \
               is not None:
                kwargs['TagNames'] = [kwargs['TagNames']]
        super(Average, self).set_param(*args, **kwargs)
    
    
    def numSweeps(self):
        if self.get_param('TagNames') is None:
            return self.in_numSweeps()-1
        TagNames = self.get_param('TagNames')
        TagTypes = [getattr(self.parent.tagManager, name) for name in TagNames]
        count = 0
        for tg in TagTypes:
            if tg.universe is int:
                count += self._countIntUniverse(tg.__name__)
            else:
                count += len(tg.universe)
        return count
    
    def _countIntUniverse(self, tagName, returnAll = 0):
        tagType = getattr(self.parent.tagManager, tagName)
        if tagType.universe is not int:
            print 'universe for %s is not int !'%tagName
            return
        count = 0
        All = []
        for i in range(self.in_numSweeps()):
            taglist = self.in_tag(i)
            if any([type(tg) == tagType for tg in taglist]):
                count += 1
                All += i
        if returnAll:
            return (count, All)
        return count
    
    def tagUsed2Average(self, index = None):
        '''return the tag used to average
        
        if index is None, return the list of (tagtype, tagvalue) used,
        otherwise return the (tagtype, tagvalue) used for average.sweep(index)
        '''
        TagNames = self.get_param('TagNames')
        if TagNames is None:
            print 'No tag used !!!!'
            return
        tgMg = self.parent.tagManager
        if index is None:
            out = []
            for tagName in TagNames:
                tagType = getattr(tgMg, tagName)
                if tagType.universe is int:
                    n, AllIndex = self._countIntUniverse(tagType.__name__, 1)
                    out += [(tagName, i) for i in AllIndex]
                else:
                    out += [(tagName, value) for value in tagType.universe]
            return out
        
        count = 0
        for tagName in TagNames:
            tagType = getattr(tgMg, tagName)
            if tagType.universe is not int:
                univ = tagType.universe
            else:
                n, univ = self._countIntUniverse(tagType.__name__, 1)
            
            if index < count + len(univ):
                return (tagName, univ[index - count])
            count += len(univ)
        raise ValueError('I think I haven\'t found what I was looking for ...')
    
    def chanNames(self, index = 0):
        return self.in_chanNames(index)
    
    def tag(self, index, AND = 1, OR = 1):
        '''return the tag associated with the average
        
        if AND return tags present in all the averaged sweeps
        if OR return tags present in any of the averaged sweeps'''
        
        #tag = self._createTagFromParams(index)
        print "creating tag"
        list_index = self._createListIndex(index)#, tag)
        cached = self.get_cache('cached_tag')
        if cached is None: cached = {}
        out = cached.get(str(index))
        if out is not None:
            return out
        if len(list_index) == 0:
            return []
        print 'getting input'
        tags = [self.in_tag(i) for i in list_index]
        print 'fusing input'
        vals = {}
        for ta in tags:
            for i in ta:
                if type(i).__name__ not in vals:
                    vals[type(i).__name__] = [i.value]
                else:
                    vals[type(i).__name__].append(i.value)
        print 'sorting values types'
        trueVals = [(k, uniquify([_ for sub in v for _ in sub])) for k, v in vals.items()] 
        out = []
        print 'generate out tag'
        for k,v in trueVals:
            tgName = 'tag_%s_in_%s_sw_%s'%(k,self.name, index)
            out.append(getattr(self.parent.tagManager, k)(tgName, v))
        # out = self.in_tag(list_index[0] )
        # if len(list_index) != 1:
        #     for ind in list_index[1:]:
        #         out = tagModule.combine(out, self.in_tag(ind), AND, OR)
        print 'done'
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
        if self.get_param('jackKnife'):
            list_index = range(self.get_param('begin_average'), 
                               self.numSweeps())
            list_index.pop(index)
            return list_index
        if self.get_param('TagNames') is None:
            #default behaviour
            if isinstance(index, int):
                assert index >= self.get_param('begin_average')
                list_index = range(self.get_param('begin_average'), index+1)
            elif isinstance(index, list):
                list_index = [int(i) for i in index]
            else:
                raise IOError('index must be int or list of int')
        else:
            list_index = self.get_cache(index)
            if list_index is None:
                self._findTaggedInputs()
            list_index = self._cache[index]
        return list_index
        
    def tag2Index(self, tagTypeName, tagValue):
        """return the index corresponding to `tagValue` of `tagType`
        
        Arguments:
        - `tagType`: a tag type in TagNames
        - `tagValue`: a value of tagType universe
        """
        tagNames = self.get_param('TagNames')
        if tagTypeName not in tagNames:
            raise ValueError('tagType must be in TagNames')
        tagType = getattr(self.parent.tagManager, tagTypeName)
        if tagValue not in tagType.universe:
            raise ValueError('tagValue must be in tagType.universe')
            
        tagTypeIndex = tagNames.index(tagTypeName)
        uInd = tagType.universe.index(tagValue)
        return tagTypeIndex+uInd    
        
    def _findTaggedInputs(self):
         """Populate cache (find tagged sweeps)
         """
         tag2use = self.tagUsed2Average()
         types = []
         out = dict([(i, []) for i in xrange(len(tag2use))])
         for i, j in tag2use:
             if i not in types:
                 types.append(i)
         print 'Finding tagged inputs in %s ...'%self.name
         pbar = pgb.ProgressBar(maxval=self.in_numSweeps(),term_width =
                                                                79).start()
         for i in xrange(self.in_numSweeps()):
             pbar.update(i)
             listTag = self.in_tag(i)
             for tg in listTag:
                 name = tg.__class__.__name__
                 if name in types:
                     for value in tg.value:
                         ind = self.tag2Index(name, value)
                         out[ind].append(i)
                         
         [self.set_cache(k,v) for k, v in out.iteritems()]
         pbar.finish()
    
    def numAveraged(self, index):
        #tag= self._createTagFromParams(index)
        lst = self._createListIndex(index)#, tag)
        return len(lst)
        
    # def _createTagFromParams(self, index):
    #     if self.get_param('TagNames') is not None:
    #         if not isinstance(index, int):
    #             raise ValueError('index must be an integer')
    #         tagTypeName, tagValue = self.tagUsed2Average(index)
    #         tagType = getattr(self.parent.tagManager, tagTypeName)
    #         name = '%s_index%s_in%s'%(tagTypeName,index,self.name)
    #         tag = tagType(name = name, value = tagValue)
    #         return tag
    
    def sweep(self, index, chan = None):
        #assert index < self.numSweeps()
        if chan is None:
            chan = list(sorted(self.chanNames()))
        if not isinstance(chan, list):
            chan = [str(chan)]
        list_index = self._createListIndex(index)#, tag)
        cached = self.get_cache('cached')
        if cached is None: cached = {}
        key = 'sw'+str(index)
        cached_val = cached.get(key) if cached is not None else None
        swinf = self.in_sweepInfo(0)
        chanNames = [i.name for i in swinf.channelInfo]
        chanInd = [chanNames.index(c) for c in chan]
        chanInf = [swinf.channelInfo[i] for i in chanInd]
        name = 'Sw_%s_in_%s_%s_sweeps_averaged'%(index,self.name,len(list_index))
        
        if cached_val is None:
            data = None
            if list_index:
                print 'Averaging in node %s ...'%self.name
                pbar = pgb.ProgressBar(maxval=len(list_index),term_width = 
                                        79).start()
                for i, ind in enumerate(list_index):
                    pbar.update(i)
                    in_sw = self.in_sweep(ind)
                    
                    if data is None:
                        data = in_sw._data
                    else:
                        data += in_sw._data
                data/= float(len(list_index))
                pbar.finish()
            else:
                data = np.array([])
            chan2ind = in_sw._name2index
        else:
            data, chan2ind = cached_val
        if data.size:
            chanInd = [chanNames.index(name)+1 for name in chan]
            out = Sweep(name = name, data = data[[0]+chanInd,:], chan_info 
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
            cached[key] = (data, chan2ind)
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
            for chan, chind in value[1].items():
                kwargs['_'.join((i,chan))] = value[0][[0,chind],:]
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
            sw,ch, ind = k.split('_')
            chind = ch+'_'+ind
            if not self._cache['cached'].has_key(sw):
                self._cache["cached"][sw] = [np.array(data[k][0], ndmin = 2), {}]
            if not force:
                if self._cache['cached'][sw][1].has_key(chind):
                    print 'Average already in cache. Use force to replace it'
                    continue
            assert all(data[k][0] == self._cache["cached"][sw][0][0])
            self._cache['cached'][sw][0] = np.vstack((self._cache["cached"][sw][0],
                                                      data[k][1]))
            indInCache = self._cache['cached'][sw][0].shape[0]-1
            self._cache['cached'][sw][1][chind] = indInCache
        
