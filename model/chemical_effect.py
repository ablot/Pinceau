# from IPython.kernel import client
from IPython.parallel import client
from scipy.optimize import fmin_l_bfgs_b
from twisted.internet.error import ConnectionRefusedError
import numpy as np
from Pinceau.CONFIG import *
# from Pinceau.model.plot_model import *
from Pinceau.model.plot_various_freq_CC import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from copy import deepcopy

_j = os.path.join

# ######################################
# ## generate traces
# datas = [np.load('WCbasketPCpair/%s'%i) for i in ['average_cell_100114A.npy',
#                                                  'average_cell_110208A_PPF.npy',
#                                                  'average_cell_110209D_PPF.npy',
#                                                  'average_cell_110223B_PPF.npy']]

# Wins = [i[0].searchsorted((-10e-3,15e-3)) for i in datas]
# ds = [i[:,w[0]:w[1]] for i, w in zip(datas, Wins)]
# t_d = max([np.diff(i) for i in Wins])
# t_d = np.linspace(-10e-3, 15e-3, t_d)
# scaled = np.array([np.interp(t_d, i[0], i[-1]) for i in ds])
# av = scaled.mean(0)
# av -= av[:t_d.searchsorted(0)].mean()
# t_d *= 1000

# def _event0(params, t):
#         A,t0, tau1, pseudotau2 = params
#         out=np.zeros(t.size)
#         out[t>= t0] =  - (A*( np.exp(-(t[t>=t0]-t0)/tau1) - np.exp(-(t[t>=t0]-t0)/(pseudotau2+tau1))))
#         return out

# def createErrorfunc(func):
#     def _error(params, t, y):
#         return np.sum((y-func(params, t))**2)
#     return _error

# _error = createErrorfunc(_event0)
# p = dict(A = 20, t0 = 1, tau1 =1, tau2 = 5)
# param0 = (p['A'], p['t0'], p['tau1'], max(0,p['tau2']-p['tau1']))

# ## bounds = [(a['b_A']), (a['b_A2']), (a['b_t0']), (a['b_tau1']), (0,a['b_tau2']), (0,a['b_tau3'])]
# (param1, _errorvalue, success) = fmin_l_bfgs_b(_error, param0, args=(t_d, av), bounds= None, approx_grad=1)
# p_out={'A':param1[0], 
#        't0': param1[1],
#        'tau1': param1[2],
#        'tau2': param1[2]+param1[3],
#        'success': success,
#        'fit': np.vstack((t_d, (_event0(param1,t_d))))}
# ######################################


from Pinceau.neuropype.ressources import plot_common

t = np.arange(t[0], cst.t_peak + 50e-3, np.diff(t[:2]))

Vsyn = np.load(_j(DATA, 'WCbasketPCpair/event.npy'))
tvsyn = Vsyn[0] * 1e-3
vsyn = Vsyn[1] * 1e-12
vsyn -= vsyn[:tvsyn.searchsorted(0)].mean()
y0 = cst.y0
arg = getarg()
arg['pace'] = 0
arg_P = deepcopy(arg)
arg_P_SY = deepcopy(arg)
ampl = -1  # amplitude of extra BC spike in mV
arg_P_SY['vs_noise'] = vsyn
arg_P_SY['vs_noise_time'] = tvsyn + cst.t_peak
arg_SY = deepcopy(arg_P_SY)
arg_SY['spike_In'] = np.zeros_like(arg['spike_In']) + cst.V_Spike_0
arg_SY['dspike_In'] *= 0
arg_0 = deepcopy(arg)
# arg_0['spike_In'] = np.zeros_like(arg['spike_In'])+cst.V_Spike_0
# arg_0['dspike_In'] *= 0
time = (t - cst.t_peak) * 1000

args = dict(arg_P=arg_P, arg_SY=arg_SY, arg_P_SY=arg_P_SY)
colors = ['g', 'orange', 'k']
out = {}
fig = myFigure(1.5, 'double')
ax0 = fig.add_subplot(611, facecolor='none')
ax1 = fig.add_subplot(612, sharex=ax0, facecolor='none')
ax2 = fig.add_subplot(613, sharex=ax0, facecolor='none')
ax3 = fig.add_subplot(614, sharex=ax0, facecolor='none')
ax4 = fig.add_subplot(615, sharex=ax0, facecolor='none')
ax5 = fig.add_subplot(616, sharex=ax0, facecolor='none')
for i, (l, arg) in enumerate(args.items()):
    out[l] = integrate_and_fire(y0, t, arg)
    kwargs = dict(label=' and '.join(l.split('_')[1:]), color=colors[i])
    # ax1.plot(time, out[l]['v_sy']*1e3, **kwargs)
    ax0.plot(time, out[l]['vd'] * 1e6 + 70e3, **kwargs)
    ax1.plot(time, out[l]['vs'] * 1e6 + 70e3, **kwargs)
    ax2.plot(time, (out[l]['vs'] - out[l]['vs_ext']) * 1e6 + 70e3, **kwargs)
    ax3.plot(time, out[l]['v_pa'] * 1e6 + 70e3, **kwargs)
    ax4.plot(time, out[l]['v_p'] * 1e6, **kwargs)
    ax5.plot(time, (out[l]['v_pa'] - out[l]['v_p']) * 1e6 + 70e3, **kwargs)

