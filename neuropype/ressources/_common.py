import numpy as np
from scipy import stats

##debuging tool!
#from IPython.Shell import IPShellEmbed
#banner = '\n*** Nested interpreter *** \n\nYou are now in a nested ipython'
#exit_msg = '*** Closing embedded IPython ***'
##paramv = ['-noconfirm_exit', '-pi1','Neuropype In <\\#>:','-pi2','     .\\D.:','-po','Out<\\#>:']
#paramv = ['-pi1','Neuropype In <\\#>:','-pi2','     .\\D.:','-po','Out<\\#>:']
#ipshell = IPShellEmbed(paramv, banner=banner,exit_msg=exit_msg)
##end of debuging tool

conv_dict = {'s': 1.,
             'ms': 1/1000.,
             'micros': 1/1000000.,
             'min': 60.,
             'h': 3600.,
             'index': 1}

def checkInput(value, possibleValues, allIfNone = 1):
    """check if value is a list of element in possibleValues
    if value is None return possibleValues if allIfNone, None else"""
    if value is None:
        return possibleValues if allIfNone else None
    if not isinstance(value, list):
        value = [value]
    if any([i not in possibleValues for i in value]):
           raise ValueError('%s not in possible values'%value)
    return value

def boxfilter(sweep, w, cumulativ = None):
    w=int(w)    
    if w == 0:
        return sweep
    if cumulativ is None:
        cumulativ=sweep.cumsum()
    output=(cumulativ[w:]-cumulativ[:-w])/float(w)
    not_filtered_begin=sweep[:w/2+w%2]
    not_filtered_end=sweep[-(w/2):] if w !=1 else np.array([])
    output=np.hstack((not_filtered_begin, output,not_filtered_end))
    return output

def half_gauss_density(data, sd):
    """ Takes a sequence of spike times and produces a non-normalised density 
    estimate by summing Half-gaussian (asymetric) defined by sd at each spike
    time. The range of the output is guessed from the extent of the data (which
    need not be ordered), the resolution is automagically determined from sd; we
    currently used sd/10. A 2d np.array is returned with the time scale and 
    non-normalised 'density' as first and second rows. """
    
    # Resolution as fraction of sd
    res = 0.1
    data = np.array(data)
    dmax = np.max(data)+sd*4.
    dmin = np.min(data)-sd*4.
    dstep = sd*res
    time = np.arange(start=dmin, stop=dmax, step=dstep)
    if time.size %2 !=0:
        time = time[:-1]
    r = np.arange(0, len(time), dtype=int)
    hal = r.size/2
    gauss = np.zeros(r.size, dtype = 'float')
    gauss[hal:] =  2/np.sqrt(2*np.pi*sd**2)*np.exp(-(time[hal:])**2/
                   (2*sd**2))
    
    time, dens = kernel_density(data, np.vstack((time, gauss)))
    return np.vstack((time, dens))

def half_exp_density(data, sd):
    """ Takes a sequence of spike times and produces a non-normalised density 
    estimate by summing Half-exponential (asymetric) defined by sd at each spike
    time. The range of the output is guessed from the extent of the data (which
    need not be ordered), the resolution is automagically determined from sd; we
    currently used sd/10. A 2d np.array is returned with the time scale and 
    non-normalised 'density' as first and second rows. """
    
    # Resolution as fraction of sd
    res = 0.1
    data = np.array(data)
    dmax = np.max(data)+sd*4.
    dmin = np.min(data)-sd*4.
    dstep = sd*res
    time = np.arange(start=dmin, stop=dmax, step=dstep)
    if time.size %2 !=0:
        time = time[:-1]
    r = np.arange(0, len(time), dtype=int)
    hal = r.size/2
    exp = np.zeros(r.size, dtype = 'float')
    exp[hal:] = 2/np.sqrt(2*sd**2)*np.exp(-np.sqrt(2)*np.abs(time[hal:])/sd)
    
    time, dens = kernel_density(data, np.vstack((time, exp)))
    return np.vstack((time, dens))

def exponential_density(data, sd, start = None, end = None, dstep = None):
    """ Takes a sequence of spike times and produces a non-normalised density 
    estimate by summing Exponential defined by sd at each spike time. The range of
    the output is guessed from the extent of the data (which need not be 
    ordered), the resolution is automagically determined from sd; we currently
    used sd/10. A 2d np.array is returned with the time scale and 
    non-normalised 'density' as first and second rows. """

    data = np.array(data)
    dmax = np.max(data)+sd*4. if end is None else float(end)
    dmin = np.min(data)-sd*4. if start is None else float(start)
    
    res = 0.05
    if dstep is None:
        dstep = sd*res
    else:
        if dstep > sd *res:
            print 'Warning dstep big relative to sd'
    time = np.arange(start=dmin, stop=dmax, step=dstep)
    # dens = np.zeros_like(time)
    
    # Resolution as fraction of sd

    res = 0.1
    time = np.arange(start=dmin, stop=dmax, step=dstep)
    
    exp = 1/np.sqrt(2*sd**2)*np.exp(-np.sqrt(2)*np.abs(-time)/sd)
    
    time, dens = kernel_density(data, np.vstack((time, exp)))
    return np.vstack((time, dens))


    
