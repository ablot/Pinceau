# -*- coding: utf-8 -*-

#TODO:  convert fixed sampling rate assumption to variable rate.
#       many more measures to add (rise, decay, peak search)
import numpy as np
from neuropype import node
from neuropype import parameter
from neuropype.datatypes import Sweep

class Synaptix(node.Node):
    def __init__(self, name, parent):
        self.in_sweep = node.Input('Sweep')
        self.in_numSweeps = node.Input('int')
        self.in_chanNames = node.Input('list')
        self.in_origin = node.Input('list')
        self.in_tag = node.Input('list')
        self.in_sweepInfo = node.Input('SweepInfo')
        
        self.out_amp1 = node.Output('list')
        self.out_amp2 = node.Output('list')
        self.out_amp3 = node.Output('list')
        self.out_baseline1 = node.Output('list')
        # rise, decay times
        # fits ?

        super(Synaptix, self).__init__(name, parent)
        self._inputGroups['sweep'] = {'sweep': 'in_sweep',
                                      'numSweeps': 'in_numSweeps',
                                      'chanNames': 'in_chanNames',
                                      'origin': 'in_origin',
                                      'tag' : 'in_tag',
                                      'sweepInfo': 'in_sweepInfo'}
        
        self._params = {'chan': 'Ch_0',
                        'tag': None,
                        'baseline1_centre': None,
                        #'baseline1_search_half_width': None,
                        'baseline1_mean_half_width': 0,
                        #'baseline1_max': True,
                        'baseline2_centre': None,
                        #'baseline2_search_half_width': None,
                        'baseline2_mean_half_width': 0,
                        #'baseline2_max': True,
                        'baseline3_centre': None,
                        #'baseline3_search_half_width': None,
                        'baseline3_mean_half_width': 0,
                        #'baseline3_max': True,
                        'amp1_centre': None,
                        'amp1_mean_half_width': 0,
                        'amp2_centre': None,
                        'amp2_mean_half_width': 0,
                        'amp3_centre': None,
                        'amp3_mean_half_width': 0,
            }
        
        #connecting outputs:
        # Format: self.out_outName.output = one of your methods.
        self.out_amp1.output = self.amp1
        self.out_amp2.output = self.amp2        
        self.out_amp3.output = self.amp3        
        self.out_baseline1.output = self.baseline1

# Corresponding method definitions.

    def _measure(self, sweep, ampNum, si):
        """Measure relative amplitude relative to a baseline. 
        
        sweep is just the data of the correct channel as an array. ampNum identifies the amplitude to calculate. si is the sampling interval used to calculate the half widths in points."""
        c = np.cumsum(sweep)
        if ampNum==1:
            bc=int(self._params['baseline1_centre']/si)
            bmhw=int(self._params['baseline1_mean_half_width']/si)
            ac=int(self._params['amp1_centre']/si)
            amhw=int(self._params['amp1_mean_half_width']/si)
            #mx=self._params['baseline1_max']
        elif ampNum==2:
            bc=int(self._params['baseline2_centre']/si)
            bmhw=int(self._params['baseline2_mean_half_width']/si)
            ac=int(self._params['amp2_centre']/si)
            amhw=int(self._params['amp2_mean_half_width']/si)
            #mx=self._params['baseline2_max']
        else: # ampNum==3
            bc=int(self._params['baseline3_centre']/si)
            bmhw=int(self._params['baseline3_mean_half_width']/si)
            ac=int(self._params['amp3_centre']/si)
            amhw=int(self._params['amp3_mean_half_width']/si)
            #mx=self._params['baseline3_max']
        b=(c[bc+bmhw]-c[bc-bmhw-1])/(2*bmhw+1)
        a=(c[ac+amhw]-c[ac-amhw-1])/(2*bmhw+1)
        return (b,a)
        
            
    def _out_amp(self, ampNum, index=None):
        if index:
            s = self.in_sweep(index)
            #i = self.in_sweepInfo(index)
            sw = s.get_data(self._params['chan'])
            si = sw[0][1]
            m = self._measure(sw[1], ampNum, si)
            return ([m[1], m[0]])
        else:
            n = self.in_numSweeps()
            a = np.zeros(n)
            b = np.zeros(n)
            for i in range(n):
                if self.in_tag(i) == self._params['tag']:
                    sw = s.get_data(self._params['chan'])
                    si = sw[1]
                    m = self._measure(sw[1],ampNum,si)
                    a[i] = m[1]
                    b[i] = m[0]
                else:
                    a[i] = np.nan
                    b[i] = np.nan
            return (a,b)
            
    def amp1(self, index=None):
        a, b = self._out_amp(1,index)
        return a - b
        
    def amp2(self, index=None):
        a, b = self._out_amp(2,index)
        return a - b
        
    def amp3(self, index=None):
        a, b = self._out_amp(3,index)
        return a - b
        
    def baseline1(self, index=None):
        a, b = self._out_amp(1,index)
        return b        
