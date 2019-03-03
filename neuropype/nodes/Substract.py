from neuropype import node
#from neuropype.datatypes import Sweep
from numpy import logical_and, vstack
from neuropype import tag as tagModule

class Substract(node.Node):
    '''substract trace1 to trace0 (out = trace0 - trace1)
    
    if self.in_sweep_index is None (default):
          out[i] = trace0[i] - trace1[1]
    else:
          out[i] = trace0[i] - trace1[int(self.in_sweep_index(i))]
    
    if the channel to substract is different from the channel substracted, 
    change params['chan_substracted']
    
    TODO: change cache policy!!!
    '''
    
    def __init__(self, name, parent):
        self.in_trace1 = node.Input('Sweep')
        self.in_numSweeps1 = node.Input('int')
        self.in_chanNames1 = node.Input('list')
        self.in_origin1 = node.Input('list')
        self.in_tag1 = node.Input('list')
        self.in_sweepInfo1 = node.Input('SweepInfo')
        
        self.in_trace0 = node.Input('Sweep')
        self.in_numSweeps0 = node.Input('int')
        self.in_chanNames0 = node.Input('list')
        self.in_origin0 = node.Input('list')
        self.in_tag0 = node.Input('list')
        self.in_sweepInfo0 = node.Input('SweepInfo')
        
        self.out_sweep = node.Output('Sweep')
        self.out_numSweeps = node.Output('int')
        self.out_chanNames = node.Output('list')
        self.out_origin = node.Output('list')
        self.out_tag = node.Output('list')
        self.out_sweepInfo = node.Output('SweepInfo')
        
        super(Substract, self).__init__(name, parent)
        
        self._inputGroups['trace1Gr'] = {'sweep': 'in_trace1', 
                                         'numSweeps': 'in_numSweeps1', 
                                         'chanNames': 'in_chanNames1', 
                                         'origin': 'in_origin1', 
                                         'tag': 'in_tag1',
                                         'sweepInfo': 'in_sweepInfo1'}
        
        self._inputGroups['trace0Gr'] = {'sweep': 'in_trace0', 
                                         'numSweeps': 'in_numSweeps0', 
                                         'chanNames': 'in_chanNames0',
                                         'origin': 'in_origin0', 
                                         'tag': 'in_tag0',
                                         'sweepInfo': 'in_sweepInfo0'}
        
        self._outputGroups['sweep']={'sweep': 'out_sweep',
                                     'numSweeps': 'out_numSweeps',
                                     'chanNames': 'out_chanNames',
                                     'origin': 'out_origin',
                                     'tag': 'out_tag',
                                     'sweepInfo': 'out_sweepInfo'}
        
        self._params = {'verbose': 1,
                        'chan_substracted':None,
                        'use_part' : False,
                        'part' : {'substract':['begin','end'],
                                  'from': ['begin','end']},
                        'graphviz':{'style': 'filled', 'fillcolor': 'lightcyan'},
                        'ind2sub': None,
                        'tag2keep': 2}
        
        #connecting outputs:
        self.out_sweep.output = self.sweep
        self.out_numSweeps.output = self.numSweeps
        self.out_chanNames.output = self.chanNames
        self.out_origin.output = self.origin
        self.out_tag.output = self.tag
        self.out_sweepInfo.output = self.sweepInfo
    
    def numSweeps(self):
        return self.in_numSweeps0()
    
    def chanNames(self, index = 0):
        return self.in_chanNames0(index)
        
    def sweepInfo(self, index):
        swInf = self.in_sweepInfo0(index)
        return swInf
    
    def origin(self, index_sweep):
        in_ori = self.in_origin0(index_sweep)
        
        if self.get_param('ind2sub') is None:
            index = index_sweep
        else:
            index = self.get_param('ind2sub')
            if not isinstance(index, int):
                index = int(index[index_sweep])
        sub_ori = self.in_origin1(index)
        return [in_ori, ['minus'].append(sub_ori)]
    
    def tag(self, index, AND  = 1, OR = 1):
        '''Return the tags associated with the substracted traces

        params['tag2keep'] define wich tag to use. 0 for trace 0, 1 for trace 1,
        2 for both.
        If 2, tags are combined according to args AND and OR:
        
        if AND: return tags present in both the substracted trace and the trace
                used to substract
        if OR:  return tags present in either the substracted trace or the trace
                used to substract'''
        tag2keep = self.get_param('tag2keep')
        if tag2keep == 0:
            return self.in_tag0(index)
        elif tag2keep ==1:
            return self.in_tag1(index)
        tag0 = self.in_tag0(index)
        
        if self.get_param('ind2sub') is None:
            ind1 = index
        else:
            ind1 = self.get_param('ind2sub')
            if not isinstance(ind1, int):
                ind1 = int(ind1[index])
        tag1 = self.in_tag1(ind1)
        return tagModule.combine(tag0, tag1, AND  = 1, OR = 1)
    
    def sweep(self, index_sweep, chan = None):
        if chan is None:
            chan = self.chanNames()
        
        sweep = self.in_trace0(index_sweep, chan)
        chan_substracted = self.get_param('chan_substracted')
        if chan_substracted is None:
            chan_substracted = chan
        if self.get_param('ind2sub') is None:
            index = index_sweep
            sub = self.in_trace1(index, chan)
        else:
            index = self.get_param('ind2sub')
            if not isinstance(index, int):
                index = int(index[index_sweep])
            sub = self.get_cache('sub'+'_'+str(chan))
            if sub is None:
                sub = self.in_trace1(index, chan)
                self.set_cache('sub'+'_'+str(chan),sub)
            
        
        if self.get_param('use_part'):
            raise NotImplementedError
            p = self.get_param['part']
            if p['substract'][0] == 'begin':
                p['substract'][0] = sub._data[0][0]
            if p['substract'][1] == 'end':
                p['substract'][1] = sub._data[0][-1]
            if p['from'][0] == 'begin':
                p['from'][0] = sweep._data[0][0]
            if p['from'][1] == 'end':
                p['from'][1] = sweep._data[0][-1]
            part2substract = logical_and('TODO')
            return 'somestuff'
        data = sweep._data[1:]-sub._data[1:]
        data = vstack((sweep._data[0], data))
        sweep._data = data
        tag = self.tag(index)
        sweep.tag = tag
        return sweep
        
        
