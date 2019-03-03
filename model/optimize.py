#from IPython.kernel import client
from IPython.parallel import client
from twisted.internet.error import ConnectionRefusedError
import os, sys
import numpy as np
from plot_model import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.optimize import leastsq, minimize
from copy import deepcopy

jn = os.path.join
HOME = os.path.expanduser('~')
CT_time = np.load(jn(HOME,'share/Slow/Projet/Pinceau/model/time_extraCtrl.npy'))
CT_data = np.load(jn(HOME,'share/Slow/Projet/Pinceau/model/data_extraCtrl.npy'))
DT_time = np.load(jn(HOME,'share/Slow/Projet/Pinceau/model/time_extraDtx.npy'))
DT_data = np.load(jn(HOME,'share/Slow/Projet/Pinceau/model/data_extraDtx.npy'))
# param0 = cst.R_E, cst.gK, cst.C_BA
# F = [1e-5, 1e9, 1e13]
param0 = cst.gK, cst.C_BA
F = [1e8, 1e12]


class watch(object):
    def __init__(self, param0):
        self.p0 = param0
        
    def doOpt(self, t= None, **fkwargs):
        self.params = []
        self.v_e = []
        self.refs = []
        self.ress = []
        def w_cost(*args, **kwargs):
            self.params.append(deepcopy(args[0]))
            o, ref, trace,  out = cost(*args, retAll = True, **kwargs)
            self.v_e.append(trace)
            self.refs.append(ref)
            self.ress.append(o)
            return o
        p = [i*j for  i, j in zip(param0, F)]
        paramOut = minimize(w_cost, p, **fkwargs)
        return paramOut
        

def cost(p, t = None, arg = None, CT_time = CT_time, CT_data = CT_data, retAll = False):
    """Defined to have R_E, gK, C_BA"""
    param =[i/j for  i, j in zip(p, F)]
    if arg is None:
        arg = getarg()
    arg['pace'] = 0
    # arg['R_E'] = param[0]
    arg['gK'] = param[0]
    arg['C_BA'] = param[1]
    if t is None:
        t = cst.time
    y0 = cst.y0
    out = integrate_and_fire(y0, t, arg)
    part2compare = out['time'].searchsorted(np.array([-.5e-3,0.5e-3])+cst.t_peak)
    b = out['time'].searchsorted(np.array([-5e-3,-4e-3])+cst.t_peak)
    trace = out['v_e']
    ref = np.array([Vi_func(_, CT_time, CT_data) for _ in out['time']-cst.t_peak+0.23e-3])*1e-6+trace[b[0]:b[1]].mean()
    res =  np.sum(np.sqrt(((trace-ref)[part2compare[0]:part2compare[1]])**2))
    if retAll:
        return res, ref, trace, out
    return res

def opt(param0, **kwargs):
    p = [i*j for  i, j in zip(param0, F)]
    paramOut = leastsq(cost, p, **kwargs)
    return paramOut

def test_param(p2varie, values, main_param = None, t= None, y0 = None):
    if y0 is None:
        y0 = cst.y0
    if t is None:
        t = np.linspace(0e-3, 100e-3, 100*500)
    if main_param is None:
        main_param = getarg()
        main_param['pace'] = 0
    out = []
    for val in values:
        arg = deepcopy(main_param.copy())
        arg[p2varie] = val
        arg['R_P'] = arg['R_E'] -arg['R_E']
        print val
        out.append(integrate_and_fire(y0, t, arg))
    return out


# p2varie = 'R_E'
# fact = np.logspace(-1,1,10)
# values = [cst.R_E * i for i in fact]
# out_list = test_param(p2varie, values)


# cmap = cm.get_cmap('jet', len(out_list))
# fig = plt.figure()
# ax = fig.add_subplot(111)
# for i,out in enumerate(out_list):
#     ax.plot((out['time']-cst.t_peak)*1000, out['v_e']*1e6, label = 'val * %.2f'%(fact[i]), c = cmap(i))

# ref = np.array([Vi_func(_, CT_time, CT_data) for _ in out['time']-cst.t_peak+0.23e-3])*1e-6
# time = (out['time']-cst.t_peak)*1000
# ax.plot(time, ref*1e6, 'k', lw = 2)

