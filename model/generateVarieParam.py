import os
from copy import deepcopy
#from IPython.kernel import client
from IPython.parallel import client
from twisted.internet.error import ConnectionRefusedError
import numpy as np
from Pinceau.CONFIG import *
from Pinceau.model.plot_model import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from Pinceau.neuropype.ressources import plot_common
_j = os.path.join

arg = getarg()
arg['pace'] = 0
R = np.linspace(0.5,1.5,11)
step = np.diff(R[:2])
Rborder = np.hstack((R,1.5+step))
# np.logspace(-0.3,0.3,11)
cmap = cm.get_cmap('jet', len(R))

params = ['R_I', 'C_BA', 'gK', 'R_L', 'C_PA',   'R_AS']
factor = {'C_BA':1e12, 'R_L':1e-6, 'C_PA':1e12, 'gK'  : 1e9, 'R_I' : 1e-6, 'R_AS':1e-6}
units = {'C_BA': 'pF', 'R_L':'MOhm', 'C_PA':'pF', 'gK'  : 'nS', 'R_I': 'MOhm', 'R_AS': 'MOhm'}
Z = [[0,0],[0,0]]
fig = myFigure(1)
zeroDone = False
axes = []
for ind, p in enumerate(params):
    ax = fig.add_subplot(int(np.ceil(np.sqrt(len(params))+0.5)), 
                         int(np.sqrt(len(params))), ind+1, facecolor = 'none', sharey = fig.axes[0] if zeroDone else None, sharex = fig.axes[0] if zeroDone else None )
    axes.append(fig.axes[-1])
    zeroDone = True
    ax.set_frame_on(False)
    CS3 = ax.contourf(Z, Rborder, cmap=cmap)
    ax.clear()
    outs = {}
    for i,r in enumerate(R):
        g = deepcopy(getarg())
        g['pace'] = 0
        g[p] = arg[p]*r
        o = integrate_and_fire(y0, t, g)
        outs[r] = o
        ax.plot((o['time']-cst.t_peak)*1000, (o['v_pa']-o['v_p']+70e-3)*1e6, color = cmap(i))
    # ax.set_title(p)
    ax.set_xlim(-2,2)
    cb = fig.colorbar(CS3, ax = ax, ticks = R+step/2.)
    
    cb.ax.set_ylabel(p)
    # cb.ax.yaxis.set_ticks(np.linspace(0,1,5))
    cb.ax.set_yticklabels(['x %.2f'%(i) if i != 1 else '%.2f %s'%(getattr(cst,p)*factor[p], units[p]) for i in R])
[plot_common.makeScale(x, -2,-50,xext = 1, yunit = 'microV', xunit = 'ms') for x in axes]
fig.savefig(_j(LOCAL, 'model/figSupvariParm.pdf'))

