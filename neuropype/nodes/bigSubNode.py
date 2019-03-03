# -*- coding: utf-8 -*-

# try:
#     import mdp
#     use_mdp = True
# except ImportError:
#     print 'mdp (modular data processing) module not installed. Cannot do PCA'
#     use_mdp = False

import numpy as np
from neuropype import node
from itertools import imap, repeat
from copy import deepcopy, copy
from neuropype import parameter
import os

# from bisect import bisect_left
# from neuropype.ressources._common import boxfilter, findextrema, cross_threshold
from neuropype.ressources._common import *
from neuropype.ressources.recurtime import recurtime
import neuropype.ressources.progressbar as pgb
from neuropype.datatypes import Time_list, Sweep
from neuropype.ressources._testMEC_func import *
# from neuropype.gui.lassoExempl import  LassoManager

class bigSubNode(node.Node):
    """Do everything in one node to see if it faster
    
    killIfNot1 set what to do if not a single spike is detected on one sweep
    win_baseline is in time relative to trace begining (so only positive values)
    """
    
    def __init__(self, name, parent):
        # Inputs
        self.in_sweep = node.Input(['Sweep', 'SweepData'])
        self.in_numSweeps = node.Input('int')
        self.in_chanNames = node.Input('list')
        self.in_origin = node.Input('list')
        self.in_tag = node.Input('list')
        self.in_sweepInfo = node.Input('SweepInfo')
        
        self.in0_times = node.Input('Time_list')
        self.in0_numSweeps = node.Input('int')
        self.in1_times = node.Input('Time_list')
        self.in1_numSweeps = node.Input('int')

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
        
        super(bigSubNode, self).__init__(name, parent)
        self._inputGroups = {'sweep': {'sweep': 'in_sweep',
                                       'numSweeps': 'in_numSweeps',
                                       'chanNames': 'in_chanNames',
                                       'origin': 'in_origin',
                                       'tag' : 'in_tag',
                                       'sweepInfo': 'in_sweepInfo'},
                             'time_list0': {'time_list':'in0_times',
                                            'numSweeps':'in0_numSweeps'},
                             'time_list1': {'time_list':'in1_times',
                                            'numSweeps':'in1_numSweeps'}
                             }
        
        self._outputGroups = {'time_list':  {'time_list': 'out_time',
                                             'numSweeps': 'out_numSweeps',
                                             'tag': 'out_tagTimeList'},
                              'sweep': {'sweep': 'out_sweep',
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
        # baseline = parameter.combobox('baseline', self, ['fixed', 'floating', 
        #                               'mean', 'window', None], 'floating')
        # fixed_baseline = parameter.float_param('fixed_baseline', self, 0, decimals= 9,
        #                                        singleStep= 1e-3)
        # createUniv = CreateUniv(self)
        # self.cU = createUniv
        
        # chan = parameter.combobox('chan', self, [], 'None', func = createUniv)
        # padding = parameter.combobox('padding', self, ['flatPad', 'zeroPad', 'keep'], 'flatPad')
        # win0 = parameter.float_param('win0', self, 5e-3, minVal= 0, decimals= 9,
        #                              singleStep= 1e-3)
        # win1 = parameter.float_param('win1', self, 1e-3, minVal= 0, decimals= 9,
        #                              singleStep= 1e-3)
        # win2 = parameter.float_param('win2', self, 1.5e-3, minVal= 0, decimals=
        #                              9, singleStep= 1e-3)
        # dt0 = parameter.float_param('dt0', self, 1.5e-3, minVal= 0, decimals=
        #                              9, singleStep= 1e-3)
        # dt1 = parameter.float_param('dt1', self, 1.5e-3, minVal= 0, decimals=
        #                              9, singleStep= 1e-3)
        # pointinterval = parameter.float_param('pointinterval', self, 1e-3, minVal= 0, decimals=
        #                              9, singleStep= 0.1e-3)
        # numWins = parameter.integer('numWins', self, 1, minVal= 1, maxVal= 3)
        # threshold = parameter.float_param('threshold', self, 0, decimals=
        #                              9, singleStep= 1e-3)
        # maximum = parameter.boolean('maximum', self, Default = True)
        # cross_threshold_param = parameter.boolean('cross_threshold', self, Default = False)
        
        self._params={'exclude4Field':(10e-3,10e-3),
                      'snipetWin':(-22e-3,22e-3),
                      'cleanSnip': (-5000,5000,'Ch_3'),
                      'shift': 22e-3,
                      'floatingWin_fast':.1e-3,
                      'win_baseline': (0e-3, 5e-3),
                      'floatingWin_slow': 5e-3,
                      'threshold': -250,
                      'maximum':False,
                      'pointinterval':.5e-3,
                      'chan': 'Ch_3',
                      'warningMem': 5,
                      'killIfNot1': True}
        #connecting outputs:
        # self.out_time.output = self.time_list
        # self.out_numSweeps.output = self.numSweeps
        # self.out_chanNames.output = self.chanNames
        # self.out_sweep.output = self.filteredSweep
        # self.out_origin.output = self.origin
        # self.out_tagTimeList.output = self.tag
        # self.out_sweepInfo.output = self.sweepInfo
        # self.out_numSpikes.output = self.numSpikes
        # self.out_snip_tag.output = self.snip_tag
        # self.out_snip.output = self.snippet
        # self.out_snip_origin.origin = self.snippet_origin
        # self.out_snip_sweepInfo.origin = self.snippet_sweepInfo
        # self.out_snip_chanNames.output = self.snippet_chanNames
        
        #initializing mec for multiprossecing:
        # not valid since python 0.12 I think. Anyway was useless until now
        # from IPython.kernel import client
        # try:
        #     self.mec = client.MultiEngineClient()
        #     self.map = self.mec.map
        #     self.mec.execute('import os; os.chdir("/import/nsr/blot/share/Python/neuropype")')
        #     self.mec.execute('from neuropype.ressources._testMEC_func import *')
        # except Exception:
        self.mec = None
        self.map = map

        
    def _cleanSweeps(self, list_sweep = None, shift = None):
        """bef and aft are the time excluded before and after, both are positive"""
        if list_sweep is None:
            list_sweep = np.arange(self.in0_numSweeps())
        bef, aft = self.get_param('exclude4Field')
        if bef is None and aft is None:
            return True
        time0 = getattr(self.parent, self.inputs['in0_times'][0]).all_times(list_sweep, groupbysweep = True)
        if shift is not None:
            time0 = [ti+shift for ti in time0]
        time1 = getattr(self.parent, self.inputs['in1_times'][0]).all_times(list_sweep, groupbysweep = True)
        N = len(time0)
        if self.mec is not None and N > len(self.mec.get_ids()):
            tempMap = self.map
        else:
            tempMap = map
        listOK = tempMap(cleanInt, time0, time1, [bef]*N, [aft]*N, [self.get_param('killIfNot1')]*N)
        return listOK

    
    def _snippet(self, list_sweep, chan, shift, okSpikes = None):
        """snipetWin is tbef, taft in absolute value (so bef negativ)"""
        if isinstance(chan, str):
            chan = [chan]
        # okSpikes = self._cleanSweeps(list_sweep, shift = shift)
        time0 = getattr(self.parent, self.inputs['in0_times'][0]).all_times(list_sweep, groupbysweep = True)
        if okSpikes is None:
            okSpikes = [np.ones(ti.size, dtype = 'bool') for ti in time0]
        if shift is not None:
            time0 = [ti+shift for ti in time0]
        w0,w1 = self.get_param('snipetWin')
        swInf = self.in_sweepInfo(list_sweep[0])
        dt = swInf.dt
        length = int((w1-w0)/dt)
        t0 = swInf.t0
        if self.in_sweep.source.Type == 'SweepData':
            dtype = 'int' 
            s = 16
        else:
            dtype = 'float'
            s = 64
        N = np.sum(flatenList(okSpikes))
        nchan =len(chan)
        size = float(64*N*nchan*length)/1024/1024/1024
        print "Total snippet array of at least %.2f Go"%size
        if size > self.get_param('warningMem'):
            test = raw_input("That seems like a lot of memory, do you want to proceed? (Y/n): ")
            while test not in ['Y', '', 'y', 'n', 'N']:
                test = raw_input("'y' for yes, 'n' for no")
            if test.lower() == 'n':
                return None
        out = np.zeros((N,nchan,length), dtype = dtype)
        count = 0
        for enu, (mask,spT) in enumerate(zip(okSpikes, time0)):
            sp = spT[mask]
            if not sp.size:
                continue
            ind = list_sweep[enu]
            sw = self.in_sweep(ind)
            ch_ind = [sw._name2index[i] for i in chan]
            data = sw._data
            for s in sp:
                beg = int((s-t0+w0)/dt)
                if beg+length> data.shape[1] or beg <0:
                    out[count] = self._createPadArray(data[ch_ind], beg, beg+length)
                else:
                    out[count] = data[ch_ind,beg:beg+length]
                count+=1
        cl = self.get_param('cleanSnip')
        if cl is not None:
            m,M, c = cl
            c = chan.index(c)
            out = out[np.logical_and(out[:,c,:].min(1)>m, out[:,c,:].max(1)<M)]
        return out
            
    def _createPadArray(self, data, indbeg, indend):
        ndim, nvalues = data.shape
        lastInd = nvalues - 1
        if nvalues == 0:
            # no data, return ones
            return np.ones((ndim,indend-indbeg))
        #creating pad head and tail
        if indbeg < 0:
            padBeg = np.ones((ndim, -indbeg))
            indbeg = 0
        else:
            padBeg = np.ones((ndim, 0))
        n = indend - lastInd
        if n > 0:
            padEnd = np.ones((ndim, n))
            indend = lastInd
        else:
            padEnd = np.ones((ndim, 0))
        
        firsts = np.array(data[:,indbeg], ndmin = 2).T
        lasts = np.array(data[:,indend], ndmin = 2).T
        if padBeg.size != 0: padBeg *= firsts
        if padEnd.size != 0: padEnd *= lasts
        out = data[:,indbeg:indend]
        out = np.hstack((padBeg, out, padEnd))
        return out


    def field(self, list_sweep = None, chan = None, returnAll = False):
        if list_sweep is None:
            list_sweep = np.arange(self.in0_numSweeps())
        if chan is None:
            chan = self.in_chanNames()
        if isinstance(chan, str):
            chan = [chan]
        shift = self.get_param('shift')
        okSpikes = self._cleanSweeps(list_sweep, shift = shift)
        shifted = self._snippet(list_sweep, chan, shift,okSpikes)
        med_shifted = np.mean(shifted.T-np.mean(shifted,2).T,2)
        okSpikes = self._cleanSweeps(list_sweep, shift = None)
        not_shifted = self._snippet(list_sweep, chan, None, okSpikes)
        med_not_shifted = np.mean(not_shifted.T-np.mean(not_shifted,2).T,2)
        if returnAll:
            return shifted, not_shifted, med_shifted.T, med_not_shifted.T, (med_not_shifted-med_shifted).T
        return (med_not_shifted-med_shifted).T
    
    def readytrace2detectAgain(self, list_sweep = None, chan = None, field = None, snippet = None):
        if list_sweep is None:
            list_sweep = np.arange(self.in0_numSweeps())
        if chan is None:
            chan = self.get_param('chan')
        if not isinstance(chan, str):
            print 'chan must be the name of one channel!'
            return
        if snippet is None:
            snippet = np.asarray(self._snippet(list_sweep, [chan], shift = None, okSpikes = None)[:,0,:], dtype = 'float')
        if field is None:
            field = self.field(list_sweep, [chan], False)[0]
        elif field is "brutal":
            field = snippet.mean(0)-snippet.mean()
        field = np.asarray(field, dtype = 'float')
        trace = np.asarray(snippet - field, dtype = 'float')
        cumsum = trace.cumsum(1)
        dt = self.in_sweepInfo(0).dt
        w_fast = int(self.get_param('floatingWin_fast')/dt)
        out_f = (cumsum[:,w_fast:]-cumsum[:,:-w_fast])/float(w_fast)
        win = [int(i/dt) for i in self.get_param('win_baseline')]
        if win is not None:
            wb,we = win
            out_f = (out_f.T - out_f[:,wb:we].mean(1)).T
        out = np.zeros_like(trace)
        w_slow = self.get_param('floatingWin_slow')
        if w_slow is not None:
            w_slow = int(w_slow/dt)
            out_b = (cumsum[:,w_slow:]-cumsum[:,:-w_slow])/float(w_slow)
            shft = w_slow - w_fast
            out[:,w_slow/2:-int(w_slow/2.+.5)] = out_f[:,shft/2:-int(shft/2.+.5)]-out_b
        else:
            out[:,w_fast/2:-int(w_fast/2.+.5)] = out_f
        return out
    
    def redetect(self, trace):
        m = self.get_param('maximum')
        th = self.get_param('threshold')
        dt = self.in_sweepInfo(0).dt
        point = int(self.get_param('pointinterval')/dt)
        times = two_dim_findextrema(trace, 1,m, th, point)
        return times
    
    def doubleDetect(self, list_sweep=None, chan =None, raw = False, snippet = None, field =None):
        if list_sweep is None:
            list_sweep = np.arange(self.in0_numSweeps())
        if chan is None:
            chan = self.get_param('chan')
        if snippet is None:
            snippet = self._snippet(list_sweep, [chan], shift = None, okSpikes = None)[:,0,:]
        trace_field = self.readytrace2detectAgain(list_sweep = list_sweep, chan = chan, field = field, snippet = snippet)
        time_field = self.redetect(trace_field)
        del trace_field
        trace_brutal = self.readytrace2detectAgain(list_sweep = list_sweep, chan = chan, field = "brutal", snippet = snippet)
        time_brutal = self.redetect(trace_brutal)
        del trace_brutal
        if raw:
            f = np.zeros(snippet.shape[1])
            trace_raw = self.readytrace2detectAgain(list_sweep = list_sweep, chan = chan, field = f, snippet = snippet)
            time_raw = self.redetect(trace_raw)
            del trace_raw
            return time_brutal, time_field, time_raw
        return time_brutal, time_field

    

"""
Usage:


dt = c.file.sweepInfo(0).dt
ct = np.arange(20)
lab = 'Gab'

chan = c.bigNode_P1.get_param('chan')
snp_ct1 = c.bigNode_P1._snippet(ct, chan, None)[:,0,:]
bord1 =(snp_ct1.min(), snp_ct1.max())
fi1 = c.bigNode_P1.field(ct, chan =chan)[0]
br1 = snp_ct1.mean(0)

#PLOTING FIELD:
time = (np.arange(fi1.size)*dt+c.bigNode_P1.get_param('snipetWin')[0])*1000
ax = fig.add_subplot(111)
ax.clear()
ax.plot(time,fi1, label = 'field', c= 'b')
ax.plot(time,br1-br1.mean(), label = 'STA', c = 'g')
ax.plot(time,fi1-(br1-br1.mean()), label = 'fi - STA', c = 'k')
ax.set_title('Field of %s P1 \n %s'%(line[0], lab))

ax.legend(loc = 0)
ax.set_xlim(-2,5)
ax.set_ylim(-30,200)


time_ct1 = c.bigNode_P1.doubleDetect(ct, chan, raw = True, snippet = snp_ct1, field =fi1)
s = c.bigNode_P1.get_param('snipetWin')[0]*1000
gau1 = [gaussian_density(tim[1]*dt*1000+s, sd = .5/3) for tim in time_ct1]

#PLOTING KDE

fig1.clear()
ax = fig1.add_subplot(111)
colors = ['b', 'g', 'orange']
labels = ['brutal', 'field', 'raw']
for i, g in enumerate(gau1):
   ax.plot(g[0], g[1], c = colors[i], label = labels[i])
ax.legend(loc = 0)
ax.vlines([0,0.47], *ax.get_ylim(), color = 'k')
ax.set_xlim(-10,10)
ax.set_ylim(auto = True)
ax.set_title('Gaussian KDE of %s P1 \n %s'%(line[0], lab))


"""
