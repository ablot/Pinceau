import os
import re
import numpy as np
import matplotlib
from matplotlib.transforms import Bbox, offset_copy
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.signal import resample
import scipy.stats

centered_Label = ['Baseline', 'Response', 'Peak']
timing_Label = ['20 % of rise', '50 % of rise','80 % of rise', 'peak', '20 % of decrease','50 % of rise','80 % of decrease']
lengths_Label = ['half width','20 % to peak', 'peak to 20 %', '>80 %', '>20 %']

def barPlot(ax, data, labels = None, ylabel = None, repeatedM = False, meanSd = True):
    """Barplotise one 2-D array with Nprop lines and N column in ax"""
    
    Nprop = len(data)
    if labels is None:
        labels = ['prop %i'%i for i in range(Nprop)]
    elif len(labels) != Nprop:
        raise ValueError('need %s labels'%Nprop)
    dots = [ax.plot(np.zeros_like(line)+ind, line, 'ko',
                    alpha = .5) for ind, line in enumerate(data)]
    if repeatedM:
        col = [[data[col][line] for col in range(Nprop)] for line in range(len(data[0]))]
        lines = [ax.plot(np.arange(Nprop), c, lw = .3, marker = '',
              c = 'grey', alpha = .5) for c in col]
    if meanSd:
        erbar = ax.errorbar(np.arange(Nprop), [d.mean() for d in data],
                 [d.std()/np.sqrt(d.size) for d in data],
                 ls = '', ms=10, marker = '*', c = 'orange',
                 ecolor='orange', alpha = .5)
    
    ax.yaxis.grid(True, linestyle='-', which='major',
                   color='lightgrey', alpha=0.5)
    ax.set_axisbelow(True)
    bp1 = ax.boxplot(list(data), notch=0, sym='+', vert=1,
                     whis=1.5, positions = range(Nprop))
    plt.setp(bp1['boxes'], color='black')
    plt.setp(bp1['whiskers'], color='black')
    plt.setp(bp1['fliers'], color='orange', marker='+')
    plt.setp(bp1['medians'], color='orange')
    
    M = max([d.max() for d in data])
    m = min([d.min() for d in data])
    ptp = max([d.ptp() for d in data])
    
    top = M + ptp*0.1
    bottom = m - ptp*0.1
    ax.set_ylim(bottom, top)
    ax.set_xlim(-.5,Nprop-0.5)
    ax.set_xticks(np.arange(Nprop))
    ax.set_xticklabels(labels, rotation=45)
    
    pos = np.arange(Nprop)
    upperLabels = [str(np.round(np.median(d), 2)) for d in data]
    for tick,label in zip(range(Nprop),ax.get_xticklabels()):
       ax.text(pos[tick], top-(top*0.05), upperLabels[tick],
            horizontalalignment='center', size='x-small', 
            color='k')
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    left = ax.get_xlim()[0]
    ax.text(left + abs(left)*0.05, top-(top*0.05), 'median:',
            horizontalalignment='left', size='x-small', color = 'k')
    if not meanSd:
        return dots, bp1
    return dots, erbar, bp1


