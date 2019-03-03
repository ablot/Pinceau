# -*- coding: utf-8 -*-
from numpy import exp, log
import numpy as np
import os, sys

# choose between current injection and leak in PC
# from model_3 import *
from model_7 import *

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colorbar as cbar

from Pinceau.neuropype.ressources._common import *


#########################################################################
### Ploting results
#########################################################################

def complete_dict(integrate_dict=None, arg=None):
    if arg is None:
        arg = getarg()

    if integrate_dict is None:
        integrate_dict = integrate(y0, t, arg)
    out = {}
    out.update(integrate_dict)
    # out['Vi'] = np.array([Vi_func(i) for i in t])
    # out['dVi'] = np.array([dVi_func(i) for i in t])

    # out['V_BA'] = arg['R_I'] * (out['Vi']/arg['R_I'] - (out['V_PA']-out['V_S'])/arg['R_AS'] - out['V_P']/arg['R_L'])
    # out['i'] = (out['Vi'] - out['V_BA'])/arg['R_I']
    # out['i_k'] = IK(out, arg)
    # out['i_p'] = out['i'] - out['i_k']

    # out['i_l'] = out['V_P']/arg['R_L']
    # out['i_e'] = out['i'] - out['i_l']
    # #out['Va'] = R_AS*out['i_e'] + out['V_S']
    # out['i_d'] = (out['V_S'] - out['V_D'])/arg['R_J']
    # out['i_s'] = out['i_e'] - out['i_d']

    # out['dV_D'] = dV_D(out, arg)
    # out['dV_S'] = dV_S(o, arg)
    # out['dV_P'] = dV_P(out, arg)
    # out['dVa'] = dVa(out, arg)
    return out


def plot_bioV(d, fig=None):
    if fig is None:
        fig = plt.figure()
    ax0 = fig.add_subplot(211)
    ax1 = fig.add_subplot(212, sharex=ax0)
    ax0.plot(t * 1e3, (d['V_BA'] - d['V_P']) * 1e3, label='V_P')
    ax1.plot(t * 1e3, (d['Va'] - d['V_P']) * 1e3, label='V_A')
    ax1.plot(t * 1e3, d['V_S'] * 1e6 + 80e3, label='V_S')
    ax1.plot(t * 1e3, d['V_D'] * 1e6 + 80e3, label='V_D')
    ax0.set_ylabel('Vm (mV)')
    ax1.set_ylabel('Vm (mV)')
    ax1.set_xlabel('time (ms)')
    ax0.legend()
    ax1.legend()
    return fig


def plot_modelV(d, fig=None):
    if fig is None:
        fig = plt.figure()
    ax0 = fig.add_subplot(411)
    ax1 = fig.add_subplot(412, sharex=ax0)
    ax2 = fig.add_subplot(413, sharex=ax0)
    ax3 = fig.add_subplot(414, sharex=ax0)

    ax0.plot(t * 1e3, (d['V_BA']) * 1e3, label='V_p')
    ax0.plot(t * 1e3, (d['Vi']) * 1e3, label='V_i')

    ax1.plot(t * 1e3, (d['V_P']) * 1e6, label='V_e')

    ax2.plot(t * 1e3, (d['Va']) * 1e6 + 80e3, label='V_a')
    ax2.plot(t * 1e3, (d['V_S']) * 1e6 + 80e3, label='V_s')
    ax2.plot(t * 1e3, (d['V_D']) * 1e6 + 80e3, label='V_d')

    ax3.plot(t * 1e3, (d['n']), label='n')

    ax0.set_ylabel('V (mV)')
    ax2.set_ylabel('V (microV + 80 mV)')
    ax1.set_ylabel('V (microV)')
    ax2.set_xlabel('time (ms)')
    ax0.legend()
    ax2.legend()
    ax1.legend()
    ax3.legend()
    return fig


def vari_param(argName, values, arg=None):
    if arg is None:
        arg = getarg()

    tot_out = []
    # print 'integration with variable parameter:'
    for v in values:
        # print '%s = %s ...'%(argName, v)
        arg[argName] = v
        out = integrate_and_fire(cst.y0, cst.time, arg)
        tot_out.append(out)
    return tot_out


def replace_param(argNames, values, arg=None):
    if arg is None:
        arg = getarg()

    for ind, value in zip(argNames, values):
        arg[ind] = value

    return complete_dict(arg=arg)


