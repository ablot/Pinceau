from neuropype import node
from neuropype.datatypes import Time_list
import numpy as np
#from itertools import imap

import neuropype.ressources.progressbar as pgb

class filter_ISI(node.Node):
    '''filter a time_list based on its Inter Spike Intervals
    
    max_ISI: maximal ISI before and after spike (there must be at least one 
             other spike in the max_ISI[0] seconds before and max_ISI[1] seconds
             after each spike)
             
    min_ISI: minimal ISI before and after spike (there must be 0 spike in the 
             min_ISI[0] secondes before and min_ISI[1] seconds after each spike)
             if you want to keep the only the first or last spike of the sweep
             set min_ISI[0] or [1] to np.inf
             
    border: policy for the first and last spikes. Can be 'ifOk', 'never' or
            'always'
            if 'ifOk', keep spikes only if all the conditions can be checked
            if 'never', throw the spikes
            if 'always', keep the spikes'''
    
    def __init__(self, name, parent):
        
        self.in_time = node.Input('Time_list')
        self.in_numSweeps = node.Input('int')
        self.in_tag_time_list = node.Input('list')
        
        self.out_time = node.Output('Time_list')
        self.out_numSweeps = node.Output('int')
        self.out_tag_time_list = node.Output('list')
        
        super(filter_ISI, self).__init__(name, parent)
        self._inputGroups['time_list'] = {'time_list': 'in_time',
        'numSweeps': 'in_numSweeps', 'tag': 'in_tag_time_list'}
        self._outputGroups['time_list'] = {'time_list': 'out_time',
        'numSweeps': 'out_numSweeps', 'tag': 'out_tag_time_list'}
        
        self._params={'min_ISI': [None,None], 'max_ISI': [None,None], 'border': 
                      'ifOk'}
        
        #connecting outputs:
        self.out_time.output = self.time_list
        self.out_numSweeps.output = self.numSweeps
        self.out_tag_time_list.output = self.tag
    
    def tag(self, index):
        out_tag = self.in_tag_time_list(index)
        return out_tag
    
    def createTag(self, tagName, universe = None, min_ISI = None, 
                  max_ISI = None, border = None, force = False):
        '''create a new tag instance (in self.parent.tagManager) with a given
        name
        
        universe can be a list of names
        min_ISI must be a list of tuple
        if force, erase preceding tags with same name'''
        
        #checking that name is a string beginning with alphabetical value
        tagName =str(tagName)
        if not tagName[0].isalpha():
            tagName = '_'+tagName
        if universe is None:
            universe = [tagName]
        else:
            if not isinstance(universe, list):
                raise IOError('Universe must be a list of str')
        
        #checking parameters
        params = [min_ISI, max_ISI]
        for ind, param in enumerate(params):
            if param is None:
                params[ind] = [[None,None]]*len(universe)
                
            elif len(universe) == 1 and len(param) == 2:
                params[ind] = [param]
            elif len(param) != len(universe):
                raise ValueError('len(%s) != len(universe)'%params[ind])
            elif any([len(i) !=2 for i in param]):
                raise ValueError('length of elements in %s must be 2'%
                                 params[ind])
        if border is None:
            border = ['ifOk' for i in universe]
        elif len(universe) == 1 and not isinstance(border, list):
            border =  [str(border)]
        else:
            border = [str(b) for b in border]
            
        tagType = self.parent.tagManager.add_tagType(tagName, universe, 
                                                     verbose = 0)
        if tagType is None: #tag already defined
            if not force:
                raise ValueError('tag already defined, use force to replace it')
            self.parent.tagManager.rmTag(tagName)
            tagType = self.parent.tagManager.add_tagType(tagName, universe, 
                                                         verbose = 1)
        min_ISI, max_ISI = params
        values = [[min_ISI[i], max_ISI[i], border[i]] for i in range(len(universe))]
        out = dict([(uni,values[i]) for i, uni in enumerate(universe)])
        self.tagCreated[tagType] = out
    
    def time_list(self, index_sweep, min_ISI = None, max_ISI = None):
        in_list = self.in_time(index_sweep)
        data = in_list._data
        size = data.size
        ISI = np.diff(data)
        correct = np.ones_like(data)
        
        if size == 0:
            name = 'FilteredSpikeOfSweep'+str(index_sweep)
            out = Time_list.Time_list(name, data, in_list.origin,
                                      in_list.SweepIndex, in_list.nodeOfSweep,
                                        title = 'NoTitle', units = 's')
            out.tag = self.in_tag_time_list(index_sweep)
            out.way = in_list.way
            return out
        # looking for tag:
        
     
        # adding params:
        if min_ISI is None:
            min_ISI = self.get_param('min_ISI')
        if max_ISI is None:
            max_ISI = self.get_param('max_ISI')
        border = self.get_param('border')
        tagged = self._isValid(size, ISI, min_ISI, max_ISI, border)
        correct = np.logical_and(correct, tagged)
        
        out_data = data[correct]
        name = 'FilteredSpikeOfSweep'+str(index_sweep)
        out = Time_list.Time_list(name, out_data, in_list.origin,
                                  in_list.SweepIndex, in_list.nodeOfSweep,
                                  title = 'NoTitle', units = 's')
        out.tag = self.in_tag_time_list(index_sweep)
        out.way = in_list.way
        return out
    
    def _save(self, txtfile):
        '''function used to add text to regenerate tags'''
        for tag, dictValue in self.tagCreated.iteritems():
            tagName = tag.__name__
            universe = []
            min_ISI = []
            max_ISI = []
            border = []
            for name, value in dictValue.iteritems():
                universe.append(name)
                min_ISI.append(value[0])
                max_ISI.append(value[1])
                border.append(value[2])
            txtfile.write('t.%s.createTag(\'%s\',%s,%s,%s, %s)\n'%(self.name,tagName,
                                            universe, min_ISI, max_ISI, border))
            
    
    
    def _isValid(self, size, ISI, min_ISI, max_ISI, border):
        min_bef, min_aft = min_ISI
        max_bef, max_aft = max_ISI
        if size > 2:#number of events
            #middle = data[1:-1]
            correct = (ISI < max_bef)[:-1] if max_bef is not None \
                           else np.ones(ISI.size -1, dtype = bool)
            if max_aft is not None:
                correct = np.logical_and(correct, (ISI < max_aft)[1:])
            if min_bef is not None:
                correct = np.logical_and(correct, (ISI > min_bef)[:-1])
            if min_aft is not None:
                correct = np.logical_and(correct, (ISI > min_aft)[1:])
            
            if border == 'always':
                correct = np.hstack((True, correct, True))
            elif border == 'never':
                correct = np.hstack((False, correct, False))
            else: #if border == 'ifOk':
                first, last = self._checkOk(min_bef, min_aft, max_bef, max_aft,
                                           ISI)
                correct = np.hstack((first, correct, last))
        elif size == 2:
            if border == 'always':
                correct = np.array([True, True])
            elif border == 'never':
                correct = np.array([False, False])
            else: #if border == 'ifOk' or smthg not recognised
                first, last = self._checkOk(min_bef, min_aft, max_bef, max_aft,
                                           ISI)
                correct = np.array([first, last])
        elif size ==1:
            if border == 'always': correct = np.array([True])
            elif border == 'never': correct = np.array([False])
            else: #if border == 'ifOk' or smthg not recognised
                correct = np.array([True])
                if (min_bef not in [np.inf, None]) or (min_aft not in [np.inf, 
                                                       None]):
                    correct = np.array([False])
                if (max_bef is not None) or (max_aft is not None):
                    correct = np.array([False])
        else: correct = None#size = 0
        return correct
    
    def all_times(self, list_sweep = None, groupbysweep = True):
        out = None
        if list_sweep is None:
            list_sweep = xrange(self.numSweeps())
        for i, sweep in enumerate(list_sweep):
            temp = self.time_list(sweep)._data
            if groupbysweep:
                if out is None:
                    out = [temp]
                else:
                    out.append(temp)
            else:
                if out is None:
                    out = temp
                else:
                    out = np.append(out, temp)
        return out
    
    def numSweeps(self):
        return self.in_numSweeps()
    def numSpikes(self, list_sweep = None):
        if list_sweep is None:
            list_sweep = xrange(self.numSweeps())
        pbar = pgb.ProgressBar(maxval=len(list_sweep), 
        term_width = 79).start()
        n=0
        for i, ind in enumerate(list_sweep):
            n += len(self.time_list(ind))
            pbar.update(i)
        pbar.finish()
        return n
        
    def _checkOk(self, min_bef, min_aft, max_bef, max_aft, ISI):
        first = True
        last = True
        if min_bef is not None:
            first = False if min_bef != np.inf else first
            last = ISI[-1] > min_bef
        if min_aft is not None:
            first = first and (ISI[0] > min_aft)
            last = False if min_aft != np.inf else last
        if max_bef is not None:
            first = False
            last = last and (ISI[-1] < max_bef)
        if max_aft is not None:
            first = first and (ISI[0] < max_aft)
            last = False
        return (first, last)