def searchKin(data, time = None, part = [45,60], base= 48, res = 52,isMax = True,
              hwidth =1, peakpart = None, kin2keep = 'peak'):
    """peakpart is used to limite the place where to look for the extremum
    kin2keep can ben in ['mean', 'base', 'peak'], if peak, give the first point 
    crossing the threshold (XX % of amplitude) starting from the peak, if base, 
    give the further from the peak (first starting from part[0] for rise, and
    from part[-1] from decrease), if mean do the mean of the two
    """
    
    if time is not None:
        if any([d.ndim != 1 for d in data]):
            raise ValueError("I'm lost")
        data = [np.vstack((time, d)) for d in data]
    begpart = [np.searchsorted(l[0], part[0]) for l in data]
    endpart = [np.searchsorted(l[0],part[1]) for l in data]
    cutted = [np.array(d[:,b:e]) for d,b,e in zip(data, begpart, endpart)]
    time = cutted[0][0]
    
    if isMax:
        for i in range(len(cutted)):
            cutted[i][1:]*=-1
    if peakpart is not None:
        b,e = time.searchsorted(peakpart)
    else:
        b,e = 0, len(time)
    peak = np.array([r[1][b:e].min() for r in cutted])
    argpeak = np.array([r[1][b:e].argmin() for r in cutted])+b
    timepeak = np.array([r[0][p] for r,p in zip(cutted, argpeak)])
    
    baseline = np.array([r[1,time.searchsorted((base-hwidth)):
                           time.searchsorted((base+hwidth))].mean() for r in cutted])
    afterIn =  np.array([r[1,time.searchsorted((res-hwidth)):
                           time.searchsorted((res+hwidth))].mean() for r in cutted])

    rise20, rise50, rise80, decrease80, decrease50, decrease20 = [], [], [], [], [], []
    if kin2keep in ['mean', 'peak']:
        rise50_peak = [time[:agp][r[1,:agp] > b+(p-b)*0.5] for r, p, agp, b
                           in zip(cutted, peak, argpeak, baseline)]
        rise50.append(np.array([r[-1] if r.size else np.nan for r in rise50_peak]))
        rise80_peak = [time[:agp][r[1,:agp] > b+(p-b)*0.8] for r, p, agp, b
                           in zip(cutted, peak, argpeak, baseline)]
        rise80.append(np.array([r[-1] if r.size else np.nan for r in rise80_peak]))
        rise20_peak = [time[:agp][r[1,:agp] > b+(p-b)*0.2] for r, p, agp, b
                           in zip(cutted, peak, argpeak, baseline)]
        rise20.append(np.array([r[-1] if r.size else np.nan for r in rise20_peak]))
        decrease20_peak = [time[agp:][r[1,agp:] > b+(p-b)*0.2] for r, p, agp, b
                               in zip(cutted, peak, argpeak, baseline)]
        decrease20.append(np.array([r[0] if r.size else np.nan for r in decrease20_peak]))
        decrease50_peak = [time[agp:][r[1,agp:] > b+(p-b)*0.5] for r, p, agp, b
                               in zip(cutted, peak, argpeak, baseline)]
        decrease50.append(np.array([r[0] if r.size else np.nan for r in decrease50_peak]))
        decrease80_peak = [time[agp:][r[1,agp:] > b+(p-b)*0.8] for r, p, agp, b
                               in zip(cutted, peak, argpeak, baseline)]
        decrease80.append(np.array([r[0] if r.size else np.nan for r in decrease80_peak]))
    
    if kin2keep in ['mean', 'base']:
        rise50_bas = [time[:agp][r[1,:agp] < b+(p-b)*0.5] for r, p, agp, b
                           in zip(cutted, peak, argpeak, baseline)]
        rise50.append(np.array([r[0] if r.size else np.nan for r in rise50_bas]))
        rise80_bas = [time[:agp][r[1,:agp] < b+(p-b)*0.8] for r, p, agp, b
                           in zip(cutted, peak, argpeak, baseline)]
        rise80.append(np.array([r[0] if r.size else np.nan for r in rise80_bas]))
        rise20_bas = [time[:agp][r[1,:agp] < b+(p-b)*0.2] for r, p, agp, b
                           in zip(cutted, peak, argpeak, baseline)]
        rise20.append(np.array([r[0] if r.size else np.nan for r in rise20_bas]))
        decrease20_bas = [time[agp:][r[1,agp:] < b+(p-b)*0.2] for r, p, agp, b
                               in zip(cutted, peak, argpeak, baseline)]
        decrease20.append(np.array([r[-1] if r.size else np.nan for r in decrease20_bas]))
        decrease50_bas = [time[agp:][r[1,agp:] < b+(p-b)*0.5] for r, p, agp, b
                               in zip(cutted, peak, argpeak, baseline)]
        decrease50.append(np.array([r[-1] if r.size else np.nan for r in decrease50_bas])) 
        decrease80_bas = [time[agp:][r[1,agp:] < b+(p-b)*0.8] for r, p, agp, b
                               in zip(cutted, peak, argpeak, baseline)]
        decrease80.append(np.array([r[-1] if r.size else np.nan for r in decrease80_bas]))
    
    a= [np.array(ar).mean(0) for ar in (rise20, rise50, rise80, decrease80, 
                                                                   decrease50, decrease20)]
    rise20, rise50, rise80, decrease80, decrease50, decrease20 = a
    trise = rise80 - rise20
    tdecrease = decrease20 - decrease80
    thalfwidth = decrease50 - rise50
    timeOnpeak = decrease80 - rise80
    timetotal = decrease20 - rise20
    
    centered = np.array([baseline, afterIn, peak])
    timing = np.array([rise20, rise50, rise80, timepeak, decrease80, decrease50,
                            decrease20], dtype = 'float')
    length = np.array([thalfwidth, trise, tdecrease, timeOnpeak, timetotal])
    if isMax:
        centered*=-1
    return centered, timing, length
    