def gaussian_density(data, sd, start = None, end = None, dstep = None):
    """ Takes a sequence of spike times and produces a non-normalised density 
    estimate by summing Normals defined by sd at each spike time. The range of
    the output is guessed from the extent of the data (which need not be 
    ordered), the resolution is automagically determined from sd; we currently
    used sd/10. A 2d np.array is returned with the time scale and 
    non-normalised 'density' as first and second rows. """
    
    # Note: once I've understood convolutions and Fourier transforms, they 
    # probably represent the quick way of doing this.
    # note: try to fft this
    
    # Resolution as fraction of sd
    
    data = np.array(data)
    dmax = np.max(data)+sd*4. if end is None else float(end)
    dmin = np.min(data)-sd*4. if start is None else float(start)
    
    res = 0.05
    if dstep is None:
        dstep = sd*res
    else:
        if dstep > sd *res:
            print 'Warning dstep big relative to sd'
    time = np.arange(start=dmin, stop=dmax, step=dstep)
    # dens = np.zeros_like(time)
    #def t_to_i(t):
    #    return int(round((t-dmin)/dstep))
    
    norm = 1/np.sqrt(2*np.pi*sd**2)*np.exp(-(time-time[time.size/2])**2/
           (2*sd**2))
    kernel = np.vstack((time, norm))
    time, dens = kernel_density(data, kernel, dmin = dmin, dmax = dmax)
    # for t in data:
    #      dens[t_to_i(t-sd*3.)+r] += norm 
    return np.vstack((time, dens))


def kernel_density(data, kernel, dmin = None, dmax = None):
    """Kernel density estimation
    
    Given a 2-D kernel (one line for the time, one for the values) and a
    list of time (data), compute the kde (just do the convolution basically)

    if dmin and/or dmax not None, use it as the minimum/maximum time value for
       the output
    else the output has the minimum size to fit all data points plus a kernel
       half-width


    return time, kde two 1-D arrays
    """

    dstep = kernel[0][1] - kernel[0][0]
    length = kernel[0][-1] - kernel[0][0]
    if dmin is None:
        dmin = data.min() - length/2
    if dmax is None:
        dmax = data.max() + length/2
    time = np.arange(start=dmin, stop=dmax+dstep, step=dstep)
    # add one dstep to have the smallest time bigger than dmin to dmax
    out = np.zeros(time.size, dtype = int)
    for d in data:
        out[int(round((d-dmin)/dstep))] += 1
    bigkernel = np.zeros(out.size, dtype = 'float')
    beg = bigkernel.size/2-kernel.shape[1]/2
    end = bigkernel.size/2+int(kernel.shape[1]/2.+0.5)
    bigkernel[beg:end] = kernel[1][:]
    conv = np.convolve(bigkernel, out, mode = 'same')
    return time, conv

    
    
def findextrema(sweep, maximum=1, threshold=None, pointinterval=0):
    '''Find maxima (if maximum=1/True) or minima (if maximum=0/False) that fall
    beyond threshold; requires crossing of threshold between extrema of given
    sign; if there are several (e.g.) maxima interspersed with local minima 
    beyond threshold, a single largest maximum is retained. This essentially 
    guards against noise.
    TODO: implement extrema without threshold; make "rearming" an option.'''
    deriv = np.diff(sweep)
    index = np.arange(len(sweep))
    # Should find both maxima and minima.
    # But what about inflections??
    if threshold is None:
        if maximum:
            extindex = index[np.logical_and((deriv[:-1]>0),(deriv[1:len(
                        deriv)])<=0)]+1
        else:
            extindex = index[np.logical_and((deriv[:-1]<=0),(deriv[1:]>0))
                            ] + 1
    else:
          if maximum:
              extindex = index[np.logical_and(np.logical_and((deriv[:-1]
                         >0),(deriv[1:len(deriv)])<=0),(sweep[1:len(deriv)]>
                         threshold))]+1
          else:
              extindex = index[np.logical_and(np.logical_and((deriv[:-1]
                         <=0),(deriv[1:])>0),(sweep[1:len(deriv)]<threshold))]+1
    extindex=np.array(extindex)
    if extindex.size > 1:
        # retain only the maximum in a windows of pointint points.
        cleansample = np.append(index[(extindex[1:]-extindex[:-1])>
                      pointinterval]+1,np.array(len(extindex)-1))
        
        if maximum:
            cleanextindex=np.array(max(extindex[0:cleansample[0]]), ndmin=1)
            for i in range(len(cleansample)-1):
                
                tempmax=extindex[cleansample[i]]
                value=sweep[tempmax]
                for j in extindex[cleansample[i]:cleansample[i+1]]:
                    if sweep[j]>value:
                        tempmax=j
                cleanextindex=np.append(cleanextindex,np.array(tempmax))
        else:
            cleanextindex=np.array(min(extindex[0:cleansample[0]]), ndmin=1)
            for i in range(len(cleansample)-1):
                tempmin=extindex[cleansample[i]]
                value=sweep[tempmin]
                for j in extindex[cleansample[i]:cleansample[i+1]]:
                    if sweep[j]<value:
                        tempmin=j
                cleanextindex=np.append(cleanextindex,np.array(tempmin))
    else:
        cleanextindex = np.array(extindex)
    return cleanextindex

    