def explore_param(dict_values):
    arg = [getattr(cst, i) for i in ['R_I', 'R_L', 'R_AS',
                                     'R_J', 'C_BA', 'C_PA',
                                     'C_S', 'C_D', 'gK',
                                     'EK', 'cK0', 'cK1']]

    argNames, Values = dict_values.keys(), dict_values.values()
    out = {}
    n = 0
    while argNames and n < 10:
        print 'param %s:' % argNames[0]
        print '%s to go ...' % (len(argNames) - 1)
        n += 1
        main_arg = argNames.pop(0)
        main_val = Values.pop(0)
        for argbis, valbis in zip(argNames, Values):
            index = arg_Names.index(argbis)
            for v in valbis:
                arg[index] = v
                temp = vari_param(main_arg, main_val, arg=arg)
                # t[59999-1000]*1000 =  14.75
                # t[59999+1000]*1000 =  15.25
                maxs = [te['V_P'][59999 - 1000:59999 + 1000].max() for te in temp]
                for m, va in zip(maxs, main_val):
                    out[main_arg + '_' + str(va) + '/' + argbis + '_' + str(v)] = m
    return out


nl = 10
mini = np.log10(.1)
mini2 = np.log10(.5)
maxi = np.log10(10)
maxi2 = np.log10(2)
dict_val = {'C_PA': [cst.C_PA * i for i in np.logspace(mini, maxi, nl)],
            'C_BA': [cst.C_BA * i for i in np.logspace(mini, maxi, nl)],
            'R_AS': [cst.R_AS * i for i in np.logspace(mini, maxi, nl)],
            'R_L': [cst.R_L * i for i in np.logspace(mini, maxi2, nl)],
            # 'R_J':[cst.R_J* i for i in np.logspace(mini, maxi,nl)],
            # 'C_S':[cst.C_S* i for i in np.logspace(mini, maxi,nl)],
            # 'C_D':[cst.C_D* i for i in np.logspace(mini, maxi,nl)],
            'R_I': [cst.R_I * i for i in np.logspace(mini, maxi, nl)],
            'gK': [cst.gK * i for i in np.logspace(mini, maxi, nl)],
            # 'cK0': np.logspace(mini,maxi, nl),
            # 'cK1': np.logspace(mini,maxi, nl),
            'EK': np.linspace(-100e-3, -70e-3, nl)}

conv_dict = {'C_PA': 1e12,
             'C_BA': 1e12,
             'C_S': 1e12,
             'C_D': 1e12,
             'EK': 1e3,
             'R_AS': 1e-6,
             'R_L': 1e-3,
             'R_I': 1e-6,
             'R_J': 1e-6,
             'gK': 1e9,
             't': 1e3,
             'cK0': 1,
             'cK1': 1}
conv_units = {'C_PA': 'pF',
              'C_BA': 'pF',
              'C_S': 'pF',
              'C_D': 'pF',
              'EK': 'mV',
              'R_AS': 'MOhm',
              'R_L': 'kOhm',
              'R_I': 'MOhm',
              'R_J': 'MOhm',
              'gK': 'ns',
              't': 'ms',
              'cK0': 'tau factor, no units',
              'cK1': 'm factor, no units'}


def explore2param(paramName1, value1, paramName2, value2, verbose=1, arg=None):
    X, Y = np.meshgrid(sorted(value1), sorted(value2))
    Z = [[{} for i in Y] for j in X]
    if verbose: print 'Explore 2 param ... %s line(s), %s column(s)' % (X.shape)
    for lineindex, (lineX, lineY) in enumerate(zip(X, Y)):
        if verbose: print 'line %s' % lineindex
        for colindex, (x, y) in enumerate(zip(lineX, lineY)):
            out = replace_param((paramName1, paramName2), (x, y), arg)
            Z[lineindex][colindex] = out
    return X, Y, Z


def explore1param(paramName, paramValues, toKeep='V_P', arg=None):
    X, Y = np.meshgrid(t, sorted(paramValues))
    Z = np.ones_like(X)
    print 'integrating ...'
    for index, value in enumerate(paramValues):
        if index % 5 == 0: print '... %s/%s ...' % (index + 1, len(paramValues))
        out = replace_param([paramName], [value], arg)
        if toKeep != 'VA':
            Z[index, :] = out[toKeep]
        else:
            Z[index, :] = out['va'] - out['ve']
    return X, Y, Z


def explore1paramKeepall(paramName, paramValues, arg=None):
    X, Y = np.meshgrid(t, np.sort(paramValues))
    Z = []
    print 'integrating ...'
    for index, value in enumerate(paramValues):
        if index % 5 == 0: print '... %s/%s ...' % (index + 1, len(paramValues))
        out = replace_param([paramName], [value], arg)
        Z.append(out)
    return X, Y, Z


