# from IPython.kernel import client
from IPython.parallel import client
from twisted.internet.error import ConnectionRefusedError
import numpy as np
import os
from Pinceau.CONFIG import SAVE_PATH, DATA
# from Pinceau.model.plot_model import *
from Pinceau.model.plot_various_freq_CC import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from copy import deepcopy
from Pinceau.neuropype.ressources import plot_common

_j = os.path.join

# but adding it to sys.path should work if their is no other
# neuropype defined before ...

vsext = np.load(os.path.join(DATA, 'fake_Vsext.npy')) * 1e-6
vsext_dict = np.load(os.path.join(DATA, 'cell_110422A_average_In_cached.npz'))
bigArrField = np.array([vsext_dict['sw%i_Ch_3' % i] for i in range(15)])
bigArrSpike = np.array([vsext_dict['sw%i_Ch_0' % i] for i in range(15)])
ind2use = 5  # use sw_5 as v_sext
t_vsext, data = bigArrField[5]
data *= 1e-6  # put back in microV
data *= 2  # scale factor to make it bigger

arg = getarg()
arg['pace'] = 0
arg_P = deepcopy(arg)
arg_P_BA = deepcopy(arg)
ampl = -1  # amplitude of extra BC spike in mV
arg_P_BA['vsext'] = data
arg_P_BA['vsext_time'] = t_vsext + cst.t_peak
arg_P_BA['dvsext'] = np.diff(arg_P_BA['vsext']) / np.diff(arg_P_BA['vsext_time'][:2])
arg_P_BA['dvsext_time'] = arg_P_BA['vsext_time'][:-1] + np.diff(arg_P_BA['vsext_time'])
arg_BA = deepcopy(arg_P_BA)
arg_BA['spike_In'] = np.zeros_like(arg['spike_In']) + cst.V_Spike_0
arg_BA['dspike_In'] *= 0
arg_0 = deepcopy(arg)
# arg_0['spike_In'] = np.zeros_like(arg['spike_In'])+cst.V_Spike_0
# arg_0['dspike_In'] *= 0
time = (cst.time - cst.t_peak) * 1000

args = dict(arg_P=arg_P, arg_BA=arg_BA, arg_P_BA=arg_P_BA)
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
    # ax1.plot(time, out[l]['v_ba']*1e3, **kwargs)
    ax0.plot(time, out[l]['vs_ext'] * 1e6, **kwargs)
    ax1.plot(time, out[l]['vs'] * 1e6 + 70e3, **kwargs)
    ax2.plot(time, (out[l]['vs'] - out[l]['vs_ext']) * 1e6 + 70e3, **kwargs)
    ax3.plot(time, out[l]['v_pa'] * 1e6 + 70e3, **kwargs)
    ax4.plot(time, out[l]['v_p'] * 1e6, **kwargs)
    ax5.plot(time, (out[l]['v_pa'] - out[l]['v_p']) * 1e6 + 70e3, **kwargs)

ax0.set_ylabel('V Sext')
# ax1.set_ylabel('V BA (mV)')
ax1.set_ylabel('V S - V Sext')
ax2.set_ylabel('V PA')
ax3.set_ylabel('V P')
ax4.set_ylabel('V PA - V P')
ax0.set_xlim(-1.5, 1.5)
axes = [ax0, ax1, ax2, ax3, ax4, ax5]
for x in axes:
    x.xaxis.set_ticks_position('bottom')
    x.spines['top'].set_visible(False)
    x.spines['right'].set_visible(False)
    x.spines['left'].set_visible(False)
    x.spines['bottom'].set_visible(False)
    x.yaxis.set_visible(False)
    x.xaxis.set_visible(False)
    plot_common.makeScale(x, -1, x.get_ylim()[0], xext=None, yunit='microV')
ax5.spines['bottom'].set_visible(True)
ax5.xaxis.set_visible(True)
# ax5.set_ylabel('V S - V Sext (mV)')
ax3.legend(loc=1)
fig.savefig(_j(SAVE_PATH, 'figSuppBasket.pdf'))

if True:
    print 'Plotting model crossCorr'
    out_tot = {}
    V_TEIF = 15e-3 - 70e-3
    # for d in arange(-60,-20,5)*1e-3:
    arg_changes = dict(vsext_time=t_vsext,
                       dvsext_time=t_vsext[:-1] + np.diff(t_vsext))  # 'gLEIF' : 0, 'V_TEIF' : d}
    begwin, endwin = -7e-3, 4e-3
    arg = deepcopy(arg_BA)
    arg['vsext_time'] = t_vsext
    arg['dvsext_time'] = arg['vsext_time'][:-1] + np.diff(arg['vsext_time'])
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
    data, g = cc_from_out(out_cc.copy(), sd=.25 / 3., ctrlCase=ctrlCase, firstSpikeOnly=True, dstep=1 / 1500.)
    in_time = np.array(sorted(out_cc.keys()))
    pc_time = np.array([1000 * out_cc[i]['sp_times'][0] for i in in_time])
    data = pc_time - in_time
    b, e = -3, 4
    step = 1 / 5.
    hist, bins = np.histogram(data, bins=np.arange(b, e + step, step=step))
    w = endwin - begwin
    # out_tot[d] = out_cc

    # plot cc
    fig = myFigure(0.75)
    ax = fig.add_subplot(111, facecolor='none')
    # ax.set_title('%.2f'%(d*1000))
    b, e = bins.searchsorted((-2, 2))
    ax.bar(bins[b:e], 1000 * hist[b:e] / step * w / T / n, step, facecolor='none', edgecolor='k')
    ax.plot(g[0], 1000 * g[1] / n * w / T, c='k')
    part = np.logical_and(data > -2, data < 4)
    # ax.plot(data[part],np.ones_like(data[part])*15, 'k|', alpha = .5, markersize = 100)
    ax.set_xlim(-2, 2)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.set_xticks([-2, -1, 0, 1, 2])
    # ax.set_ylim(0,80)
    # xlabel('time to In peak')
    # ylabel ('freq (Hz)')
    # title('Raw CC')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.savefig(_j(SAVE_PATH, 'model_cc_basketonly.pdf'))