def normalise(bigArray, policy = 'baseline',**kwargs):
    """policy can be baseline, std, or n

    baseline, divide by basline, kwargs: win, window to normalise in points
    std, subtract mean and divide by std, kwargs: win, window to normalise in points
    n, area under curve to one, kwargs: n, a list of Ns"""
    if policy == 'baseline':
        if not kwargs.has_key('win'):
            raise ValueError('need a window "win" to normalise with baseline')
        w = kwargs['win']
        out = bigArray[:]/np.array(bigArray[:,w[0]:w[1]].mean(1), ndmin = 2).T
        return out
    else:
        raise NotImplementedError


def colors(label, cmap, cellNames):
    i = cellNames.index(label)
    return cmap(i)
    
def plot_all(array, ax, labels, time, cmap = None, cellNames = None, step = 50/100., absval = False, nstepForMean = 5, plotMean = True):
    N = len(labels)
    if cellNames is None: cellNames = labels
    if cmap is None: cmap = cm.get_cmap('jet', len(labels))
    for i, (l, a) in enumerate(zip(labels, array)):
        if not absval: a = np.array(a - np.mean(a))
        ax.plot(time, a+step*i, label = l, c = colors(l, cmap, cellNames))
        ax.hlines(step*i, time[0], time[-1], 'k',linestyles = 'dashed', alpha =.5)
    
    if plotMean:
        mean = array.mean(0)
        if not absval: mean -= np.median(mean)
        std = array.std(0)
        sem = std/np.sqrt(N)
        ax.plot(time, mean-step*nstepForMean, c = 'k', label = 'mean')
        ax.hlines(-step*nstepForMean, time[0], time[-1], 'k',linestyles = 'dashed', alpha =.5)
        
        # ax.plot(time, (mean-step*nstepForMean)+std, c = 'r', label = 'mean +/- std', alpha = .5)
        # ax.plot(time, (mean-step*nstepForMean)-std, c = 'r', label = '__no_legend__', alpha = .5)
        # ax.plot(time, (mean-step*nstepForMean)+sem, c = 'darkred', label = 'mean +/- sem_')
        # ax.plot(time, (mean-step*nstepForMean)-sem, c = 'darkred', label = '__no_legend__')
        ax.fill_between(time, (mean-step*nstepForMean)+sem, (mean-step*nstepForMean)-sem, alpha = .25,
                        color ='darkred', label = '__no_legend__')
        ax.fill_between(time, (mean-step*nstepForMean)+std, (mean-step*nstepForMean)-std, alpha = .1,
                        color ='r', label = '__no_legend__')
    ax.set_yticklabels([])
    ax.xaxis.grid(True)
    ax.xaxis.tick_bottom()
    ax.set_yticks([])
    return ax
    

