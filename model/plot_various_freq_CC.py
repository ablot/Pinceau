import os
# from IPython.kernel import client
from IPython.parallel import client
from twisted.internet.error import ConnectionRefusedError
import numpy as np
from Pinceau.CONFIG import *
from Pinceau.model.plot_model import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from Pinceau.neuropype.ressources import plot_common

_j = os.path.join

CTRLPLOT, KPLOT, CROSSCORRPLOT = True, False, False
CCEND = False
SAVE = True
SAVEFORMAT = 'svg'


def do_mec_test_various(ts, arg_changes, y0, t, maped_test_various, arg=None):
    if arg is None:
        arg = getarg()
        print 'getting arg'
    for k, v in arg_changes.items():
        arg[k] = v
    try:
        mec = client.MultiEngineClient()
        mec.execute('import os')
        mec.execute("os.chdir('%s')" % _j(LOCAL, 'model'))
        mec.execute("from plot_model import *")
        mec.execute("from constante import *")
        mec.execute("arg = {}")
        for k, v in arg.items():
            mec.execute("arg[%s] = %s" % (repr(k), repr(v)))

        for k, v in arg_changes.items():
            mec.execute("arg[%s] = %s" % (repr(k), repr(v)))
        mec.execute("y0 =" + repr(y0))
        mec.execute('ts = ' + repr(list(ts)))
        mec.execute('t = np.array(' + repr(list(t)) + ')')
        out = np.array(mec.map(maped_test_various, ts))
        out = dict([o.items()[0] for o in out])
    except Exception:
        print 'single process mode'
        out = test_various_spike_IN(arg, t, y0, ts)
    return out


def do_single_cor(ls0, ls1, trange):
    dts = []
    for spike in ls0:
        trangei = ls1.searchsorted(spike + trange)
        # find where the trange around this spike would fit in other.spikes
        if hasattr(trangei, 'count'):
            if not trangei.count():
                dts.append(np.array([]))
                continue
        dt = ls1[trangei[0]:trangei[1]] - spike
        dts.append(dt)
    return dts


def do_cor(listspike0, listspike1, trange):
    cor = []
    for ls0, ls1 in zip(listspike0, listspike1):
        cor.extend(np.array(do_single_cor(ls0, ls1, trange)))
    return cor


def plot_shift(in_time, pc_time):
    # time where the PC should be if there was no sp
    ctrl_time = pc_time[-1]
    # shift in pc spike (positive if pc is delayed)
    shift = pc_time - ctrl_time
    # pc spike relative to in
    cc = pc_time - in_time
    # pc spike relative to in if there was no sp
    cc_ctrl = np.array([ctrl_time - i for i in in_time])
    # plot part for actual data:
    pi = [plt.plot([n, s], [1, 0], 'ok-', ms=10, alpha=.5) for n, s in zip(cc_ctrl, cc)]
    plt.plot(cc_ctrl, shift, 'go-', lw=2, mfc='k')
    plt.fill_between(cc_ctrl, shift, where=shift > 0, color='orange', alpha=.5)
    plt.fill_between(cc_ctrl, shift, where=shift < 0, color='blue', alpha=.5)
    plt.hlines(0, -5, 5, 'grey')
    plt.xlim(-1, 1.5);
    plt.ylim(-0.1, 1.1)
    plt.ylabel('u.a. for the dots, ms for the shift curve')
    plt.xlabel('time to In peak')
    return ctrl_time, shift, cc, cc_ctrl, pi


################################
# PLOT FOR FIGURES
################################

