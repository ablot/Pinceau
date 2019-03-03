from neuropype import node
from neuropype.datatypes.Time_list import Time_list
import numpy as np
#from itertools import imap
from copy import deepcopy
from neuropype.ressources._common import checkInput
#import neuropype.ressources.progressbar as pgb

class Tag_time(node.Node):
    '''Tag times from a time_list and return them one by one
    
    Parameters:

    - max_ISI: maximal ISI before and after spike (there must be at least one 
             other spike in the max_ISI[0] seconds before and max_ISI[1] seconds
             after each spike)
             
    - min_ISI: minimal ISI before and after spike (there must be 0 spike in the 
             min_ISI[0] secondes before and min_ISI[1] seconds after each spike)
             if you want to keep the only the first or last spike of the sweep
             set min_ISI[0] or [1] to np.inf
             
    - border: policy for the first and last spikes. Can be 'ifOk', 'never' or
            'always'
            if 'ifOk', keep spikes only if all the conditions can be checked
            if 'never', throw the spikes
            if 'always', keep the spikes

    TODO: change filter_ISI in a more general filter time list
    '''
    
    def __init__(self, name, parent):
        
        self.in_time = node.Input('Time_list')
        self.in_numSweeps = node.Input('int')
        self.in_tag_time_list = node.Input('list')
        
        self.out_time = node.Output('Time_list')
        self.out_numSweeps = node.Output('int')
        self.out_tag_time_list = node.Output('list')
        
        super(Tag_time, self).__init__(name, parent)
        self._inputGroups['time_list'] = {'time_list': 'in_time',
        'numSweeps': 'in_numSweeps', 'tag': 'in_tag_time_list'}
        self._outputGroups['time_list'] = {'time_list': 'out_time',
        'numSweeps': 'out_numSweeps', 'tag': 'out_tag_time_list'}

        self._params = {}
        self._cache = {'numSweeps': None,
                       'eqIndex':{},
                       'tagged':{}}
                       
        self._defined_condition = {'ISI_bef': ['max','min','border'],
                                   'ISI_aft': ['max','min','border'],
                                   'Value': ['max','min']}
        self._defaultDict = {'ISI_bef': [None, None, 'ifOk'],
                         'ISI_aft': [None, None, 'ifOk'],
                         'Value': [None, None]}
        self._data = {}
        #self._params={'min_ISI': [None,None], 'max_ISI': [None,None], 'border': 
                      ## 'ifOk'}
        
        #connecting outputs:
        self.out_time.output = self.time
        self.out_numSweeps.output = self.numSweeps
        self.out_tag_time_list.output = self.tag

    def dirty(self, dirty_list = 'all', verbose = 0):
        """dirty a node and linked outputs"""
        super(Tag_time,self).dirty(dirty_list, verbose)
        self._cache = {'numSweeps': None,
                       'eqIndex':{},
                       'tagged':{}}        

    def tagNames(self):
        """Names of the tag added by the node
        """
        return self._data.keys()

    def addTag(self, name, universe = [], force = 0):
        """Add one tag to the tagManager
        
        Arguments:
        - `name`: name of the tag, must start with alphabetical value
        - `universe`: values the tag can take
        - `force`: if True erase existing tag with the same name in tagManager
        """
        name = str(name)
        if not name[0].isalpha():
            name = '_'+name
        if not isinstance(universe, list):
            raise IOError('Universe must be a list')
        tgMg = self.parent.tagManager
        exist = name in tgMg.list_tag()
        if exist and not force:
            print 'Tag already defined'
            return
        elif exist:
            tgMg.rmTag(name)
        tgMg.add_tagType(name, universe)
        self._data[name]= dict([(u, deepcopy(self._defaultDict)) for u in universe])
    
    def changeTagUniverse(self, typeName, elementName):
        """if `elementName` in tag type `typeName`, delete if, else add it
        
        Arguments:
        - `tagName`: tag type name, must be in self.tagNames()
        - `elementName`: new element to add to the universe
        """

        if typeName not in self.tagNames():
            print 'Unknown tag type: %s'%typeName
            return
        tgMg = self.parent.tagManager
        univ = getattr(tgMg, typeName).universe
        if elementName in univ:
            univ.remove(elementName)
            self._data[typeName].pop(elementName)
        else:
            univ.append(elementName)
            self._data[typeName][elementName] =self._defaultDict
        tgMg.rmTag(typeName)
        tgMg.add_tagType(typeName, univ)
        return
    
    def properties(self, tagType, tagValue = None):
        """Return the current properties of a tag applied by the node
        
        Arguments:
        - `tagType`: name of the tagType
        - `tagValue`: name of the tagValue (must be in tagType.universe),
        if None, use all
        """
        if tagType not in self.tagNames():
            raise ValueError('Unknown tag type %s'%tagType)
        tagTypeDict = self._data[tagType]
        if tagValue is None:
            tagValue = tagTypeDict.keys()
        elif not isinstance(tagValue, list):
            tagValue = [tagValue]
        out = {}
        [out.setdefault(i, tagTypeDict[i]) for i in tagValue]
        return out
    
    def setProperty(self, tagType, tagValue = None, element = None, prop = None,
                    value = 'default', **kwargs):
        """Change the property of on tag.
        
        Arguments:
        - `tagType`: name of the tagType
        - `tagValue`: name of the tag, is an element of tagType.universe (or a
        list of such elements), if None, all the universe is changed
        - `element`: element to be changed, can be Value, ISI_bef or ISI_aft
        if None, all the properties are changed.
        - `prop`: property to be changed (ex min, max, border), if None and
        value is default, restore all the properties to default values
        - `value`: the new value, if default, restore default value
        TODO: - `kwargs`: other keyword arguments are read as prop = value
        """
        if tagType is None: raise ValueError('Invalid tagType')
        tagType, = checkInput(tagType, self._data.keys(), allIfNone = 0)
        tagDict = self._data[tagType]
        tagValue = checkInput(tagValue, tagDict.keys())
        element = checkInput(element, self._defined_condition.keys())
        
        if prop is None:
            if value != 'default':
                return
            [kwargs.setdefault(i, 'default') for i in self._defaultDict.keys()]
        else:
            if any([prop not in self._defined_condition[el] for el in element]):
                raise ValueError('An element has no prop: `%s`'%prop)
            kwargs[prop] = value

        for tag in tagValue:
            for el in element:
                for k,v in kwargs.iteritems():
                    index = self._defined_condition[el].index(k)
                    if v == 'default': v = self._defaultDict[el][k]
                    tagDict[tag][el][index] = v
        self.dirty('all')
        return
    
    def _save(self, textFile):
        """Function used when node saved to store created tags
        """
        for tagType in self._data.keys():
            univ = self._data[tagType].keys()
            textFile.write("t.%s.addTag('%s', %s)\n"%(self.name, tagType,
                                                        univ))
            for u in univ:
                base = "t.%s.setProperty('%s', '%s',"%(self.name, tagType,u)
                for element, v in self._data[tagType][u].iteritems():
                    for i, prop in enumerate(self._defined_condition[element]):
                        txt = base + "'%s', '%s',"%(element, prop)
                        if type(v[i]) == str: txt += "'%s'"%v[i]
                        else: txt += str(v[i])
                        txt += ")\n"                             
                        textFile.write(txt)

    def _tagSweep(self, index, startIndex = None):
        """add in cache tags for one sweep

        Arguments: 
        - `index`: index of the sweep to tag
        """
        time_list = self.in_time(index)._data
        ISI = np.diff(time_list)
        if startIndex is None:
            startIndex = self.findSpikeIndexFromSweep(index)
        indices = np.arange(len(time_list))
        [self.set_cache(i, []) for i in indices+startIndex]
        for tagTypeName, tagTypeDict in self._data.iteritems():
            #iteration on universe:
            value = [[] for i in indices]
            for tagName, tagDict in tagTypeDict.iteritems():
                isValid = self._isValid(time_list, ISI, tagDict)
                [value[i].append(tagName) for i in indices[isValid]]
            tagType = getattr(self.parent.tagManager, tagTypeName)
            for i in indices:
                if value[i] == []:
                    continue
                tag = tagType(name = 'Tagged_by_'+self.name, value = value[i])
                self._cache[i+startIndex].append(tag)
        return

    def _isValid(self, time_list, ISI, propDict):
        """check if time agree with prop
        """
        if len(time_list) < 1:
            return np.array([])
        correct = np.ones(time_list.size, dtype = bool)
        
        maxValue, minValue = propDict['Value']
        if minValue is not None:
            correct = np.logical_and(correct, time_list > minValue)
        if maxValue is not None:
            correct = np.logical_and(correct, time_list < maxValue)
        
        maxValue, minValue, border = propDict['ISI_bef']
        if len(time_list) > 1:
            if minValue is not None:
                correct[1:] = np.logical_and(correct[1:], ISI > minValue)
            if maxValue is not None:
                correct[1:] = np.logical_and(correct[1:], ISI < maxValue)
        if border == 'always':
            pass
        elif border == 'never':
            correct[0] = 0
        elif border == 'ifOk':
            if maxValue is not None:
                correct[0] = 0
            elif minValue not in [None, np.inf]:
                correct[0] = 0
                
        maxValue, minValue, border = propDict['ISI_aft']
        if len(time_list) > 1:
            if minValue is not None:
                correct[:-1] = np.logical_and(correct[:-1], ISI > minValue)
            if maxValue is not None:
                correct[:-1] = np.logical_and(correct[:-1], ISI < maxValue)
        if border == 'always':
            pass
        elif border == 'never':
            correct[-1] = 0
        elif border == 'ifOk':
            if minValue is not None:
                correct[-1] = 0
            elif maxValue not in [None, np.inf]:
                correct[-1] = 0
        return correct
      
    def numSweeps(self, list_index = None):
        """Number of sweeps in node.

        Is equal to the number of times in input `in_time`
        
        Arguments:
        - `list_index`: input time_list to consider, if None, use all the inputs
        """
        keep = 0
        if list_index is None:
            keep = 1
            if self.get_cache('numSweeps') is not None:
                return int(self.get_cache('numSweeps'))
            list_index = range(self.in_numSweeps())

        numSpikes = 0
        
        for index in list_index:
            numSpikes += len(self.in_time(index))
        if keep: self.set_cache('numSweeps', numSpikes, force = 1)
        return numSpikes

    def findFromSpikeIndex(self, index):
        """Return the index of the sweep and the index of the spike in this sweep
        corresponding to time `index`
        
        Arguments:
        - `index`: an integer in [0, self.numSweeps()-1]
        """
        eqInd = self.get_cache('eqIndex')

        ind = eqInd.get(index)
        if ind is not None:
            return int(ind[0]), int(ind[1])
        
        n = 0
        ind_sweep = 0
        while n <= index:
            numSpikes = len(self.in_time(ind_sweep))
            tempDict = dict([(i+n, (ind_sweep, i)) for i in range(numSpikes)])
            eqInd.update(tempDict)
            n += numSpikes
            ind_sweep += 1
            
        ind_sweep, ind_spike = eqInd.get(index)
        self.set_cache('eqInd', eqInd, force =1)
        return int(ind_sweep), int(ind_spike)

    def findSpikeIndexFromSweep(self, sweep_index):
        """Return the index (in this node) of the first spike of sweep `sweep_index`
        in the input node
        
        Arguments:
        - `index`: an integer in [0, self.in_numSweeps()-1]
        """
        eqInd = self.get_cache('eqIndex')
        # look if spike index is already in cache
        key = sorted(eqInd.keys())
        sweeps = [eqInd[k][0] for k in key]
        if sweep_index in sweeps:
            ind = sweeps.index(sweep_index)
            #check that this is the first spike of sweep `sweep_index`
            spike_ind = key[ind]
            while self.findFromSpikeIndex(spike_ind-1)[0] == sweep_index:
                spike_ind -= 1
            return spike_ind
        
        current_sw_index = 0
        spike_index = 0
        while current_sw_index < sweep_index:
            numSpikes = len(self.in_time(current_sw_index))
            tempDict = dict([(i+spike_index ,(current_sw_index, i))
                                            for i in range(numSpikes)])
            eqInd.update(tempDict)
            current_sw_index += 1
            spike_index += numSpikes
        self.set_cache('eqInd', eqInd, force =1)            
        return spike_index

    def tag(self, index):
        """Return the tags of time `index`
        
        Arguments:
        - `index`: index to consider, integer < self.numSweeps
        """
        cached = self.get_cache(index)
        sweepIndex, indexInSweep = self.findFromSpikeIndex(index)
        if cached is None:
            self._tagSweep(sweepIndex)
        inTag = self.in_tag_time_list(sweepIndex)
        outTag = inTag + self._cache[index]
        return outTag

    def time(self, index):
        """Return the time at `index`
        
        Arguments:
        - `index`: index to consider, integer < self.numSweeps
        """
        sweepIndex, indexInSweep = self.findFromSpikeIndex(index)
        name = 'Time_%s_in_%s'%(index,self.name)
        time_list = self.in_time(sweepIndex)
        data = np.array(time_list._data[indexInSweep], ndmin = 1)
        origin = time_list.origin
        title = 'Spike_%s_in_sw_%s_tagged'%(indexInSweep, sweepIndex)
        out = Time_list(name, data, origin, sweepIndex, time_list.nodeOfSweep,
                        title = title, units = 's')
        out.tag = self.tag(index)
        out.way = time_list.way + [self.name]
        return out
        

    ## def tag(self, index, tag = None):
    ##     out_tag = self.in_tag_time_list(index, tag =tag)
    ##     if tag is not None:
    ##         if not isinstance(tag, list):
    ##             tag = [tag]
    ##         tag2Handle = [tg for tg in tag if type(tg) in self.tagCreated.keys()]
    ##         out_tag += tag2Handle
    ##     return out_tag
    
    ## def createTag(self, tagName, universe = None, min_ISI = None, 
    ##               max_ISI = None, border = None, force = False):
    ##     '''create a new tag instance (in self.parent.tagManager) with a given
    ##     name
        
    ##     universe can be a list of names
    ##     min_ISI must be a list of tuple
    ##     if force, erase preceding tags with same name'''
        
    ##     #checking that name is a string beginning with alphabetical value
    ##     tagName =str(tagName)
    ##     if not tagName[0].isalpha():
    ##         tagName = '_'+tagName
    ##     if universe is None:
    ##         universe = [tagName]
    ##     else:
    ##         if not isinstance(universe, list):
    ##             raise IOError('Universe must be a list of str')
        
    ##     #checking parameters
    ##     params = [min_ISI, max_ISI]
    ##     for ind, param in enumerate(params):
    ##         if param is None:
    ##             params[ind] = [[None,None]]*len(universe)
                
    ##         elif len(universe) == 1 and len(param) == 2:
    ##             params[ind] = [param]
    ##         elif len(param) != len(universe):
    ##             raise ValueError('len(%s) != len(universe)'%params[ind])
    ##         elif any([len(i) !=2 for i in param]):
    ##             raise ValueError('length of elements in %s must be 2'%
    ##                              params[ind])
    ##     if border is None:
    ##         border = ['ifOk' for i in universe]
    ##     elif len(universe) == 1 and not isinstance(border, list):
    ##         border =  [str(border)]
    ##     else:
    ##         border = [str(b) for b in border]
            
    ##     tagType = self.parent.tagManager.add_tagType(tagName, universe, 
    ##                                                  verbose = 0)
    ##     if tagType is None: #tag already defined
    ##         if not force:
    ##             raise ValueError('tag already defined, use force to replace it')
    ##         self.parent.tagManager.rmTag(tagName)
    ##         tagType = self.parent.tagManager.add_tagType(tagName, universe, 
    ##                                                      verbose = 1)
    ##     min_ISI, max_ISI = params
    ##     values = [[min_ISI[i], max_ISI[i], border[i]] for i in range(len(universe))]
    ##     out = dict([(uni,values[i]) for i, uni in enumerate(universe)])
    ##     self.tagCreated[tagType] = out
    
    ## def time_list(self, index_sweep, min_ISI = None, max_ISI = None, tag=None):
    ##     if tag is None:
    ##         tag = []
    ##     elif not isinstance(tag, list):
    ##         tag = [tag]
    ##     tag2Handle = [tg for tg in tag if type(tg) in self.tagCreated.keys()]
    ##     tag2pass = tag[:]
    ##     [tag2pass.remove(tg) for tg in tag2Handle]
    ##     in_list = self.in_time(index_sweep, tag = tag2pass)
    ##     data = in_list._data
    ##     size = data.size
    ##     ISI = np.diff(data)
    ##     correct = np.ones_like(data)
        
    ##     if size == 0:
    ##         name = 'FilteredSpikeOfSweep'+str(index_sweep)
    ##         out = Time_list.Time_list(name, data, in_list.origin, 
    ##                                     title = 'NoTitle', units = 's')
    ##         out.tag = self.in_tag_time_list(index_sweep, tag = tag2pass)
    ##         out.way = in_list.way
    ##         return out
    ##     # looking for tag:
        
    ##     for tg in tag2Handle:
    ##         tagType = type(tg)
    ##         if self.tagCreated.get(tagType) is None:
    ##             print 'type %s from neuropype.tag %s not recognised, will be ignored'%(
    ##                   tagType, tg.name)
    ##             continue
    ##         tagged = np.zeros_like(data)
    ##         for value in tg.value:
    ##             if self.tagCreated[tagType].get(value) is None:
    ##                 print 'tag value %s not recognised, will be ignored'%value
    ##                 continue
    ##             min_ISI, max_ISI, border = self.tagCreated[tagType][value]
    ##             #print  '_______________'
    ##             #print size
    ##             tagged_value = self._isValid(size, ISI, min_ISI, max_ISI, border)
    ##             #print len(tagged_value)
    ##             tagged = np.logical_or(tagged, tagged_value)
    ##         correct = np.logical_and(correct, tagged)
        
    ##     # adding params:
    ##     if min_ISI is None:
    ##         min_ISI = self.get_param('min_ISI')
    ##     if max_ISI is None:
    ##         max_ISI = self.get_param('max_ISI')
    ##     border = self.get_param('border')
    ##     tagged = self._isValid(size, ISI, min_ISI, max_ISI, border)
    ##     correct = np.logical_and(correct, tagged)
        
    ##     out_data = data[correct]
    ##     name = 'FilteredSpikeOfSweep'+str(index_sweep)
    ##     out = Time_list.Time_list(name, out_data, in_list.origin, 
    ##                               title = 'NoTitle', units = 's')
    ##     out.tag = self.in_tag_time_list(index_sweep, tag = tag2pass)
    ##     [out.tag.append(tg) for tg in tag2Handle]
    ##     out.way = in_list.way
    ##     return out
    
    ## def _save(self, txtfile):
    ##     '''function used to add text to regenerate tags'''
    ##     for tag, dictValue in self.tagCreated.iteritems():
    ##         tagName = tag.__name__
    ##         universe = []
    ##         min_ISI = []
    ##         max_ISI = []
    ##         border = []
    ##         for name, value in dictValue.iteritems():
    ##             universe.append(name)
    ##             min_ISI.append(value[0])
    ##             max_ISI.append(value[1])
    ##             border.append(value[2])
    ##         txtfile.write('t.%s.createTag(\'%s\',%s,%s,%s, %s)\n'%(self.name,tagName,
    ##                                         universe, min_ISI, max_ISI, border))
            
    
    
    ## def _isValid(self, size, ISI, min_ISI, max_ISI, border):
    ##     min_bef, min_aft = min_ISI
    ##     max_bef, max_aft = max_ISI
    ##     if size > 2:#number of events
    ##         #middle = data[1:-1]
    ##         correct = (ISI < max_bef)[:-1] if max_bef is not None \
    ##                        else np.ones(ISI.size -1, dtype = bool)
    ##         if max_aft is not None:
    ##             correct = np.logical_and(correct, (ISI < max_aft)[1:])
    ##         if min_bef is not None:
    ##             correct = np.logical_and(correct, (ISI > min_bef)[:-1])
    ##         if min_aft is not None:
    ##             correct = np.logical_and(correct, (ISI > min_aft)[1:])
            
    ##         if border == 'always':
    ##             correct = np.hstack((True, correct, True))
    ##         elif border == 'never':
    ##             correct = np.hstack((False, correct, False))
    ##         else: #if border == 'ifOk':
    ##             first, last = self._checkOk(min_bef, min_aft, max_bef, max_aft,
    ##                                        ISI)
    ##             correct = np.hstack((first, correct, last))
    ##     elif size == 2:
    ##         if border == 'always':
    ##             correct = np.array([True, True])
    ##         elif border == 'never':
    ##             correct = np.array([False, False])
    ##         else: #if border == 'ifOk' or smthg not recognised
    ##             first, last = self._checkOk(min_bef, min_aft, max_bef, max_aft,
    ##                                        ISI)
    ##             correct = np.array([first, last])
    ##     elif size ==1:
    ##         if border == 'always': correct = np.array([True])
    ##         elif border == 'never': correct = np.array([False])
    ##         else: #if border == 'ifOk' or smthg not recognised
    ##             correct = np.array([True])
    ##             if (min_bef not in [np.inf, None]) or (min_aft not in [np.inf, 
    ##                                                    None]):
    ##                 correct = np.array([False])
    ##             if (max_bef is not None) or (max_aft is not None):
    ##                 correct = np.array([False])
    ##     else: correct = None#size = 0
    ##     return correct
    
    ## def all_times(self, list_sweep = None, groupbysweep = True, tag = None):
    ##     out = None
    ##     if list_sweep is None:
    ##         list_sweep = xrange(self.numSweeps())
    ##     for i, sweep in enumerate(list_sweep):
    ##         temp = self.time_list(sweep)._data
    ##         if groupbysweep:
    ##             if out is None:
    ##                 out = [temp]
    ##             else:
    ##                 out.append(temp)
    ##         else:
    ##             if out is None:
    ##                 out = temp
    ##             else:
    ##                 out = np.append(out, temp)
    ##     return out
    
    ## def numSweeps(self, tag = None):
    ##     return self.in_numSweeps(tag = tag)

    ## def numSpikes(self, list_sweep = None, tag = None):
    ##     if list_sweep is None:
    ##         list_sweep = xrange(self.numSweeps())
    ##     pbar = pgb.ProgressBar(maxval=len(list_sweep), 
    ##     term_width = 79).start()
    ##     n=0
    ##     for i, ind in enumerate(list_sweep):
    ##         n += len(self.time_list(ind, tag = tag))
    ##         pbar.update(i)
    ##     pbar.finish()
    ##     return n
        
    ## def _checkOk(self, min_bef, min_aft, max_bef, max_aft, ISI):
    ##     first = True
    ##     last = True
    ##     if min_bef is not None:
    ##         first = False if min_bef != np.inf else first
    ##         last = ISI[-1] > min_bef
    ##     if min_aft is not None:
    ##         first = first and (ISI[0] > min_aft)
    ##         last = False if min_aft != np.inf else last
    ##     if max_bef is not None:
    ##         first = False
    ##         last = last and (ISI[-1] < max_bef)
    ##     if max_aft is not None:
    ##         first = first and (ISI[0] < max_aft)
    ##         last = False
    ##     return (first, last)