def drawLines(x, Ys, zs, zlabel='unknown', xlabel='time (ms)', ylabel='V_P (mV)', cmapName='jet'):
    assert len(x) == Ys.shape[1]
    assert Ys.shape[0] == len(zs)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    mycmap = cm.get_cmap(cmapName, len(zs))
    for i, y in enumerate(Ys):
        ax.plot(x, y, c=mycmap(i))
    cbar_ax, orientation = cbar.make_axes(ax)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    cb = cbar.ColorbarBase(cbar_ax, mycmap)
    ticks = cbar_ax.get_yticks()
    zmin = min(zs)
    zrange = max(zs) - zmin
    cbar_ax.set_yticklabels(['%.2f' % (ti * zrange + zmin) for ti in ticks])
    cbar_ax.set_ylabel(zlabel)
    return fig


"""
toKeep = 've'
ylabel = 'V PC axon (microV)'
factor = 1e6
for i, (k, v) in enumerate(dict_val.iteritems()):
    X,Y,Z = explore1param(k,v, toKeep = toKeep)
    x = X[0]*1000
    zs = [z[0]*conv_dict[k] for z in Y]
    fig = drawLines(x, Z*factor, zs, zlabel = k+' ('+conv_units[k]+')', ylabel = ylabel)
    fig.axes[0].set_xlim(9,11)
    fig.savefig(toKeep+'_changing_'+k+'.eps')
    # fig.canvas.draw()
    plt.close(fig)
"""


def flatplot2param(X, Y, Z, paramName1=None, paramName2=None, ax=None, Zfactor=1,
                   turn=0, surf=1, wire=1, surfkwargs={}, wirekwargs={}, zlabel='',
                   ylabel='', xlabel='', centerCmap=0, **kwargs):
    if paramName1 is None: paramName1 = 'paramName1'
    if paramName2 is None: paramName2 = 'paramName2'

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
    else:
        fig = ax.figure
    if kwargs.has_key('ax'):
        kwargs.pop('ax')
    if kwargs.has_key('cb'):
        cb = kwargs.pop('cb')
    else:
        cb = 1
    if kwargs.has_key('label'):
        label = kwargs.pop('label')
    else:
        label = 1
    if label: ax.set_xlabel(xlabel if xlabel else paramName1)
    if label: ax.set_ylabel(ylabel if ylabel else paramName2)

    if conv_dict.has_key(paramName1):
        conv_X = conv_dict[paramName1]
    else:
        conv_X = 1
    if conv_dict.has_key(paramName2):
        conv_Y = conv_dict[paramName2]
    else:
        conv_Y = 1

    if centerCmap:
        zflat = (Z * Zfactor).flatten()
        med = np.mean(zflat)
        quant = np.array([np.percentile(zflat, 0.95), np.percentile(zflat, 0.05)])
        vmax = np.max(np.abs(quant - med))
        vmin = med - vmax
        kwargs['vmin'] = vmin
        kwargs['vmax'] = vmax
    # raise ValueError
    wire = ax.hexbin((conv_X * X).flatten(), (conv_Y * Y).flatten(), (Z * Zfactor).flatten(),
                     **kwargs)
    ax.set_xlim(np.min(conv_X * X), np.max(conv_X * X))
    ax.set_ylim(np.min(conv_Y * Y), np.max(conv_Y * Y))
    if cb:
        cb = fig.colorbar(wire, ax=ax)
        cb.set_label(zlabel)

    return fig


def plot2param(X, Y, Z, paramName1=None, paramName2=None, Zfactor=1, turn=0,
               surf=1, wire=1, surfkwargs={}, wirekwargs={}, zlabel='',
               ylabel='', xlabel=''):
    if paramName1 is None: paramName1 = 'paramName1'
    fig = plt.figure()
    num = 1
    if surf and wire: num = 2
    ax = fig.add_subplot(1, num, 1, projection='3d')
    ax.set_xlabel(xlabel if xlabel else paramName1)
    ax.set_ylabel(ylabel if ylabel else paramName2)
    ax.set_zlabel(zlabel if zlabel else 'Z')
    if conv_dict.has_key(paramName2):
        conv_Y = conv_dict[paramName2]
    else:
        conv_Y = 1
    if conv_dict.has_key(paramName1):
        conv_X = conv_dict[paramName1]
    else:
        conv_X = 1
    # ax.plot_wireframe(conv_X*X, 1000*Y, Z*1e6,**kwargs)
    if surf:
        if not surfkwargs.has_key('cmap'):
            surfkwargs['cmap'] = cm.jet
        surf = ax.plot_surface(conv_X * X, conv_Y * Y, Z * Zfactor, **surfkwargs)
        wire = ax.plot_wireframe(conv_X * X, conv_Y * Y, Z * Zfactor, **wirekwargs)
        fig.colorbar(surf)
    if wire:
        if num == 2:
            ax = fig.add_subplot(1, 2, 2, projection='3d')
            ax.set_xlabel(xlabel if xlabel else paramName1)
            ax.set_ylabel(ylabel if ylabel else paramName2)
            ax.set_zlabel(zlabel if zlabel else 'unknown')
        wire = ax.plot_wireframe(conv_X * X, conv_Y * Y, Z * Zfactor, **wirekwargs)
    if turn:
        for angle in range(0, 360):
            ax.view_init(30, angle)
            plt.draw()
    return fig