def doCtrlPlot(arg=None):
    XBAR = 1.2
    if arg is None:
        arg = getarg()
        arg['pace'] = 0
    t = np.linspace(35e-3, 55e-3, (55 - 35) * 100)
    out = integrate_and_fire(y0, t, arg)

    time = (out['time'] - cst.t_peak) * 1000
    time2keep = (-1.5, 1.5)
    b, e = time.searchsorted(time2keep)

    fig = myFigure(1.5)
    ax = fig.add_subplot(411, facecolor='none')
    ax.plot(time[b:e], out['vi'][b:e] * 1000, label='V I', c='darkred')
    ax.plot(time[b:e], out['v_ba'][b:e] * 1000, label='V BA', c='k')
    ax.set_ylabel('Vm (mV)')
    ax.set_xlabel('time (ms)')
    ax.set_xlim(*time2keep)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # ax.set_frame_on(False)
    # ax.set_yticks([])
    # ax.set_xticks([])
    # xm, xM = 0.75,1.25
    ym, yM = -50, -30
    plot_common.makeScale(ax, XBAR, ym, None, "match", None, 'mV')
    # ax.plot([xm]*2, [ym,yM ], 'k', lw = 5, label = '__no_legend__')
    # ax.text(xm*.95, (ym+yM)/2., '20 mV', horizontalalignment = 'right',
    #         verticalalignment = 'center')
    # ax.plot([xm, xM], [ym]*2, 'k', lw = 5, label = '__no_legend__')
    # ax.text((xm+xM)*0.5,ym*1.05,  '0.5 ms', horizontalalignment = 'center',
    #         verticalalignment = 'top')
    # if SAVE:     # savefig('ctrl_example_ViVp.%s'%SAVEFORMAT)
    ax.xaxis.set_visible(False)
    ax.set_frame_on(False)

    ax = fig.add_subplot(412, sharex=ax, facecolor='none')
    ax.plot(time[b:e], out['v_e'][b:e] * 1e6, label='V E', c='green')
    ax.plot(time[b:e], out['v_p'][b:e] * 1e6, label='V P', c='purple')
    ax.plot(time[b:e], (out['v_pa'] - out['v_p'] + 70e-3)[b:e] * 1e6, c='k', label='V Trans PA')
    ax.plot(time[b:e], out['v_pa'][b:e] * 1e6 + 70e3, label='V PA', c=BLUE)
    # ax.plot(time[b:e], out['vs'][b:e]*1e6+70e3, label = 'VS')
    # ax.plot(time[b:e], out['vd'][b:e]*1e6+70e3, label = 'VD')
    # ax1 = ax.twinx()
    # ax1.plot(time[b:e], out['vi'][b:e]*1000, c='k', label = 'Basket')
    # ax1.legend(loc = 1)
    # ax.legend(loc = 2)
    # ax.set_ylabel('potential (microV)')
    # ax1.set_ylabel('Vm (mV)')
    # ax.set_xlabel('time (ms)')
    ax.set_xlim(*time2keep)
    # ax.xaxis.set_ticks_position('bottom')
    # ax.yaxis.set_ticks_position('left')
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # ax.set_frame_on(False)
    # ax.set_yticks([])
    # ax.set_xticks([])
    # xm, xM = 0.75,1.25
    # ym, yM = -50,-40
    # ax1.plot([xm]*2, [ym,yM ], 'k', lw = 5, label = '__no_legend__')
    # ax1.text(xm*.95, (ym+yM)/2., '10 mV', horizontalalignment = 'right',
    #         verticalalignment = 'center')
    # ax1.plot([xm, xM], [ym]*2, 'k', lw = 5, label = '__no_legend__')
    # ax1.text((xm+xM)*0.5,ym*1.05,  '0.5 ms', horizontalalignment = 'center',
    #         verticalalignment = 'top')
    # xm, xM = 0.75,1.25
    ym, yM = 10, 60
    plot_common.makeScale(ax, XBAR, ym, None, "match", None, 'microV')
    ax.set_frame_on(False)
    ax.yaxis.set_visible(False)
    ax.xaxis.set_visible(False)
    # ax.plot([xm]*2, [ym,yM ], 'k', lw = 5, label = '__no_legend__')
    # ax.text(xm*.95, (ym+yM)/2., '50 microV', horizontalalignment = 'right',
    #         verticalalignment = 'center')
    # ax.plot([xm, xM], [ym]*2, 'k', lw = 5, label = '__no_legend__')
    # ax.text((xm+xM)*0.5,ym*.95,  '0.5 ms', horizontalalignment = 'center',
    #         verticalalignment = 'top')
    # ax.set_ylim(-150,150)
    # if SAVE:     # savefig('ctrl_example_VeVrVp.%s'%SAVEFORMAT)

    ax = fig.add_subplot(414, sharex=ax, facecolor='none')
    bd = big_dict(out, arg)
    ax.plot(time[b:e], bd['I_C_PA'][b:e] * 1e12, label='I Ca', c='k')
    # ax.legend()
    ax.set_ylabel('current (fA)')
    ax.set_xlabel('time (ms)')
    ax.set_xlim(*time2keep)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ym, yM = 0, 60
    plot_common.makeScale(ax, XBAR, ym, None, "match", None, 'pA')
    [ax.spines[i].set_visible(False) for i in ['left', 'right', 'top']]
    ax.yaxis.set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    # ax.set_ylim(-200,200)
    # ax.plot([xm]*2, [ym,yM ], 'k', lw = 5, label = '__no_legend__')
    # ax.text(xm*.95, (ym+yM)/2., '0.2 pA', horizontalalignment = 'right',
    #         verticalalignment = 'center')
    # ax.plot([xm, xM], [ym]*2, 'k', lw = 5, label = '__no_legend__')
    # ax.text((xm+xM)*0.5,ym*1.05,  '0.5 ms', horizontalalignment = 'center',
    #         verticalalignment = 'top')
    # if SAVE:     # savefig('ctrl_example_Vpurk.%s'%SAVEFORMAT)

    ax = fig.add_subplot(413, sharex=ax)
    ax.plot(time[b:e], out['v_pa'][b:e] * 1e6 + 70e3, c=BLUE, label='V PA')
    ax.plot(time[b:e], out['vs'][b:e] * 1e6 + 70e3, c='k', label='V S')
    ax.plot(time[b:e], out['vd'][b:e] * 1e6 + 70e3, label='VD', c='orange')
    # ax.legend()
    ax.set_ylabel('change of potential (microV)')
    ax.set_xlabel('time (ms)')
    ax.set_xlim(*time2keep)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # ax.set_frame_on(False)
    # ax.set_yticks([])
    # ax.set_xticks([])
    xm, xM = 0.75, 1.25
    ym, yM = -2, -0
    # ax.set_ylim(-3.5,3.5)
    # ax.plot([xm]*2, [ym,yM ], 'k', lw = 5, label = '__no_legend__')
    # ax.text(xm*.95, (ym+yM)/2., '2 microV', horizontalalignment = 'right',
    #         verticalalignment = 'center')
    # ax.plot([xm, xM], [ym]*2, 'k', lw = 5, label = '__no_legend__')
    # ax.text((xm+xM)*0.5,ym*1.05,  '0.5 ms', horizontalalignment = 'center',
    #         verticalalignment = 'top')
    # ax.set_ylim(-4,4)
    plot_common.makeScale(ax, XBAR, ym, None, "match", None, 'microV')
    ax.set_frame_on(False)
    ax.yaxis.set_visible(False)
    ax.xaxis.set_visible(False)
    if SAVE:
        fig.savefig(_j(SAVE_PATH, 'ctrl_example_Vpurk.%s' % SAVEFORMAT))
        print 'saved'
    return out, fig