def two_dim_findextrema(sweep, axis = 1, maximum=1, threshold=None, pointinterval=0):
    '''Find maxima (if maximum=1/True) or minima (if maximum=0/False) that fall
    beyond threshold; requires crossing of threshold between extrema of given
    sign; if there are several (e.g.) maxima interspersed with local minima 
    beyond threshold, a single largest maximum is retained. This essentially 
    guards against noise.
    
    Return a 2D array([[line_index, line_index ...]
                      [col_index,  col_index ...]])
    TODO: make "rearming" an option.'''
    if sweep.ndim != 2:
        raise IOError('can deal only with 2D arrays')
    if axis ==0:
        sweep = sweep.T
    deriv = np.diff(sweep, 1)
    # index = np.arange(sweep.size).reshape(sweep.shape)
    # # # add a pointint at each line to avoid bad cleaning
    # # index = np.transpose(index.T + np.arange(index.shape[0])*pointinterval)
    # # Should find both maxima and minima.
    # # But what about inflections??
    # if threshold is None:
    #     if maximum:
    #         extindex = index[np.logical_and((deriv[:,:-1]>0),(deriv[:,1:])<=0)]+1
    #     else:
    #         extindex = index[np.logical_and((deriv[:,:-1]<=0),(deriv[:,1:]>0))]+1
    # else:
    #       if maximum:
    #           extindex = index[np.logical_and(np.logical_and((deriv[:,:-1]
    #                      >0),(deriv[:,1:])<=0),(sweep[:,1:-1]>threshold))]+1
    #       else:
    #           extindex = index[np.logical_and(np.logical_and((deriv[:,:-1]
    #                      <=0),(deriv[:,1:])>0),(sweep[:,1:-1]<threshold))]+1
    # extindex=np.asarray(extindex)
    # if extindex.size > 1:

    if threshold is None:
        if maximum:
            extindex = np.where(np.logical_and((deriv[:,:-1]>0),(deriv[:,1:])<=0))
        else:
            extindex = np.where(np.logical_and((deriv[:,:-1]<=0),(deriv[:,1:]>0)))
    else:
          if maximum:
              extindex = np.where(np.logical_and(np.logical_and((deriv[:,:-1]
                         >0),(deriv[:,1:])<=0),(sweep[:,1:-1]>threshold)))
          else:
              extindex = np.where(np.logical_and(np.logical_and((deriv[:,:-1]
                         <=0),(deriv[:,1:])>0),(sweep[:,1:-1]<threshold)))
    
    if extindex[0].size > 1:
        # retain only the maximum in a windows of pointint points.
        difPt = np.diff(extindex[1])
        chLine = np.asarray(np.diff(extindex[0]), dtype = 'bool')
        
        # find groups to sort: need to be on the same line and
        # < pointinterval (if they are negativ they should be on the same line)
        cleansample = np.asarray(np.logical_and(np.logical_not(chLine),difPt <= pointinterval), dtype = 'int')
        # notOKPoints = np.hstack((cleansample[0],np.logical_or(cleansample[:-1], cleansample[1:]),
        #                          cleansample[-1]))
        # add cleansample[0] in case first is in pointint (first diff will be -1)
        # add -cleansample[-1] to add a last -1 in case it ends with a 1
        groupChg = np.hstack((cleansample[0],np.diff(np.asarray(cleansample, dtype = 'int')), -cleansample[-1]))
        begs = np.where(groupChg==1)[0]
        ends = np.where(groupChg==-1)[0]
        out = (list(extindex[0]), list(extindex[1]))
        func = np.argmax if maximum else np.argmin
        shift = 0
        for b, e in zip(begs, ends):
            line = extindex[0][b]
            totest = extindex[1][b:e+1]
            # check to delete at some point:
            assert extindex[0][e]==line
            assert all(np.diff(extindex[1][b:e]))<pointinterval
            if e+1 < len(extindex[1]):
                assert (extindex[1][e+1]-extindex[1][e])>pointinterval or  (extindex[0][e+1]-extindex[0][e]) !=0
            val = totest[func(sweep[line,totest])]
            b -= shift
            e -= shift
            out[1][e] = val
            del out[0][b:e]
            del out[1][b:e]
            shift += e-b

        out = np.array(out)
    else:
        out = np.array(extindex)
    out[1]+=1 # add one because of deriv (I think)
    return out