# def plot2param(X, Y, Z, paramName1 = None, paramName2 = None, ax = None, c= None,
#                zlabel = 'V_P max (microV)'):
#     if paramName1 is None: paramName1 = 'paramName1'
#     if paramName2 is None: paramName2 = 'paramName2'
#     if ax is None:
#         fig = plt.figure()
#         ax = fig.gca(projection='3d')
#     ax.set_xlabel(paramName1)
#     ax.set_ylabel(paramName2)
#     ax.set_zlabel(zlabel)
#     if conv_dict.has_key(paramName1):
#         conv_X = conv_dict[paramName1]
#     else: conv_X = 1
#     if conv_dict.has_key(paramName2):
#         conv_Y = conv_dict[paramName2]
#     else: conv_Y = 1
#     ax.plot_wireframe(conv_X*X, conv_Y*Y, Z*1e6)
#     return fig


def plot_explored(dict_expl, val, N, conv_dict={}):
    Ktokeep = []
    for i in dict_expl.iterkeys():
        if val in i:
            Ktokeep.append(i)
    reformat = [[j.split('_') for j in k.split('/')] for k in Ktokeep]
    other = [i if i != val else k for (i, j), (k, l) in reformat]
    group = {}
    for K, r, o in zip(Ktokeep, reformat, other):
        if not group.has_key(o):
            group[o] = [(r, K)]
        else:
            group[o].append((r, K))

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_xlabel(val)
    ax.set_ylabel('other parameter (see legend)')
    ax.set_zlabel('V_P max (microV)')

    colors = cm.get_cmap('jet', N)
    for index_group, g in enumerate(group.itervalues()):
        X, Y, Z = [], [], []
        for [(i, j), (k, l)], key in g:
            j = float(j)
            l = float(l)
            if conv_dict.has_key(i):
                j *= conv_dict[i]
            if conv_dict.has_key(k):
                l *= conv_dict[k]

            if i == val:
                X.append(j)
                Y.append(l)
            else:
                X.append(l)
                Y.append(j)

            Z.append(dict_expl[key])
        X, Y, Z = [np.array(w) for w in (X, Y, Z)]
        order = X.argsort()
        X, Y, Z = [w[order] for w in (X, Y, Z)]
        n = 2
        # while X.size%n !=0: n+=1
        X, Y, Z = [w.reshape(N, -1) for w in (X, Y, Z)]
        for ind, (x, y, z) in enumerate(zip(X, Y, Z)):
            order = y.argsort()
            X[ind], Y[ind], Z[ind] = [w[order] for w in (x, y, z)]
        test = ax.plot_wireframe(X, Y, Z * 1e6, label=i if i != val else k,
                                 colors=colors(index_group))
        test.set_color('r')
        test.set_alpha(.5)
    ax.legend()
    plt.show()
    return test


"""
val = ['R_AS', 'C_PA',  'R_I']

while val:
    print '..... %s to go .....'%len(val)
    value = val.pop(0)
    for value2 in val:
        grandX, grandY,grandZ = explore2param(value,dict_val[value],  value2, dict_val[value2])
        plot2param(grandX, grandY, grandZ, paramName1 = value, paramName2 = value2, ax = None, c= None)
plt.show()
 """

cdict = {'red': ((0.0, 0.0, .5),
                 (0.25, 1, 1),
                 (0.5, 1.0, 1.0),
                 (0.75, .5, .5),
                 (1.0, 0.5, 0.0)),
         'green': ((0.0, 0.0, .5),
                   (0.25, 1.0, 1.0),
                   (0.5, 1.0, 1.0),
                   (0.75, .5, .50),
                   (1.0, 0, 0.0)),
         'blue': ((0.0, 0.0, 0.0),
                  (0.25, 0.0, 0.0),
                  (0.5, 1.0, 1.0),
                  (0.75, 1.0, 1.0),
                  (1.0, 1., 0.0))}