def plotTraces(ctrlCells, arrays, labels, timeCtrl, timeGa):
    # all function can probably be erased safely
    raise ValueError("OLD FUNCTION DETECTION")
    labCtrl, labTr, labGa = labels
    norm_Ctrl, norm_Tr, norm_Ga = arrays
    factor = 2
    cmap = cm.get_cmap('jet', len(ctrlCells))
    
    fig = plt.figure()
    fig.set_frameon(True)
    fig.set_facecolor('w')
    
    fig.subplots_adjust(wspace=0.05, hspace=0.05, top=0.95, bottom=0.05, left = 0.02, right = 0.98)
    ax0 = fig.add_subplot(121)
    ax1 = fig.add_subplot(122, sharex = ax0, sharey =ax0)
    time2keep = [-20,20]
    parts = timeCtrl.searchsorted(time2keep)
    step = 20
    units = 'Hz'
    
    ax_Ctrl = plot_all(norm_Ctrl[:,parts[0]:parts[1]],ax0, labCtrl, timeCtrl[parts[0]:parts[1]],cmap = cmap, cellNames = labCtrl, step = step)
    parts = timeGa.searchsorted([-20,20])
    ax_Ga = plot_all(norm_Ga[:,parts[0]:parts[1]],ax1, labGa, timeGa[parts[0]:parts[1]],cmap = cmap, cellNames = labCtrl, step = step)
    ax0.legend(bbox_to_anchor = (1,1))
    ax0.set_xlabel('Time (ms)')
    ax1.set_xlabel('Time (ms)')
    
    x = 5
    ym = step *-1.5
    yM = step * -0.5
    ax1.plot([x, x], [ym,yM ], 'k', lw = 3, label = '__no_legend__')
    ax1.text(x-1, (ym+yM)/2., '%.2f %s'%(step, units), horizontalalignment = 'right',
            verticalalignment = 'center')
    ax1.set_xlim(*time2keep)
    ax1.set_ylim(step * -5, step * (len(norm_Ga)+0.25))
    
    # ax0.plot([-5, -5], [0.25, 0.75], 'k', lw = 3, label = '__no_legend__')
    # ax0.text(-5.2, 0.5, '50%', horizontalalignment = 'right', verticalalignment = 'center')
    # ax1.plot([-5, -5], [0.25, 0.75], 'k', lw = 3, label = '__no_legend__')
    # ax1.text(-5.2, 0.5, '50%', horizontalalignment = 'right', verticalalignment = 'center')
    ax0.xaxis.grid(True)
    ax1.xaxis.grid(True)
    return fig

def makeScale(ax, x, y, xext = "match", yext = "match", xunit = 'n.d.', 
              yunit = 'n.d.', w= 4, hidex = None, hidey = None, **kwargs):
    def f(axis):
        l = axis.get_majorticklocs()
        return len(l)>1 and (l[1] - l[0])
    if hidex is None:
        hidex = True if xext is not None else False
    if hidey is None:
        hidey = True if yext is not None else False
    fig = ax.figure
    x_size, y_size = fig.get_size_inches()
    wx = w/72./x_size # /72 to go from point to inches
    wy = w/72./y_size
    bbox = Bbox.from_bounds(0,0,wx, wy) # bbox to create "vector"
    displayScale = fig.transFigure.transform(bbox)
    dataBbox = ax.transData.inverted().transform(displayScale)
    _,_,Wx,Wy = Bbox.from_extents(dataBbox).bounds
    # transWX = blended_transform_factory(ax.transData, fig.transFigure)
    # transWY = blended_transform_factory(fig.transFigure, ax.transData)
    out = []
    if yext is not None:
        if yext == "match":
            yext = f(ax.yaxis)
        rect = matplotlib.patches.Rectangle((x,y),Wx,yext, facecolor = 'k', 
                                            edgecolor = 'none', **kwargs)
        l = ax.add_patch(rect)
        # l = ax.vlines(x, y,y+yext, 'k', linewidth = w)
        out.append(l)
        if yunit is not None:
            yt = y + yext/2.
            transy = offset_copy(ax.transData, x=-2, y=0, units='points', fig = fig)
            txt = '%i %s'%(yext, yunit) if isinstance(yext, int) else '%.2f %s'%(yext, yunit)
            tx=ax.text(x, yt, txt, transform = transy,
                    verticalalignment = 'center', horizontalalignment = 'right')
            out.append(tx)
    if xext is not None:
        if xext == "match":
            xext = f(ax.xaxis)
        rect = matplotlib.patches.Rectangle((x,y),xext,Wy, facecolor = 'k', 
                                            edgecolor = 'none', **kwargs)
        l = ax.add_patch(rect)
        # l = ax.hlines(y, x,x+yext, 'k', linewidth = w)
        out.append(l)
        if xunit is not None:
            transx = offset_copy(ax.transData, x=0, y=-2, units='points', fig = fig)
            xt = x + xext/2.
            txt = '%i %s'%(xext, xunit) if isinstance(xext, int) else '%.2f %s'%(xext, xunit)
            tx=ax.text(xt, y, txt, transform = transx,
                    verticalalignment = 'top', horizontalalignment = 'center')
            out.append(tx)
    if hidex : ax.xaxis.set_visible(False)
    if hidey : ax.yaxis.set_visible(False)
    return out