def doCrossCorrPlot(arg=None, Plot=True):
    ####################
    # CROSSCORR
    ####################
    print 'Plotting model crossCorr'
    out_tot = {}
    V_TEIF = 15e-3 - 70e-3
    # for d in arange(-60,-20,5)*1e-3:
    arg_changes = {}  # 'gLEIF' : 0, 'V_TEIF' : d}
    begwin, endwin = -7e-3, 4e-3
    if arg is None:
        arg = getarg()
        print 'getting in doCross'
    for k, v in arg_changes.iteritems():
        arg[k] = v
    y0 = cst.y0
    t = np.linspace(0e-3, 100e-3, 100 * 500)

    singleOut = integrate_and_fire(y0, t, arg, stopAtFirstSpike=True, verbose=False)
    tsp = singleOut['sp_times'][0]
    ind_sp = singleOut['time'].searchsorted(tsp + begwin)
    y0 = [singleOut[i][ind_sp] for i in ['vd', 'vs', 'v_pa', 'v_p', 'n']]
    t = np.linspace(tsp + begwin, tsp + endwin, (endwin - begwin) * 1e3 * 500)  # pts per ms
    singleOut = integrate_and_fire(y0, t, arg, stopAtFirstSpike=True, verbose=False)
    tsp = singleOut['sp_times'][0]
    ts = np.linspace(tsp + begwin, tsp + endwin, (endwin - begwin) * 1e3 * 250)  # sp per ms
    ts = np.hstack((np.array([1]), ts))
    maped_test_various = lambda ts: test_various_spike_IN(arg, t, y0, [ts], stopAtFirstSpike=True)
    out_cc = do_mec_test_various(ts, arg_changes, y0, t, maped_test_various, arg=arg)
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
    height = 1000 * hist / step * w / T / n
    g[1] = 1000 * g[1] / n * w / T

    if Plot:
        # plot cc
        fig = myFigure(0.75)
        ax = fig.add_subplot(111, facecolor='none')
        # ax.set_title('%.2f'%(d*1000))
        b, e = bins.searchsorted((-2, 2))
        ax.bar(bins[b:e], height[b:e], step, facecolor='none', edgecolor='k')
        ax.plot(g[0], g[1], c='k')
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
        if SAVE:
            fig.savefig(_j(SAVE_PATH, 'model_cc_LASTVERSION.%s' % SAVEFORMAT))
            print 'saved'
        return dict(g=g, heigh=height, bins=bins, pc_time=pc_time,
                    in_time=in_time, data=data, arg=arg), fig

    return dict(g=g, heigh=height, bins=bins, pc_time=pc_time,
                in_time=in_time, data=data, arg=arg)