cdict = {'red': ((0.0, .5, .5),
                 (0.25, .5, .5),
                 (0.5, 1, 1),
                 (0.75, 1, 1),
                 (1.0, .75, .75)),
         'green': ((0.0, 0.0, 0),
                   (0.25, .5, .5),
                   (0.5, 1.0, 1.0),
                   (0.75, 1, 1),
                   (1.0, 0.75, 0.75)),
         'blue': ((0.0, 1.0, 1),
                  (0.25, 1.0, 1.0),
                  (0.5, 1.0, 1.0),
                  (0.75, .0, .0),
                  (1.0, 0., 0.0))}
ulm_colors = matplotlib.colors.LinearSegmentedColormap('my_colormap', cdict, 256)

labels = ['Potential change in PC axon',
          'Extracellular Potential',
          'Potential in Pinceau',
          'Potential change in PC soma']

Z_funcs = [lambda z: (z['Va'] - z['V_P']) + 80e-3,
           lambda z: z['V_P'],
           lambda z: (z['V_BA'] - z['V_P']),
           lambda z: z['V_S'] + 80e-3]
Zfactors = [1e6, 1e6, 1e3, 1e6]
Zunits = ['microV', 'microV', 'mV', 'microV']
Vbornes = [(-20, 20), (-20, 20), (-160, 0), (-1, 1)]
deb = 3500
end = 6500


def multiplot(X, Y, Z, xlabel='', **kwargs):
    fig = plt.figure()
    axes = [fig.add_subplot(2, 2, i) for i in range(1, 5)]
    if kwargs.has_key('xlabel'):
        xlabel = kwargs.pop('xlabel')
    for ax, lab, Z_func, Zfac, Zun, (vm, vM) in zip(axes, labels, Z_funcs, Zfactors,
                                                    Zunits, Vbornes):
        flatplot2param(X[:, deb:end] - 15e-3, Y[:, deb:end],
                       np.array([Z_func(z)[deb:end] for z in Z]), ax=ax,
                       label=0, cb=1, Zfactor=Zfac,
                       zlabel=Zun, vmin=vm, vmax=vM, **kwargs)
        ax.set_title(lab)
    axes[0].set_ylabel('time to AP peak (ms)')
    axes[2].set_ylabel('time (ms)')
    axes[2].set_xlabel(xlabel)
    axes[3].set_xlabel(xlabel)
    # fig.colorbar(axes[2].collections[0])
    return fig


def pleindeplot(t, Zs, X, Y):
    fig = plt.figure()
    axes = [fig.add_subplot(len(Zs), len(Zs[0]), i + 1) for i in range(len(Zs) * len(Zs[0]))]
    n = 0
    for ind_line, zline in enumerate(Zs):
        for ind_col, z in enumerate(zline):
            axes[n].plot(t[deb:end] * 1000, (z['Va'] - z['V_P'])[deb:end] * 1e6, 'k')
            axes[n].set_title('X =%.2f Y=%.2f' % (X[ind_line, ind_col], Y[ind_line,
                                                                          ind_col]))
            n += 1
    return fig


surfkwargs = {'rstride': 1, 'cstride': 1, 'linewidth': 0, 'cmap': ulm_colors, 'vmin': None, 'vmax': None}
wirekwargs = {'rstride': 1, 'cstride': 1, 'color': 'k'}


###############################################################################
###############################################################################
## PART MADE TO USE WITH LIF BELOW
###############################################################################
###############################################################################

def test_various_start_point(arg, t, y0, startPoints=np.linspace(-90e-3, -60e-3, 10)):
    out = {}
    for st in startPoints:
        y0[VA] = st
        y0[VS] = st
        y0[VD] = st
        out[round(st * 1000, 2)] = integrate_and_fire(y0, t, args=arg, verbose=False)
    return out


