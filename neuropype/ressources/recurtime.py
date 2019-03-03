import numpy as np
import sys,os
import matplotlib.pyplot as plt

# p = os.path.join(os.path.expanduser('~') , 'share/Python/neuropype')
# if p not in sys.path: sys.path.append(p)

from neuropype.ressources._common import *

def _cc(ls0, ls1, trange, lastBefCond = None, keep_zero = True):
    dts =[]
    ls0.sort()
    ls1.sort()

    for spike in ls0:
        trangei = ls1.searchsorted(spike+trange)
        # find where the trange around this spike would fit in other.spikes
        if hasattr(trangei, 'count'):
            if not trangei.count():
                dts.append(np.array([]))
                continue
        dt = ls1[trangei[0]:trangei[1]] - spike
        if lastBefCond is not None:
            lastBef = dt[:dt.searchsorted(0)]
            if lastBef.size:
                lastBef = lastBef[-1]
                if cmp(lastBef, lastBefCond[1]) != lastBefCond[0]:
                    dt = np.array([])
            elif lastBefCond[0] in [0,1]:
                dt = np.array([])
            # find dt between this spike and only those other.spikes that are in trange of this spike
        dts.append(dt)
    #ipshell()
    if not keep_zero:
        dts = [line[line != 0] for line in dts]
    return dts


def recurtime(array0, array1,border =None):
    """Return a list of time bef and time aft array0
    
    if border is None, put None for missing values (first and last time)
    if border is "exclude" keep only time with a tbef and a taft
    """
    if not array0.size or not array1.size:
        print "One empty array in recurtime"
        if border is None:
            return [np.ones(array0.size)*np.inf]*2
        else:
            return [np.array([])]*2
    ind = array1.searchsorted(array0)
    
    #first deal with the middle:
    ok = np.logical_and(ind >0, ind < len(array1))
    # if ind == 0, then there is no tbef
    # if ind == len(i), then there is no taft
    trueInd = ind[ok]
    tbef = array1[trueInd-1]
    taft = array1[trueInd]
    waszero = taft == array0[ok]
    tbef[waszero] = array0[waszero]
    #two lines to make sure coincidence are detected
    befs = array0[ok]-tbef
    afts = taft-array0[ok]
    if border == 'exclude':
        return befs,afts 

    # now deal with the borders if needed 
    else:
        noBef = np.sum(ind == 0)
        befsHead = np.ones(noBef)*np.inf
        aftsHead = array1[0]-array0[:noBef]
        noAft = np.sum(ind == len(array1))
        befsTail = array0[-noAft:]-array1[-1] if noAft != 0 else np.array([])
        aftsTail = np.ones(noAft)*np.inf
        befs = np.hstack((befsHead, befs,befsTail))
        afts = np.hstack((aftsHead, afts,aftsTail))
    return befs, afts

def epdf(array, step = 1, start = None, end = None, x = None):
    """ Compute an histogram of probability density fonction of an array
    x is an array of len = len(array)+1, it's the borders of the histo
    if x is None, an x is computed from start, end and step,
    
        
    return x, the time corresponding and the edpf at that values"""
    if x is not None:
        if start is not None or end is not None:
            raise ValueError('cannot use start/end AND x')
    else:
        if start is not None:
            array = array[array>start]
        else:
            start= array.min()
        if end is not None:
            array = array[array<end]
        else:
            end = array.max()
        x= np.arange(start, end, step)
    deltas = np.diff(x)
    array.sort()
    pdf = np.diff(array.searchsorted(x))/(deltas*array.size)
    return x[:-1],pdf


def recurTest(train0, train1, step, start = None, end = None):
    """trains must be two list of arrays"""
    ISI = [np.diff(t) for t in train0]
    isi = flatenList(ISI)
    N_b = flatenList(train1).size
    
    x, pdf_isi = epdf(isi, step, start = start, end = end)
    ecdf_isi = np.cumsum(pdf_isi)*step
    E_isi = isi.mean()
    pv_0 = 1/E_isi * (ecdf_isi[-1] - ecdf_isi)

    befs, afts = [flatenList(i) for i in recurtime(train0, train1)]
    Npv_bef, xb = np.histogram(befs, np.hstack((x,x[-1]+step)))
    Npv_aft, xt = np.histogram(afts, np.hstack((x,x[-1]+step)))
        
    sigma = np.sqrt(N_b * pv_0 *step * (1-pv_0 *step))

    res_b = Npv_bef-pv_0*N_b*step
    res_a = Npv_aft-pv_0*N_b*step
    return x, isi, pv_0, Npv_bef, Npv_aft, res_b, res_a, sigma

def stack_bef_aft(x, res_b, res_a, sigma):
    res = np.hstack((res_b[::-1], res_a))
    x = np.hstack((-x[::-1], x))
    s = np.hstack((sigma[::-1], sigma))
    return x, res, s
    
def plot_recur(x, residual, sigma, nsigm = 4, ax = None):
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    ax.fill_between(x, nsigm*sigma, -nsigm*sigma, color = 'grey', alpha = .3)
    ax.plot(x,residual,  color = 'k', drawstyle = 'steps-post')
    pos_sign = residual>nsigm*sigma
    neg_sign = residual<-nsigm*sigma
    ax.bar(x[pos_sign], residual[pos_sign]-nsigm*sigma[pos_sign], np.diff(x[:2])[0],
           bottom= nsigm*sigma[pos_sign], color= 'r', lw= 0,alpha = .5)
    ax.bar(x[neg_sign], residual[neg_sign]+nsigm*sigma[neg_sign], np.diff(x[:2])[0],
           bottom= -nsigm*sigma[neg_sign], color= 'b', lw= 0,alpha = .5)
    ax.set_xlim(-25,25)
    return ax, pos_sign, neg_sign

def full_test(train0, train1, start = 0, end = 50, step = .5, nsigm =4):
    x, isi, pv_0, Npv_bef, Npv_aft, res_b, res_a, sigma = recurTest(train0, train1, step, start, end)
    X, R, S = stack_bef_aft(x, res_b, res_a, sigma)
    ax, psig, nsig = plot_recur(X, R,S, nsigm)
    return X, R,S, psig, nsig,ax 
