from neuropype import node
import matplotlib.cm as cm
from neuropype.ressources._common import gaussian_density, flatenList, exponential_density, conv_dict
from neuropype import parameter

from numpy import array

import numpy as np
import neuropype.ressources.progressbar as pgb
from neuropype.ressources.recurtime import _cc


class CrossCorr(node.Node):
    '''
    kernel can be "gauss" or "exp"
    '''
    def __init__(self, name, parent):
        self.in0_times = node.Input('Time_list')
        self.in0_numSweeps = node.Input('int')
        self.in1_times = node.Input('Time_list')
        self.in1_numSweeps = node.Input('int')
        
        super(CrossCorr, self).__init__(name, parent)
        self._inputGroups['time_list0'] = {'time_list': 'in0_times',          \
        'numSweeps': 'in0_numSweeps'}
        self._inputGroups['time_list1'] = {'time_list': 'in1_times',          \
        'numSweeps': 'in1_numSweeps'}
        
        
        #defining parameters
        keep_zero = parameter.boolean('keep_zero', self, True)
        inverse = parameter.boolean('inverse', self, False)
        units = parameter.combobox('units', self, sorted(conv_dict.keys()),
                                   'ms')
        bins = parameter.integer('bins', self, 100, minVal= 1)
        sd = parameter.float_param('sd', self, 1/40.)
        
        self._params = {'keep_zero' : keep_zero, 
                        'sd': sd, 
                        'trange': [-50, 50], 
                        'units': units, 
                        'bins': bins, 
                        'inverse': inverse,
                        'graphviz':{'style': 'filled',
                                    'fillcolor': 'palegreen'},
                        'kernel':'gauss',
                        'lastBefCond':None}

    def numSweeps(self):
        return min(self.in0_numSweeps(),self.in1_numSweeps())
        
    def single_cross_cor(self, index_sweep):
        """lastBefCond can be None or (cond, boundary)"""
        lastBefCond = self.get_param('lastBefCond')
        dts = self.get_cache(index_sweep)
        if dts is not None:
            return dts
        
        trange = self.get_param('trange')
        time_list0 = self.in0_times(index_sweep)
        ls0 = time_list0.get_data(units = self.get_param('units'))
        # if hasattr(ls0, 'count'):
        #     if not ls0.count():
        #         return []
        time_list1 = self.in1_times(index_sweep)
        ls1 = time_list1.get_data(units = self.get_param('units'))
        # if hasattr(ls1, 'count'):
        #     if not ls1.count():
        #         return []
        if self.get_param('inverse'):
            temp = ls0
            ls0 = ls1
            ls1 = temp
        dts = _cc(ls0, ls1, trange, lastBefCond = lastBefCond, keep_zero = self.get_param('keep_zero'))        
        self.set_cache(index_sweep, dts)
        return dts
    
    def cross_corr(self, listofsweep = None):
        print 'Doing crosscorr'
        if listofsweep is None:
            listofsweep = range(min(self.in0_numSweeps(),
            self.in1_numSweeps()))
        if not isinstance(listofsweep, list):
            listofsweep = [int(listofsweep)]
        cor=[]
        pbar = pgb.ProgressBar(maxval=len(listofsweep), term_width = 79).     \
        start()

        for (j,i) in enumerate(listofsweep):
            cor.extend(self.single_cross_cor(i))
            pbar.update(j)
        pbar.finish()

        return cor

    def kde(self, flatcor, normalise = True):
        k = self.get_param('kernel')
        s, e = self.get_param('trange')
        if k == 'gauss':
            #print 'gauss'
            gauss=gaussian_density(flatcor,self.get_param('sd'), start = s, end = e)
        elif k == 'exp':
            print 'exp'
            gauss=exponential_density(flatcor,self.get_param('sd'), start = s, end = e)
        else:
            raise ValueError('unknown param for kernel: %s'%k)
        #print 'plot'
        if normalise:
            gauss[1] /= flatcor.size
        return gauss
    
    def plot_CC(self, ax, listofsweep = None, cor = None, clearAx = True, **kwargs):
        if cor is None:
            cor = self.cross_corr(listofsweep)
        trange = self.get_param('trange')
        if clearAx: ax.clear()
        print 'flatening cor'
        onelinecor = flatenList(cor)
        gauss = self.kde(onelinecor)
        
        
        a=ax.hist(onelinecor, bins = self.get_param('bins'),**kwargs)
        ax.plot(gauss[0], gauss[1]*a[0].max()/gauss[1].max(), lw=1)
        ax.set_xlim(trange[0], trange[1])
        ax.set_title(self.name)
        
        del(a)
        ax.set_xlabel('time (ms)')
        ax.figure.canvas.draw()
        
        #print 'end !!'
        return ax
    
    def raster(self, ax, listofsweep = None, cor = None, Sorted = False,
               showSw_ind = False, maxNumLine = 1000, numCol = 200, colorbar =
               True, simplify = True, **kwargs):
        if cor is None:
            cor = self.cross_corr(listofsweep)
        
        if Sorted:
            withspikesbef = np.array([], dtype ='int16')
            nospikesbef = np.array([], dtype ='int16')
            last_bef = np.array([])
            print "Sorting cor"
            pbar = pgb.ProgressBar(maxval=len(cor), term_width = 79).     \
            start()
            if Sorted == 'bef':
                for i,line in enumerate(cor):
                    pbar.update(i)
                    last_spike = line[line<0]
                    if last_spike.size > 0:
                        last_bef = np.append(last_bef, last_spike[-1])
                        withspikesbef = np.append(withspikesbef, i)
                    else:
                        nospikesbef = np.append(nospikesbef,i)
                    pbar.finish()
                    
                    sortedind = withspikesbef[last_bef.argsort()]
            elif Sorted == 'aft':
                for i, line in enumerate(cor):
                    pbar.update(i)
                    last_spike = line[line>0]
                    if last_spike.size > 0:
                        last_bef = np.append(last_bef, last_spike[0])
                        withspikesbef = np.append(withspikesbef, i)
                    else:
                        nospikesbef = np.append(nospikesbef,i)
                    pbar.finish()
                    
                    sortedind = withspikesbef[last_bef.argsort()]
            else:
                raise ValueError('unkwnown argument for sorted')
            argsort = np.hstack((nospikesbef,sortedind))
            cor = [cor[i] for i in argsort]
        else:
            argsort = range(len(cor))
        print "plotting cor"
        #pbar = pgb.ProgressBar(maxval=len(argsort), term_width = 79).     \
        #       start()
        
        if simplify and len(cor)>maxNumLine:
            step = int(np.ceil(len(cor)/float(maxNumLine)))
            trange = self.get_param('trange')
            cols = np.linspace(trange[0],trange[1], numCol+1) #to diff later
            out = np.zeros((maxNumLine, numCol))
            n = 0
            i = 0
            while n < len(cor):
                flat = sorted(flatenList(cor[n:n+step]))
                inds = [np.searchsorted(flat, c) for c in cols]
                out[i] = np.diff(inds)
                i+=1
                n+=step
            if i < maxNumLine:
                #len(cor) not exactly divisible by maxNumLine
                flat = sorted(flatenList(cor[n-step:-1])) #takes what's left
                inds = [np.searchsorted(flat, c) for c in cols]
                out[i] = np.diff(inds) #there should be a i+=1 left from the last while
            X, Y = np.meshgrid(cols[1:],np.arange(maxNumLine))
            pc = ax.pcolor(X, Y, out, cmap = cm.Greys)
            if colorbar:
                ax.figure.colorbar(pc, ax = ax, orientation='horizontal')
        else: 
            lengths = map(np.size, cor)
            nTot = sum(lengths)
            out = np.array(np.zeros(nTot), dtype = cor[0].dtype)
            outsortedindex = np.array(np.zeros(nTot), dtype = 'int')
            outindex = np.array(np.zeros(nTot), dtype = 'int')
            n=0
            for i, j in enumerate(lengths):
                out[n:n+j] = cor[i]
                outsortedindex[n:n+j] = np.ones(j)*i
                outindex[n:n+j] = np.ones(j)*argsort[i]
                n+=j
            if showSw_ind:
                if kwargs.has_key('c'):
                    print 'kwarg "c" incompatible with option "showSw_ind"'
                kwargs['c'] = np.array(outindex, dtype = 'float')*255/outindex.max()
                
            if not kwargs.has_key('c'): kwargs['c'] = 'k'
            if not kwargs.has_key('marker'): kwargs['marker'] = 'o'
            if kwargs.has_key('showSw_ind'): kwargs.pop('showSw_ind')
            ax.scatter(out, outsortedindex,  **kwargs)
            #for index, i in enumerate(argsort):
            #    pbar.update(index)
            #    ax.plot(cor[i], [index for n in cor[i]], 'ko', **kwargs)
            ax.set_xlabel('time (%s)'%self.get_param('units'))
            ax.set_ylim(outindex.min(), outindex.max())
            #pbar.finish()
            ax.figure.canvas.draw()
            return ax
    
    def plot_crosscorr(self, fig, listofsweep = None, cor = None, showSw_ind = False,
                       rasterKwargs ={}, histKwargs = {}):
        if cor is None:
            cor = self.cross_corr(listofsweep)
        fig.clear()
        ax0 = fig.add_subplot(211)
        ax1 = fig.add_subplot(212, sharex = ax0)
        self.raster(ax0, listofsweep, cor = cor,showSw_ind = showSw_ind, **rasterKwargs)
        self.plot_CC(ax1, listofsweep, cor = cor, **histKwargs)
        return fig
     
    def notIsolatedSpikes(self, sweep):
        """return a list of boolean arrays (one per sweep) indicating if there
        is a least one spike in times1 in trange around each spike of times0
        
        Arguments:
        - `sweep`: sweep index or list of sweep indices
        """
        
        if not isinstance(sweep, list):
            sweep = [int(sweep)]
            delist = True
        else:
            sweep = [int(i) for i in sweep]
            delist = False
        
        out = []
        for i in sweep:
            out.append([c.size != 0 for c in self.single_cross_cor(i)])
        
        if delist: return out[0]
        return out
            
        
    def save(self, name = None, force = 0):
        """Save crossCorr in file 'name' (can only save ALL the times at once)

        'name' is absolute or relative to parent.home
        if 'force', replace existing file
        """
        import os
        if name is None:
            name = self.parent.name+'_'+self.name+'_crossCorr.npz'
        if name[0] != '/':
            path = self.parent.home + name
        data = self.cross_corr()
        np.savez(name, **dict([('sw_'+str(i), d) for i, d in enumerate(data)]))
        