def test_various_spike_IN(arg, time, y0, sp_times=np.linspace(40e-3, 54e-3, 20),
                          withExp=None, stopAtFirstSpike=False, killPinceau=False):
    """y0 can be just the initial condition or a list of initial conditions if
    len(y0) == len(sp_times)"""
    out = {}
    if not hasattr(sp_times, '__iter__'):
        sp_times = [sp_times]
    if len(y0) != len(sp_times):
        y = lambda i: y0
    else:
        print 'use different y for each spike'
        y = lambda i: y0[i]
    F = 0 if killPinceau else 1
    _vst = np.array(arg['vsext_time'])
    _dvst = np.array(arg['dvsext_time'])
    _vsnoiset = np.array(arg['vs_noise_time'])
    import Pinceau.model.model_pgbar as pgb
    slow = None if not arg.has_key('slow') else arg['slow']
    pbar = pgb.ProgressBar(len(sp_times) - 1)
    for i, sp in enumerate(sp_times):
        pbar.animate(i)
        # print 'spike %s/%s'%(i, len(sp_times))
        sptime, spike, time_d, dspike = create_spike(cst.V_Spike_0, cst.factor, sp,
                                                     cst.PATH,
                                                     withExp=withExp, slow=slow)
        arg['vsext_time'] = _vst + sp
        arg['dvsext_time'] = _dvst + sp
        arg['vs_noise_time'] = _vsnoiset + sp
        arg['time_In'] = sptime
        arg['spike_In'] = spike * F
        arg['time_dIn'] = time_d
        arg['dspike_In'] = dspike * F
        out[sp * 1000] = integrate_and_fire(y(i), time, args=arg, verbose=False, stopAtFirstSpike=stopAtFirstSpike)
    return out


def plot_out_of_test_various(out, ax, toPlot='trueVa', **kwargs):
    cmap = cm.get_cmap('jet', len(out))
    for i, k in enumerate(sorted(out.keys())):
        v = out[k]
        if toPlot == 'trueVa':
            vt = v['va'] - v['ve']
        else:
            vt = copy(v[toPlot])
        ax.plot(copy(v['time']) * 1000, vt * 1000, c=cmap(i), label=str(k), **kwargs)
    plt.show()
    return cmap, ax


def repeat_test_various_with_different_arg(test_various, t, y0, args, test_various_kwargs={}):
    out = []
    for arg in args:
        out.append(test_various(arg, t, y0, **test_various_kwargs))
    return out


def plot_spikeplace_from_out_of_test_various(out, ax, ct_time=None, **kwargs):
    for i, In_time in enumerate(sorted(out.keys())):
        o = out[In_time]
        shift = o['sp_times']
        if ct_time is not None:
            shift = shift - ct_time
        ax.plot(shift * 1000, [i for w in shift], 'ko')
    plt.show()
    return ax


def CC(arg, t, sp_time, Nrun=100, window=17e-3, randomPCstart=0):
    y0 = np.array([-80e-3] * 3 + [0, 0.02])
    if randomPCstart:
        y0 = [copy(y0) for w in range(Nrun)]
        for i in range(Nrun):
            y0[i][:3] = np.random.random(3) * 20e-3 - 80e-3
    IN_times = np.random.random(Nrun) * window * 2 - window + sp_time
    out = test_various_spike_IN(arg, t, y0, IN_times)
    sp_times = dict([(sp, o['sp_times']) for sp, o in out.iteritems()])
    return sp_times


def cc_from_out(out, sd=.03, firstSpikeOnly=False, start=None, end=None, ctrlCase=None, dstep=None):
    if ctrlCase is not None:
        ctrl = out.pop(ctrlCase)
    in_time = np.array(sorted(out.keys()))
    pc_time = [1000 * out[i]['sp_times'] for i in in_time]
    if firstSpikeOnly:
        pc_time = [i[0] if i.size else i for i in pc_time]
    data = [pc - i for pc, i in zip(pc_time, in_time)]
    g = gaussian_density(np.array(data), sd=sd, start=start, end=end, dstep=dstep)
    return data, g