ax0.set_ylabel('V D')
ax1.set_ylabel('V S')
ax2.set_ylabel('V S - V Sext')
ax3.set_ylabel('V PA')
ax4.set_ylabel('V P')
ax5.set_ylabel('V PA - V P')
ax0.set_xlim(-5, 15)
axes = [ax0, ax1, ax2, ax3, ax4, ax5]
for x in axes:
    x.xaxis.set_ticks_position('bottom')
    x.spines['top'].set_visible(False)
    x.spines['right'].set_visible(False)
    x.spines['left'].set_visible(False)
    x.spines['bottom'].set_visible(False)
    # x.yaxis.set_visible(False)
    x.xaxis.set_visible(False)
    plot_common.makeScale(x, -1, x.get_ylim()[0], xext=None, yunit='microV')
ax5.spines['bottom'].set_visible(True)
ax5.xaxis.set_visible(True)
# ax5.set_ylabel('V S - V Sext (mV)')
ax3.legend(loc=1)
fig.savefig(_j(SAVE_PATH, 'figChemicalInh.pdf'))

# arg_P_SY['vs_noise'] = vsyn
# arg_P_SY['vs_noise_time'] = tvsyn+cst.t_peak

if True:
    print 'Plotting model crossCorr'
    out_tot = {}
    V_TEIF = 15e-3 - 70e-3
    # for d in arange(-60,-20,5)*1e-3:
    arg_changes = dict(vs_noise_time=tvsyn)  # 'gLEIF' : 0, 'V_TEIF' : d}
    begwin, endwin = -7e-3, 30e-3
    arg = deepcopy(arg_SY)
    arg['vs_noise_time'] = tvsyn
    # arg['dvsext_time'] = arg['vsext_time'][:-1]+np.diff(arg['vsext_time'])
    arg['pace'] = cst.pace
    for k, v in arg_changes.iteritems():
        arg[k] = v
    y0 = cst.y0
    t = np.linspace(0e-3, 100e-3, 100 * 500)
    singleOut = integrate_and_fire(y0, t, arg, stopAtFirstSpike=True)
    tsp = singleOut['sp_times'][0]
    ind_sp = singleOut['time'].searchsorted(tsp + begwin)
    y0 = [singleOut[i][ind_sp] for i in ['vd', 'vs', 'v_pa', 'v_p', 'n']]
    t = np.linspace(tsp + begwin, tsp + endwin, (endwin - begwin) * 1e3 * 500)  # pts per ms
    singleOut = integrate_and_fire(y0, t, arg, stopAtFirstSpike=True)
    tsp = singleOut['sp_times'][0]
    ts = np.linspace(tsp + begwin, tsp + endwin, (endwin - begwin) * 1e3 * 250)  # sp per ms
    ts = np.hstack((np.array([1]), ts))
    # maped_test_various = lambda ts: test_various_spike_IN(arg, t, y0, [ts], stopAtFirstSpike = True, killPinceau = True)
    # out_cc = do_mec_test_various(ts, arg_changes,y0, t, maped_test_various)
    out_cc = test_various_spike_IN(arg, t, y0, ts, stopAtFirstSpike=True, killPinceau=True)
    ctrlCase = np.array(1, dtype='float') * 1000
    T = out_cc[ctrlCase]['sp_times'][0]
    rate = 1 / T
    n = len(out_cc) - 1  # remove ctrl case, so -1
    data, g = cc_from_out(out_cc.copy(), sd=.5 / 3., ctrlCase=ctrlCase, firstSpikeOnly=True, dstep=1 / 1500.)
    in_time = np.array(sorted(out_cc.keys()))
    pc_time = np.array([1000 * out_cc[i]['sp_times'][0] for i in in_time])
    data = pc_time - in_time
    b, e = begwin * 1000, endwin * 1000
    step = 1 / 5.
    hist, bins = np.histogram(data, bins=np.arange(begwin * 1000, endwin * 1000 + step, step=step))
    w = (endwin - begwin)
    # out_tot[d] = out_cc

    # plot cc
    fig = myFigure(0.75)
    ax = fig.add_subplot(111, facecolor='none')
    # ax.set_title('%.2f'%(d*1000))
    b, e = bins.searchsorted((begwin * 1000, endwin * 1000))
    ax.bar(bins[b:e], 1000 * hist[b:e] / step * w / T / n, step, facecolor='none', edgecolor='k')
    ax.plot(g[0], 1000 * g[1] / n * w / T, c='k')
    part = np.logical_and(data > -2, data < 4)
    # ax.plot(data[part],np.ones_like(data[part])*15, 'k|', alpha = .5, markersize = 100)
    # ax.set_xlim(begwin,endwin)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    # ax.set_xticks([-2,-1,0,1,2])
    # ax.set_ylim(0,80)
    # xlabel('time to In peak')
    # ylabel ('freq (Hz)')
    # title('Raw CC')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.savefig(_j(SAVE_PATH, 'model_cc_chemicalonly.pdf'))