def doKPlot():
    ####################
    # no K no C_BA
    ####################
    arg = getarg()
    arg['pace'] = 0
    t = np.linspace(30e-3, 55e-3, (60 - 30) * 100)

    print 'integrating'
    out = integrate_and_fire(y0, t, arg)
    print 'ctrl done'
    arg['gK'] = 0
    out_noK = integrate_and_fire(y0, t, arg)
    print 'no K done'
    arg['gK'] = cst.gK
    arg['C_BA'] = cst.C_BA / 100.
    out_lowC_BA = integrate_and_fire(y0, t, arg)
    print 'low C_BA done'

    time = out['time'] * 1000 - cst.t_peak * 1000
    time2keep = (-1.5, 1.5)
    b, e = time.searchsorted(time2keep)
    fig = myFigure(1)
    ax = fig.add_subplot(111)
    ax.plot(time[b:e], out['v_p'][b:e] * 1e6, label='Control', c='purple')
    ax.plot(time[b:e], out_noK['v_p'][b:e] * 1e6, label='No Potassium', c='b')
    ax.plot(time[b:e], out_lowC_BA['v_p'][b:e] * 1e6, c='orange', label='Low C BA')
    ax1 = ax.twinx()
    ax1.plot(time[b:e], out['vi'][b:e] * 1000, c='k', label='Basket', ls='dashed')
    ax1.legend(loc=1)
    ax.legend(loc=2)
    ax.set_xlabel('time (ms)')
    ax.set_xlim(*time2keep)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    [ax.spines[i].set_visible(False) for i in ['left', 'right', 'top']]
    ax.yaxis.set_visible(False)
    ax1.yaxis.set_visible(False)
    ax1.set_frame_on(False)
    ax.xaxis.set_ticks_position('bottom')
    xm, xM = 0.75, 1.25
    ym, yM = -50, -20
    plot_common.makeScale(ax1, 1, ym, None, "match", None, 'mV')
    plot_common.makeScale(ax, -1, ym, None, "match", None, 'microV')
    if SAVE:
        fig.savefig(_j(SAVE_PATH, 'ctrl_example_CtNoKNoC_BA.%s' % SAVEFORMAT))
        print 'saved'
    return dict(out_ct=out, out_noK=out_noK,
                out_lowC_BA=out_lowC_BA), fig