if __name__ == '__main__':
    import sys

    N_args = 3
    if len(sys.argv) > 1 and sys.argv[1] == '-do':
        if len(sys.argv) < 5:
            raise ValueError('need number of Tstart and window')
        if len(sys.argv) > 5:
            rest = sys.argv[5:]
            rest = [r.split('=') for r in rest]
            for res in rest:
                try:
                    getattr(cst, res[0])
                    getattr(cst, res[0], eval(res[1]))
                except AttributeError:
                    print 'no attribute %s' % res[0]
        fpath, arg, N, b, e = sys.argv[:5]
        N = int(N)
        b = float(b)
        e = float(e)
        ts = np.linspace(b, e, N)
        arg = getarg()
        from IPython.kernel import client
        from twisted.internet.error import ConnectionRefusedError

        maped_test_various = lambda ts: test_various_spike_IN(arg, t, y0, [ts])

        try:
            mec = client.MultiEngineClient()
            mec.execute('import os')
            mec.execute("os.chdir(os.path.expanduser('~')+'/share/Slow/Projet/Pinceau/model/')")
            mec.execute("from plot_model import *")
            mec.execute('arg = getarg()')
            mec.execute('ts = ' + repr(list(ts)))
            out = np.array(mec.map(maped_test_various, ts))
        except ConnectionRefusedError:
            print 'single process mode'
            out = np.array(map(maped_test_various, ts))

        # base  = os.path.expanduser('~')+'/share/Slow/Projet/Pinceau/model/'
        # l = [# 'spike_spont_3.npy',
        #      # 'spike_spont_4.npy',
        #      # 'spike_spont_5.npy',
        #      # 'spike_spont_6.npy',
        #      # 'spike_spont_7.npy',
        #      # 'spike_spont_8.npy',
        #      # 'spike_spont_9.npy',
        #      # 'spike_spont_10.npy',
        #      # 'spike_spont_0.5.npy',
        #      # 'spike_spont_0.7.npy',
        #      # 'spike_spont_0.9.npy',
        #      'spike_withexp.npy']#,
        #      # 'spike_spont_1.1.npy',
        #      # 'spike_spont_1.3.npy',
        #      # 'spike_spont_1.5.npy',
        #      # 'spike_spont_1.7.npy',
        #      # 'spike_spont_1.9.npy',
        #      # 'spike_spont_2.npy',
        #      # 'spike_spont_2.1.npy',
        #      # 'spike_spont_2.3.npy',
        #      # 'spike_spont_2.5.npy',
        #      # 'spike_spont_2.7.npy',
        #      # 'spike_spont_2.9.npy']

        # # figspike = plt.figure()
        # # axspike = figspike.add_subplot(111)
        # cmapspike = cm.get_cmap('jet', len(l))
        # kspike = ts[len(ts)/2]*1000
        # for ispike, name in enumerate(l):
        #     cst.PATH = base+name
        #     print "with long spike ... %s"%name
        #     out_long  = test_various_spike_IN(arg, t, y0, ts, withExp = None)
        #     in_time_long = np.array(sorted(out_long.keys()))
        #     pc_time_long = np.array([out_long[i]['sp_times'][0] for i in in_time_long])*1000
        #     # axspike.plot(out_long[kspike]['time']*1000, out_long[kspike]['vi']*1000, label = name, c = cmapspike(ispike))

        #     from ressources._common import gaussian_density
        #     # fig1 = plt.figure()
        #     # ax = fig1.add_subplot(111)
        #     data_long = pc_time_long - in_time_long
        #     g_long = gaussian_density(data_long, sd = 0.03)
        #     # val, bins,patch = ax.hist(data_long, bins = 30, histtype = 'step', color = 'b', alpha = .5)
        #     # ax.plot(g_long[0], g_long[1]/g_long[1].max()*val.max(), c = 'b', label = 'long')
        #     # ax.plot(data_long, np.ones_like(data_long), '|b', ms = 5, mew = 2)
        #     # ax.set_title(name)
        # # plt.show()

    #######################            
    elif len(sys.argv) > 1 and sys.argv[1] == '-variousNoise':
        if len(sys.argv) < 5:
            raise ValueError('need number of Tstart and window')
        if len(sys.argv) > 5:
            rest = sys.argv[5:]
            rest = [r.split('=') for r in rest]
            for res in rest:
                try:
                    getattr(cst, res[0])
                    getattr(cst, res[0], eval(res[1]))
                except AttributeError:
                    print 'no attribute %s' % res[0]
        fpath, arg, N, b, e = sys.argv[:5]
        N = int(N)
        b = float(b)
        e = float(e)
        ts = np.linspace(b, e, N)
        # creating N noise
        base = os.path.expanduser('~') + '/share/Slow/Projet/Pinceau/model/data_PC/'
        time_noise = np.load(base + 'PC_VC_time.npy')
        time_noise -= time_noise[0]
        t0 = t[0]
        tend = t[-1]
        dt = tend - t0
        length = time_noise.searchsorted(dt)
        i_noise = 0
        temp_noise = np.load(os.path.expanduser('~') + '/share/Slow/Projet/Pinceau/model/data_PC/PC_VC_sw%i.npy' % i)
        noise = []
        current_i = 0
        for i in range(N):
            if not current_i + length < time_noise.size:
                i_noise += 1
                current_i = 0
                temp_noise = np.load(
                    os.path.expanduser('~') + '/share/Slow/Projet/Pinceau/model/data_PC/PC_VC_sw%i.npy' % i_noise)
            noise.append(temp_noise[current_i: current_i + length])
            current_i += length
        trueTimeNoise = time_noise[:length] + t0
        args = []
        for i in range(N):
            args.append(getarg())
            args[-1]['vs_noise'] = (noise[i] - np.median(noise[i])) * 1e-12
            args[-1]['vs_noise_time'] = trueTimeNoise
        # noise created
        from IPython.kernel import client
        from twisted.internet.error import ConnectionRefusedError

        maped_test_various = lambda arg, ts: test_various_spike_IN(arg, t, y0, [ts])
        try:
            mec = client.MultiEngineClient()
            mec.execute('import os')
            mec.execute("os.chdir(os.path.expanduser('~')+'/share/Slow/Projet/Pinceau/model/')")
            mec.execute("from plot_model import *")
            out = np.array(mec.map(maped_test_various, args, ts))
        except ConnectionRefusedError:
            print 'single process mode'
            out = np.array(map(maped_test_various, args, ts))
        #################""

    elif len(sys.argv) > 1 and sys.argv[1] == '-variousTstart':
        if len(sys.argv) < 5:
            raise ValueError('need number of Tstart and window')
        if len(sys.argv) > 5:
            rest = sys.argv[5:]
            rest = [r.split('=') for r in rest]
            for res in rest:
                try:
                    getattr(cst, res[0])
                    getattr(cst, res[0], eval(res[1]))
                except AttributeError:
                    print 'no attribute %s' % res[0]
        fpath, arg, N, b, e = sys.argv[:5]
        N = int(N)
        b = float(b)
        e = float(e)
        ts = np.random.random(N) * (e - b) + b
        arg = getarg()
        from IPython.kernel import client
        from twisted.internet.error import ConnectionRefusedError

        maped_test_various = lambda ts: [(k, v['sp_times'] * 1000) for k, v in
                                         test_various_spike_IN(arg, t, y0, [ts]).items()]
        try:
            mec = client.MultiEngineClient()
            mec.execute('import os')
            mec.execute("os.chdir(os.path.expanduser('~')+'/share/Slow/Projet/Pinceau/model/')")
            mec.execute("from plot_model import *")
            mec.execute('arg = getarg()')
            mec.execute('ts = ' + repr(list(ts)))
            out = mec.map(maped_test_various, ts)
        except ConnectionRefusedError:
            print 'single process mode'
            out = map(maped_test_various, ts)

