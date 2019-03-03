# -*- coding: utf-8 -*-

from neuropype import node
#from neuropype.datatypes.Sweep import Sweep
import numpy as np
#from neuropype.datatypes import Time_list, Sweep
#from neuropype.ressources._common import boxfilter, findextrema, cross_threshold
#import neuropype.ressources.progressbar as pgb
#from neuropype import tag as tagModule

#from neuropype import parameter


class TagCreator(node.Node):
    '''Stupid tag creator
    
    tagName is the name of the tag you want to create
    
    tagUniverse is a dict whose keys are the name of the different
    values that tagName can take (tag_0, tag_1 ... tag_n or simply True False).
    The values of this dict are list of indices to tag with that peculiar tag 
    (not necessarily exclusive)'''
    
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
        
        super(TagCreator, self).__init__(name, parent)
        
        self._inputGroups['sweep'] = {'sweep': 'in_sweep', 'numSweeps': 
        'in_numSweeps', 'chanNames': 'in_chanNames', 'origin': 'in_origin',
        'tag' : 'in_tag','sweepInfo': 'in_sweepInfo'}
        self._outputGroups['sweep'] = {'sweep': 'out_sweep', 
        'numSweeps': 'out_numSweeps', 'chanNames': 'out_chanNames',
        'origin': 'out_origin', 'tag' : 'out_tag', 'sweepInfo': 'out_sweepInfo'}
        
        #connecting outputs:
        self.out_numSweeps.output = self.numSweeps
        self.out_sweep.output = self.sweep
        self.out_chanNames.output = self.chanNames
        self.out_origin.output = self.origin
        self.out_tag.output = self.tag
        self.out_sweepInfo.output = self.sweepInfo
        
        #defining parameters:
        
        self._params = {'tagName' : None,
                        'tagUniverse': {}}
    
    
    def numSweeps(self):
        return self.in_numSweeps()
    
    
    def chanNames(self, index = 0):
        return self.in_chanNames(index)
    
    def _createTagArray(self):
        tagU = self.get_param('tagUniverse')
        array = np.zeros((self.numSweeps(),len(tagU)),
                         dtype ='bool')
        ind = []
        for i, (name, value) in enumerate(tagU.iteritems()):
            ind.append(name)
            array[value,i]+=1
        self.set_cache('array', array)
        self.set_cache('ind', ind)
        return array, ind
    
    def _createTagType(self):
        name = self.get_param('tagName')
        universe = self.get_param('tagUniverse').keys()
        self.parent.tagManager.add_tagType(name, universe, verbose =0)

    def _tagVal(self, index):
        if not self._cache.has_key('array'):
            self._createTagArray()
        ind = self._cache['ind']
        array = self._cache["array"][index]
        return [n for i, n in enumerate(ind) if array[i]]

    def tag(self, index):
        
        tag = self.in_tag(index)
        tgMg=self.parent.tagManager
        name = self.get_param('tagName')
        if not hasattr(tgMg, name):
            self._createTagType()
        
        
        tg = tgMg.tagInstance(name, self.name+'_%s'%index, self._tagVal(index))
        tag.append(tg)
        return tag
    
    def sweep(self, index, chan = None):
        sw = self.in_sweep(index, chan)
        sw.tag = self.tag(index)
        return sw

    def sweepInfo(self, index):
        return self.in_sweepInfo(index)
    
    def origin(self, index):
        return self.in_origin(index)+[self.name]