def doCCEnd():
    ################################
    # do one cc around 50 Hz to test:
    ################################

    # surfs = np.linspace(0.05,0.1,10)*1e-9
    # freq from 10 to 150 Hz
    # surfs = [1e-11, 1.9e-11, 3.2e-11, 4e-11, 4.5e-11, 5e-11, 5.5e-11,
    #          6.1e-11, 6.7e-11, 7.2e-11, 7.8e-11, 10e-11]

    out = []
    begwin = -5e-3
    endwin = 5e-3
    w = endwin - begwin
    paces = 15e-3 * np.linspace(10, 100, 10)

    for index, p in enumerate(paces):
        print '%s/%s !!\n--------------' % (index, len(paces))
        arg = getarg()
        arg_changes = {'pace': p}
        for k, v in arg_changes.items():
            arg[k] = v
        t = np.linspace(0e-3, 500e-3, 500 * 2)
        singleOut = integrate_and_fire(y0, t, arg, stopAtFirstSpike=True)
        tsp = singleOut['sp_times'][0]
        ind_sp = singleOut['time'].searchsorted(tsp + begwin)
        y0 = [singleOut[i][ind_sp] for i in ['vd', 'vs', 'v_pa', 'v_p', 'n']]
        t = np.linspace(tsp + begwin, tsp + endwin, (endwin - begwin) * 1e3 * 500)  # 5 pts per ms
        singleOut = integrate_and_fire(y0, t, arg, stopAtFirstSpike=True)
        tsp = singleOut['sp_times'][0]
        ts = np.linspace(tsp + begwin, tsp + endwin, (endwin - begwin) * 1e3 * 100)  # sp per ms
        ts = np.hstack((np.array([1]), ts))
        maped_test_various = lambda ts: test_various_spike_IN(arg, t, y0, [ts], stopAtFirstSpike=True)
        temp = do_mec_test_various(ts, arg_changes, y0, t, maped_test_various, arg=arg)
        out.append(temp)

    ctrlCase = np.array(1, dtype='float') * 1000
    T = np.array([o[ctrlCase]['sp_times'][0] for o in out])
    n = [len(o) for o in out]
    datas = []
    gausses = []
    for o in out:
        data, g = cc_from_out(o.copy(), sd=.2 / 3., ctrlCase=ctrlCase, firstSpikeOnly=True, dstep=1 / 1500.)
        datas.append(data)
        gausses.append(g)
    in_times = [np.array(sorted(o.keys())) for o in out]
    pc_times = [np.array([1000 * o[i]['sp_times'][0] for i in in_t]) for in_t, o in zip(in_times, out)]
    rate = 1 / T

    # #plot shift
    # for r, In, PC in zip(rate, in_times, pc_times):
    #     figure()
    #     plot_shift(In, PC)
    #     title('rate = %i hz'%(r))
    # if SAVE:     #     savefig('shift_rate_%i.%s'%SAVEFORMAT%(r))

    # plot gauss
    cmap = cm.get_cmap('jet', len(out))
    figure()
    for i, (g, r, b) in enumerate(zip(gausses, T, n)):
        plot(g[0], 1000 * g[1] / b * w / r, label='%i Hz' % (1 / r), c=cmap(i))
    xlim(-4, 4)
    legend(loc=0)
    xlabel('time to In peak')
    ylabel('freq (Hz)')
    title('Raw CC')
    if SAVE:
        savefig(_j(SAVE_PATH, 'cc_various_rate_raw.%s' % SAVEFORMAT))
        print 'saved'

    figure()
    for i, (g, r, b) in enumerate(zip(gausses, T, n)):
        plot(g[0], 1000 * g[1] / b * w * 100, label='%i Hz' % (1 / r), c=cmap(i))
    xlim(-4, 4)
    legend(loc=0)
    xlabel('time to In peak')
    ylabel('rel freq (%)')
    title('Rel CC')
    if SAVE:
        savefig(_j(SAVE_PATH, 'cc_various_rate_rel.%s' % SAVEFORMAT))
        print 'saved'

    figure()
    for i, (g, r, b) in enumerate(zip(gausses, T, n)):
        plot(g[0], 1000 * g[1] / b * w / r - (1 / r), label='%i Hz' % (1 / r), c=cmap(i))
    xlim(-4, 4)
    ylim(-20, 20)
    legend(loc=0)
    xlabel('time to In peak')
    ylabel('effect ampl (Hz)')
    title('Sub CC')
    if SAVE:
        savefig(_j(SAVE_PATH, 'cc_various_rate_sub.%s' % SAVEFORMAT))
        print 'saved'

    period = 1 / rate

    ys = ['Vd0', 'Vs0', 'Va0', 'Ve0', 'n0']

    # spike times
    in_time = in_times[0]
    pc_time = pc_times[0]
    ctrl_time, shift, cc, cc_ctrl, pi = plot_shift(in_time, pc_time)

    # make a func to linear interpolate
    shift_func = lambda t: Vi_func(t, cc_ctrl[::-1], shift[::-1])
    # need to reverse to make the time right (since in spike increases, pc - in decreases)
    # create interpolated data
    fake_x = np.arange(-5, 5, 1e-3)
    fake_data = np.array([shift_func(i) + i for i in fake_x])
    plot(fake_x, fake_data, 'go-', mfc='k')
    pi = [plot([n, s], [1, 0], 'ok-', ms=10, alpha=.5) for n, s in zip(fake_x, fake_data)]
    xlim(-1, 1.5);
    ylim(-0.1, 1.1)
    ylabel('u.a. for the dots, ms for the shift curve')
    xlabel('time to In peak')
    title('interpolated version')

    # test various Rl
    Rl_part = np.linspace(1e3, 500e3, 10)
    Rl = Rl_part + cst.Rinf
    larg_changes = [{'Rl': rl, 'Rl_part': rlpart} for rl, rlpart in zip(Rl, Rl_part)]
    # out = loop_sim(larg_changes)
    pts_per_ms = 50
    sp_per_ms = 20
    firstwithoutSp = True
    # def loop_sim(list_arg_changes, pts_per_ms = 50, sp_per_ms = 10, tsp = None, y0 = None, firstwithoutSp = True):
    #    """ WARNING this loop should probably bug if there is a spike PC in the first 3 ms of simulation !"""
    y0 = [getattr(cst, i) for i in 'Vd0', 'Vs0', 'V_PA0', 'V_P0', 'n0']
    t = np.linspace(0e-3, 50e-3, 50 * 2)
    singleOut = integrate_and_fire(y0, t, arg)
    tsp = singleOut['sp_times'][0]
    ind_sp = singleOut['time'].searchsorted(tsp - 3e-3)
    y0 = [singleOut[i][ind_sp] for i in ['vd', 'vs', 'v_pa', 'v_p', 'n']]
    t = np.linspace(tsp - 5e-3, tsp + 3e-3, 8 * pts_per_ms)  # pts per ms
    singleOut = integrate_and_fire(y0, t, arg)
    tsp2 = singleOut['sp_times'][0]
    ts = np.linspace(tsp2 - 5e-3, tsp2 + 3e-3, 8 * sp_per_ms)
    ts = np.hstack((np.array([100]), ts))
    ts_prim = np.array([100])
    out = []
    for arg_changes in larg_changes:
        arg = getarg()
        for k, v in arg_changes.items():
            arg[k] = v
        # if tsp is None:
        #     y0 = [getattr(cst, i) for i in 'Vd0', 'Vs0', 'Va0', 'Ve0', 'n0']
        #     t = np.linspace(0e-3, 50e-3, 50*2)
        #     singleOut = integrate_and_fire(y0, t, arg)
        #     tsp = singleOut['sp_times'][0]
        #     ind_sp = singleOut['time'].searchsorted(tsp-3e-3)
        #     y0 = [singleOut[i][ind_sp] for i in ['vd', 'vs','v_pa','v_p','n']]
        #     t = np.linspace(tsp-3e-3, tsp+5e-3, 7*pts_per_ms) # pts per ms
        #     singleOut = integrate_and_fire(y0,t, arg)
        #     tsp = singleOut['sp_times'][0]
        # elif y0 is None:
        #     raise IOError('tsp without y0 !')
        # else:
        maped_test_various = lambda ts: test_various_spike_IN(arg, t, y0, [ts])
        temp = do_mec_test_various(ts, arg_changes, y0, t, maped_test_various, arg=arg)
        out.append(temp)
    #    return out
    ctrlCase = max(out[0].keys())
    T = [o[ctrlCase]['sp_times'] for o in out]
    n = [len(o) for o in out]
    datas = []
    gausses = []
    for o in out:
        data, g = cc_from_out(o.copy(), sd=1 / 5., ctrlCase=None, firstSpikeOnly=True)
        datas.append(data)
        gausses.append(g)

    in_times = [np.array(sorted(o.keys())) for o in out]
    pc_times = [np.array([1000 * o[i]['sp_times'][0] for i in in_t]) for in_t, o in zip(in_times, out)]
    rate = 1 / T

    for r, In, PC in zip(rate, in_times, pc_times):
        figure()
        plot_shift(In, PC)
        title('rate = %i hz' % (r))
        if SAVE:
            savefig(j_(SAVE_PATH, 'shift_rate_%i.%s' % SAVEFORMAT % (r)))
            print 'saved'

    cmap = cm.get_cmap('jet', len(out))
    figure()
    for i, (g, r, b) in enumerate(zip(gausses, T, n)):
        plot(g[0], 1000 * g[1] / b * w / r - 1 / r, label='%i Hz' % (1 / r), c=cmap(i))
    xlim(-4, 4)
    legend(loc=0)
    xlabel('time to In peak')
    ylabel('freq (Hz)')
    title('Raw CC')

    period = 1 / rate
    number = [len(In) for In in in_times]
    figure()
    for i, (g, r, b) in enumerate(zip(gausses, rate, base)):
        plot(g[0], g[1] / b * 100, label='%i Hz' % (r), c=cmap(i))

    xlim(-4, 4)
    legend(loc=0)
    xlabel('time to In peak')
    ylabel('relative freq (%)')
    title('CC relative to baseline')

    figure()
    for i, (g, T, n) in enumerate(zip(gausses, period, number)):
        plot(g[0], g[1] / n * 1000 * w / T, label='%i Hz' % (1 / T), c=cmap(i))
    xlim(-4, 4)
    legend(loc=0)
    xlabel('time to In peak')
    ylabel('effect ampl (Hz)')
    title('CC minus baseline')

    part = [g[0].searchsorted([-2, 1]) for g in gausses]
    minimum = np.array([g[1, p[0]:p[1]].min() for g, p in zip(gausses, part)])
    min_hz = minimum / number * 1000 * w / period

    shifts = [PC - PC[-1] for PC in pc_times]
    x_shifts = [np.array([PC[-1] - i for i in in_time]) for PC, in_time in zip(pc_times, in_times)]

    shift_max = [s.max() for s in shifts]


if __name__ == '__main__':
    if CTRLPLOT:
        doCtrlPlot()
    if KPLOT:
        doKPlot()
    if CROSSCORRPLOT:
        doCrossCorrPlot()
    if CCEND:
        doCCEnd()
