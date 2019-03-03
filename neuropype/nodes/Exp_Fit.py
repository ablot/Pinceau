from neuropype import node

import neuropype.ressources.progressbar as pgb
#from neuropype import tag as tagModule
from scipy.optimize import fmin_l_bfgs_b
import numpy as np

##debuging tool!
#from IPython.Shell import IPShellEmbed
#banner = '\n*** Nested interpreter *** \n\nYou are now in a nested ipython'
#exit_msg = '*** Closing embedded IPython ***'
##paramv = ['-noconfirm_exit', '-pi1','Neuropype In <\\#>:','-pi2','     .\\D.:','-po','Out<\\#>:']
#paramv = ['-pi1','Neuropype In <\\#>:','-pi2','     .\\D.:','-po','Out<\\#>:']
#ipshell = IPShellEmbed(paramv, banner=banner,exit_msg=exit_msg)
##end of debuging tool

class Exp_Fit(node.Node):
    '''Fit synaptique event with two exponentials 
    
    baseline can be None, 'Free', 'window' or any float, 
    if None use the mean value of the whole trace as baseline, 
    if 'Free', add a parameter to the Fit
    if 'window', use the mean value of the trace in 'baseline_window' (in ms)
    
    type can ben 'mono', 'bi', 'both' or 'best' to choose the number of 
    exponential during the decay if 'best' use 'best_criterion' to determine 
    which model to use.
    
    'best_criterion' can be 'AIC' or 'BIC'
    'AIC', Akaike's information criterion asnp.sumes here that model errors are 
    normally and independently distributed and that the variance of the model 
    errors is unknown but equal for both of them
    'BIC', Bayesian information criterion or Schwarz Criterion asnp.sumes that the
    data distribution is in the exponential family and that the model errors or 
    disturbances are normally distributed.
    '''
    
    def __init__(self, name, parent):
        
        self.in_sweep = node.Input('Sweep')
        self.in_numSweeps = node.Input('int')
        self.in_chanNames = node.Input('list')
        self.in_origin = node.Input('list')
        self.in_tag_sweep = node.Input('list')
        
        self.out_numSweeps = node.Output('int')
        self.out_sweep = node.Output('Sweep')
        self.out_chanNames = node.Output('list')
        self.out_origin = node.Output('list')
        self.out_tag = node.Output('list')

        
        
        super(Exp_Fit, self).__init__(name, parent)
        
        self._inputGroups['sweep'] = {'sweep': 'in_sweep', 'numSweeps': 
        'in_numSweeps', 'chanNames': 'in_chanNames', 'origin': 'in_origin',
        'tag': 'in_tag_sweep'}
        self._outputGroups['sweep'] = {'sweep': 'out_sweep', 
        'numSweeps': 'out_numSweeps', 'chanNames': 'out_chanNames',
        'origin': 'out_origin', 'tag': 'out_tag'}
        
        #connecting outputs:
        self.out_numSweeps.output = self.numSweeps
        self.out_sweep.output = self.sweep
        self.out_chanNames.output = self.chanNames
        self.out_origin.output = self.origin
        self.out_tag.output = self.tag
        
        self._params = {'chan':'Ch_0', 
                        'maximum':1, 
                        'ini_param':{'A':10, 't0': 0, 'tau1':0.5e-3, 
                        'tau2':5e-3, 'B':0, 'tau3':10e-3, 'A2' : 1},
                        'baseline': 'Free',
                        'rhobeg':10, 
                        'rhoend':0.0001, 
                        'maxfun':1000, 
                        'b_t0': (-10e-3, 10e-3), 
                        'b_tau1': (0.1e-3, 50e-3), 
                        'b_tau2': 50e-3, 
                        'b_tau3': 100e-3, 
                        'b_A' : (0.0001, 1000), 
                        'b_A2' : (0.0001, 1000),
                        'iprint' : 0,
                        'baseline_window': [-5e-3,-3e-3],
                        'type': 'best', 
                        'best_criterion' : 'BIC', 
                        'graphviz':{'fillcolor':'thistle', 'style': 'filled'},
                        'part2fit': None}

     
    def numSweeps(self):
        return self.in_numSweeps()
    
    def fit_sweep(self, index_sweep, verbose = 0):
        
        factor=1
        if not self.get_param('maximum'): factor=-1
        trace = self.in_sweep(index_sweep, self.get_param('chan'))
        data = trace._data[1]*factor
        time = trace._data[0]
        if self.get_param('part2fit') is not None:
            w = self.get_param('part2fit')
            part2fit = np.logical_and((time>= w[0]),(time <=w[1]))
            data = data[part2fit]
            time = time[part2fit]
        temp=[]
        
        fitType = self.get_param('type')
        p = self.get_param('ini_param')
        if self.get_param('baseline') == 'Free':
            
            a = {}
            for i in ['b_A', 'b_A2', 'b_t0', 'b_tau1', 'b_tau2', 'b_tau3']:
                a[i] = self.get_param(i)
            if fitType in ['mono', 'both', 'best']:
                param0 = (p['A'], p['t0'], p['tau1'], max(0,
                              p['tau2']-p['tau1']), p['B'])
                _error=self.createErrorfunc(self._event1)
                (param1, _errorvalue, success) = fmin_l_bfgs_b(_error, param0, 
                    args=(time, data), bounds=[(a['b_A']), (a['b_t0']), 
                    (a['b_tau1']), (0,a['b_tau2']), (None,None)], approx_grad=1)
                
                p_out={'A':factor*param1[0], 
                       't0': param1[1],
                       'tau1': param1[2],
                       'tau2': param1[3]+param1[2],
                       'B': param1[4], 
                       'success': success,
                       'fit' :np.vstack((time, factor*(self._event1(param1,
                                    time))))}
                temp+=[p_out]
            if fitType in ['bi', 'both', 'best']:
                param0 = (p['A'], p['A2'], p['t0'], p['tau1'], max(0,
                              p['tau2']-p['tau1']), max(0,p['tau3'] - p['tau2']
                              + p['tau1']), p['B'])
                _error=self.createErrorfunc(self._event1bi)
                (param1, _errorvalue, success) = fmin_l_bfgs_b(_error, param0, 
                    args=(time, data), bounds=[(a['b_A']), (a['b_A2']),
                    (a['b_t0']), (a['b_tau1']), (0,a['b_tau2']), (0,a['b_tau3']),
                    (None,None)], approx_grad=1)
                p_out={'A':factor*param1[0], 
                       'A2': param1[1]*factor,
                       't0': param1[2],
                       'tau1': param1[3],
                       'tau2': param1[4]+param1[3],
                       'tau3': param1[4]+param1[3]+param1[5],
                       'B': param1[6], 
                       'success': success,
                       'fit': np.vstack((time, factor*(self._event1bi(param1,
                                    time))))}
                temp+=[p_out]
            if fitType == 'best':
                temp= self._choosethebest(data, temp, criterion =
                            self.get_param('best_criterion'), params=param0)
            return (temp, trace)
        
        #if baseline is not a free parameter:
        else:
            blne = self.get_param('baseline')
            if blne is None: 
                baseline = float(np.mean(data))            
            elif blne == 'window':
                baseline_window = self.get_param('baseline_window')
                if baseline_window[0]>baseline_window[1]:
                    print "Error: baseline_window[0]>baseline_window[1]"
                    raise ValueError
                elif ((baseline_window[0]>max(time)) or
                     (baseline_window[1]<np.min(time))):
                    print 'baseline_window not in trace time range'
                    raise ValueError
                part2mean=np.logical_and((time>=baseline_window[0]/1000.),
                                      (time<=baseline_window[1]/1000.)) 
                baseline=float(np.mean(data[part2mean]))   
            else: baseline = float(blne)
            
            #substracting baseline:
            data -= baseline
            
            a = {}
            for i in ['b_A', 'b_t0', 'b_A2', 'b_tau1', 'b_tau2', 'b_tau3']:
                a[i] = self.get_param(i)
            if fitType in ['mono', 'both', 'best']:
                param0 =(p['A'], p['t0'], p['tau1'], max([0,p['tau2']-
                     p['tau1']]))
                _error=self.createErrorfunc(self._event0)
                (param1, _errorvalue, success) = fmin_l_bfgs_b(_error, param0, 
                    args=(time, data), bounds=[(a['b_A']), (a['b_t0']), 
                    (a['b_tau1']), (0,a['b_tau2'])], approx_grad=1)
                
                p_out={'A':factor*param1[0], 
                       't0': param1[1],
                       'tau1': param1[2],
                       'tau2': param1[3]+param1[2],
                       'success': success,
                       'fit' :np.vstack((time, factor*(self._event0(param1,
                                    time))))}
                temp+=[p_out]
            if fitType in ['bi', 'both', 'best']:
                param0 =(p['A'], p['A2'], p['t0'], p['tau1'], max([0,p['tau2']-
                     p['tau1']]), max([0,p['tau3'] - p['tau2']+p['tau1']]))
                _error=self.createErrorfunc(self._event0bi)
                (param1, _errorvalue, success) = fmin_l_bfgs_b(_error, param0, 
                    args=(time, data), bounds=[(a['b_A']), (a['b_A2']),
                    (a['b_t0']), (a['b_tau1']), (0,a['b_tau2']), (0,a['b_tau3']),
                    ], approx_grad=1)
                p_out={'A':factor*param1[0], 
                       'A2': param1[1]*factor,
                       't0': param1[2],
                       'tau1': param1[3],
                       'tau2': param1[4]+param1[3],
                       'tau3': param1[4]+param1[3]+param1[5],
                       'success': success,
                       'fit': np.vstack((time, factor*(self._event0bi(param1,
                                    time))))}
                temp+=[p_out]
            if fitType == 'best':
                temp= self._choosethebest(data, temp, criterion =
                            self.get_param('best_criterion'), params=param0)
                return (temp, trace)
            return (temp, trace)
    
    def sweep(self, index, chan = None):
        temp, trace = self.fit_sweep(index)
        trace._data = temp[0]['fit']
        return trace
    
    def init_sweep(self, time, fitType = None):
        p = self.get_param('ini_param')
        if fitType is None:
            fitType = self.get_param('type')
        out = {}
        
        if fitType in ['mono', 'both', 'best']:
            param0 =(p['A'], p['t0'], p['tau1'], max([0,p['tau2']-
                     p['tau1']]))
            out['mono'] = self._event0(param0, time)
        if fitType in ['bi', 'both', 'best']:
            param0 =(p['A'], p['A2'], p['t0'], p['tau1'], max([0,p['tau2']-
                     p['tau1']]),  max([0,p['tau3'] - p['tau2']+p['tau1']]))
            out['bi'] = self._event0bi(param0, time)
        return out
    
    def tag(self, index):
        return self.in_tag_sweep(index)
        
    def chanNames(self, index = 0):
        if self.get_param('fitType') == 'both':
            return [self.get_param('chan') + '_' + i for i in ['mono', 'bi']]
        return [self.get_param('fitType') + '_fitOf_' + self.get_param['chan']]
    
    def origin(self, index):
        return [str(self.name), str(index)]
            
    def _event0(self, params, t):
        A,t0, tau1, pseudotau2 = params
        out=np.zeros(t.size)
        out[t>= t0] =  - (A*( np.exp(-(t[t>=t0]-t0)/tau1) - np.exp(-(t[t>=t0]-t0)/(pseudotau2+tau1))))
        return out

    def _event0bi(self, params, t):
        A, A1, t0, tau1, pseudotau2, pseudotau3 = params
        out=np.zeros(t.size)
        out[t>= t0] =  - ((A+A1)*np.exp(-(t[t>=t0]-t0)/tau1) - A*np.exp(-(t[t>=t0]-t0)/(pseudotau2+tau1))- A1*np.exp(-(t[t>=t0]-t0)/(pseudotau3 + pseudotau2 + tau1)))
        return out

    def _event1(self, params, t):
        A,t0, tau1, pseudotau2, B = params
        out=np.zeros(t.size)+B
        out[t>= t0] = B - (A*( np.exp(-(t[t>=t0]-t0)/tau1) - np.exp(-(t[t>=t0]-t0)/(pseudotau2 + tau1))))
        return out

    def _event1bi(self, params, t):
        A, A1, t0, tau1, pseudotau2, pseudotau3, B = params
        out=np.zeros(t.size)+B
        out[t>= t0] = B - ((A+A1)* np.exp(-(t[t>=t0]-t0)/tau1) - A*np.exp(-(t[t>=t0]-t0)/(pseudotau2 + tau1))  - A1*np.exp(-(t[t>=t0]-t0)/(pseudotau3 + pseudotau2 + tau1)))
        return out

    def createErrorfunc(self, func):
        def _error(params, t, y):
            return np.sum((y-func(params, t))**2)
        return _error

    def _AIC(self, data, listofmodel, n_param, verbose=1):
        data=np.array(data)
        listofmodel=[np.array(model) for model in listofmodel]
        n_param=int(n_param)
        
        n=float(len(data)) #float to be sure to divide properly
        AIC=[]
        for (index, model) in enumerate(listofmodel):
            RSS=((data-model)**2).np.sum()
            AICtemp=2*n_param+n*np.log(RSS/n)
            if verbose>3: print 'Model %s: AIC is %s'%(index, AICtemp)
            AIC+=[AICtemp]
            
        index=np.argmin(AIC)
        if verbose>3: print 'Model %s is the best (with AIC = %s)'%(index, AIC[index])
        return index

    def _BIC(self, data, listofmodel, n_param, verbose=1):
        data=np.array(data)
        listofmodel=[np.array(model) for model in listofmodel]
        n_param=int(n_param)
        
        n=float(len(data)) #float to be sure to divide properly
        BIC=[]
        for (index, model) in enumerate(listofmodel):
            var=((data-model).std())**2
            BICtemp=np.log(var)+n_param/n*np.log(n)
            if verbose>3: print 'Model %s: BIC is %s'%(index, BICtemp)
            BIC+=[BICtemp]
        index=np.argmin(BIC)
        if verbose>3: print 'Model %s is the best (with BIC = %s)'%(index, BIC[index])
        return index    


    def _choosethebest(self, data, temp, criterion, params, verbose=0):
        listofmodel=[temp[0]['fit'][1],temp[1]['fit'][1]]
        n_param=len(params)
        
        if criterion == 'AIC':
            index=self._AIC(data, listofmodel, n_param, verbose)
        elif criterion == 'BIC':
            index=self._BIC(data, listofmodel, n_param, verbose)
        modname=['mono','bi']
        if verbose>2: print 'Will fit with a %sexponential.'%(modname[index])
        
        out=temp[index]
        return out