def cross_threshold(sweep, rise=1, maximum=1, threshold=0,pointinterval=0):
    index = np.arange(len(sweep))
    threshold=float(threshold)

    if rise:
        extindex = index[np.logical_and((sweep[1:]>threshold),(sweep[:-1]<=
                   threshold))]
    else:
        extindex = index[np.logical_and((sweep[1:]<threshold),(sweep[:-1]>=
                   threshold))] #+ 1
    
    if len(extindex) > 1:
        # retain only the maximum in a windows of pointint points.
        cleanextindex = []  
        
        cleansample=np.append(index[(extindex[1:]-extindex[:-1])>
                    pointinterval]+1,np.array(len(extindex)-1))
        #
        if maximum:
            cleanextindex=np.array(max(extindex[0:cleansample[0]]), ndmin=1)
            for i in range(len(cleansample)-1):
                
                tempmax=extindex[cleansample[i]]
                for j in extindex[cleansample[i]:cleansample[i+1]]:
                    if j>tempmax:
                        tempmax=j
                cleanextindex=np.append(cleanextindex,np.array(tempmax))
        else:
            cleanextindex=np.array(min(extindex[0:cleansample[0]]), ndmin=1)
            for i in range(len(cleansample)-1):
                
                tempmin=extindex[cleansample[i]]
                for j in extindex[cleansample[i]:cleansample[i+1]]:
                    if j<tempmin:
                        tempmin=j
                cleanextindex=np.append(cleanextindex,np.array(tempmin))
    else:
        cleanextindex = extindex
    #raise IOError
    return cleanextindex 

def flatenList(listOfArray):
    if not listOfArray:
        return np.array([])
    lengths = map(np.size, listOfArray)
    nTot = sum(lengths)
    out = np.array(np.zeros(nTot), dtype = listOfArray[0].dtype)
    n=0
    for i, j in enumerate(lengths):
        out[n:n+j] = listOfArray[i]
        n+=j
    return out

def cumulativ(arr, win2linearise = None, noTime = False):
    """do a cumulativ sum over one axis and subtract linear regression
    of win2linearise

    if arr.ndim is 1, win2linearise is the index of the first and last
    points to use
    if arr.ndim is 2, if """
    if arr.ndim == 1 or noTime:
        time = np.arange(arr.size)
        cumsum = np.array(arr, ndmin = 2).cumsum(1)
    elif arr.ndim == 2:
        time = arr[0]
        cumsum = arr[1:].cumsum(1)
    else:
        raise ValueError('need a 2-d array')

    
    if win2linearise is None:
        win2linearise = [0, time.size]
    else:
        win2linearise = time.searchsorted(win2linearise)
    out = np.array(np.zeros_like(arr), ndmin = 2)
    if arr.ndim == 2 and not noTime:
        out[0] = time
    for ind, i in enumerate(cumsum):
        gradient, intercept, r_value, p_value, std_err = \
                  stats.linregress(time, i[win2linearise[0]: win2linearise[1]])
        if r_value < 0.9:
            print 'Bad fit, gradient:%s'%gradient
            print 'intercept: %.2f'%intercept
            print 'r_value: %.2f'%r_value
            print 'p_value: %.2f'%p_value
            print 'std_err: %.2f'%std_err
        out[ind+1] = i - time*gradient + intercept
    if arr.ndim == 1:
        return out[0]
    return out
        
def filterValues(array, comp, value):
    """Test if values of an array agree with comp
    
    comp can be 0 for inferior to, 1 for superior to, 'in', or 'out' to select a
         window of value and 'among' to keep only specific values
    value is a float if comp is 0 or 1 and a doublet of float if comp is 'in' or
         'out', a list of values if comp is 'among'
    """
    if comp in [0, 1]:
        testarr = array - value
        if not comp: testarr *= -1
        out = testarr >= 0
    elif comp in ['in', 'out']:
        vals = [float(v) for v in value]
        assert len(vals) == 2
        if comp == 'in':
            out = np.logical_and(array>vals[0], array<vals[1])
        else:
            out = np.logical_and(array<vals[0], array>vals[1])
    elif comp == 'among':
        out = reduce(np.logical_or, [array == i for i in value])
    else:
        raise IOError('unknown comp: %s'%comp)
    return out

def uniquify(seq, idfun=None): 
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result