# for p in paces:
#     arg['pace'] = p
#     out = integrate_and_fire(y0,t, arg)
#     sp_t = out['sp_times']
#     if sp_t.size == 0:
#         out_tot.append(np.array([]))
#         continue
#     ts = np.linspace(sp_t[0] -7e-3, sp_t[0]+7e-3, 300)
#     arg['pace'] = p
#     out_tot.append(test_various_spike_IN(arg,t,y0, ts))
#     print arg['pace']

# from ressources._common import *

# gauss = {}

# for p, out in zip(paces, out_tot):
#     if len(out) ==0:
#         continue
# in_time = np.array(sorted(out.keys()))
# pc_time = [1000*out[i]['sp_times'] for i in in_time]
# data = [pc - i for pc, i in zip(pc_time, in_time)]
# g = gaussian_density(flatenList(data), sd = .03)
# g[1] *= 1000/len(in_time)
#     gauss[p] = g

# part = [g[0].searchsorted([-2,-1]) for g in gauss.itervalues()]
# for (p, g), (b,e)  in zip(gauss.iteritems(), part):
#     plot(g[0], g[1]-g[1][b:e].mean(), label = 'pace : %.2f'%(p*1e9))


"""



norm_time = [d[0][1] for d in data]
shift = [d[:,1] - n for n, d in zip(norm_time, data)]



N = 1000
out_long = dict([(i.keys()[0], i.values()[0]) for i in out])
in_time_long = np.array(sorted(out_long.keys()))
pc_time_long = np.array([out_long[i]['sp_times'][0] for i in in_time_long])*1000
data_long = pc_time_long - in_time_long
from ressources._common import *
g_long = gaussian_density(data_long, sd = 0.03)
val, bins = histogram(data_long, bins = 100)
bsize = np.diff(bins).mean()*1e-3
b=bar(bins[:-1], val/bsize, width = bsize*1e3, hold = 0)
l = plot(data_long, np.ones_like(data_long), '|k', ms = 50, mew = 0.5)

"""
