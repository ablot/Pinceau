# -*- coding: utf-8 -*-
from numpy import exp, log10
import numpy as np
import os, sys
from constante import cst
from copy import copy
from Pinceau.model.PC_model_Khaliq import *
#see PICKMODEL to change

fixedV_S = False
VDi, VSi, VPAi, VEi, Ni, Hi = range(6)


path = os.path.join(os.path.expanduser('~'), 'share/Python/neuropype')
if path not in sys.path:
    sys.path.append(path)

from Pinceau.neuropype.ressources._common import flatenList
y0 = cst.y0
t = cst.time #time (s)

def getarg(spvals = None):
    out =  dict([(i,getattr(cst, i)) for i in ['R_I', 'R_L', 'R_AS', 'R_J', 'C_BA',
                                               'C_PA', 'C_S', 'C_D', 'gK', 'EK',
                                               'cK0', 'cK1', 'LIF_th', 'R_E',
                                               'LIF_val', 'pace', 'R_P',
                                               'vs_noise', 'vs_noise_time',
                                               'vsext', 'vsext_time',
                                               'dvsext', 'dvsext_time', 'gLEIF',
                                               'V_TEIF', 'delta_TEIF', 'tau_rp']])
    
    if spvals is None:
        time, spike, time_d, dspike = create_spike(cst.V_Spike_0,cst.factor, cst.t_peak,
                                                   cst.PATH)
    else:
        time, spike, time_d, dspike = spvals
    out['time_In'] = time
    out['spike_In'] = spike
    out['time_dIn'] = time_d
    out['dspike_In'] = dspike
    return out
    
#########################################################################
### Creating spike
#########################################################################
def create_exp(tstart, tend, V_Start, V_Pnd, A = None, tau = None, dV_Pnd = None):
    if A is None and tau is None and dV_Pnd is None:
        raise V_PAlueError('you must specify A or tau')
    if A is not None:
        tau = (tend-tstart)/(np.log((V_Pnd-V_Start)/A)+1)
    elif tau is not None:
        A = (V_Pnd-V_Start)/(exp((tend-tstart)/tau)-1)
        
    return lambda t: A*(np.exp((t-tstart)/tau)-1)+V_Start
    
def create_spike(Vinit, factor, t_peak, path, chan = 1, withExp = None, slow= None):
    """ex of with exp: {'tstart' : -4e-3, 'tend':-0.34e-3, 'tau':0.15e-3}
    spike is an induced spike in interneuron, with peak at time = 15 ms"""
    data = np.load(path)
    if withExp is not None:
        tstart = withExp['tstart']
        tend = withExp['tend']
        tau = withExp['tau']
        beg = data[0].searchsorted(tstart)
        end = data[0].searchsorted(tend) -1
        V_Start = data[chan][beg]
        V_Pnd = data[chan][end]
        f = create_exp(tstart, tend, V_Start, V_Pnd, tau = tau)
        data[1][beg:end+1] = f(data[0][beg:end+1])
    
    spike = (data[chan] - data[chan][0])*factor + Vinit
    time = data[0]

    if slow is not None:
        argpk = spike.argmax()
        slowtime = np.array(time)
        slowtime[argpk:]= slowtime[argpk]+np.arange(slowtime.size - argpk)*np.diff(time[:2])/float(slow)
        spike = np.interp(slowtime, time, spike)
    
    dt = time[1] - time[0]
    time += t_peak
    dspike = np.diff(spike)/dt
    time_d = time[:-1]+dt/2.
    return time, spike, time_d, dspike

# time, spike, time_d, dspike = create_spike(cst.V_Spike_0,cst.factor, cst.t_peak,
#                                            cst.PATH)
# timeV_S, spikeV_S, time_dV_S, dspikeV_S = create_spike(-60e-3, 1, 10e-3,
#                                            os.path.expanduser('~') +
#                                                    '/share/Slow/Projet/Pinceau/model/V_PAfixed.npy',
#                                            chan = 1)


def Vi_func(t, time, spike):
    """return value of Vi at time t (s) using simple linear interpolation"""
    dt = time[1]-time[0]
    t0 = time[0]
    if t < t0:
        return spike[0]
    t -= t0
    ind_t = int(t/dt)
    shift = t - dt*ind_t
    if ind_t+1 >= len(spike):
        ind_t = len(spike)-2
    out = (spike[ind_t]*(dt-shift) + spike[ind_t+1]*shift)/dt
    return out

def dVi_func(t, time_d, dspike):
    dt = time_d[1]-time_d[0]
    t0 = time_d[0]
    if t < t0:
        return 0
    if t > time_d[-1]:
        return 0
    t -= t0
    ind_t = int((t-dt/2.)/dt)
    shift = t - (dt*ind_t + dt/2.)
    if ind_t+1 >= len(dspike):
        ind_t = len(dspike)-2
    out = (dspike[ind_t]*(dt-shift) + dspike[ind_t+1]*shift)/dt
    return out

# def V_S_func(t):
#     """return value of V_S at time t (s) using simple linear interpolation"""
#     dt = timeV_S[1]-timeV_S[0]
#     t0 = timeV_S[0]
#     if t < t0:
#         return spikeV_S[0]
#     t -= t0
#     ind_t = int(t/dt)
#     shift = t - dt*ind_t
#     if ind_t+1 >= len(spikeV_S):
#         ind_t = len(spikeV_S)-2
#     out = (spikeV_S[ind_t]*(dt-shift) + spikeV_S[ind_t+1]*shift)/dt
#     return out

# def dV_S_func(t):
#     dt = time_dV_S[1]-time_dV_S[0]
#     t0 = time_dV_S[0]
#     if t < t0:
#         return 0 
#     if t > time_dV_S[-1]:
#         return 0
#     t -= t0
#     ind_t = int((t-dt/2.)/dt)
#     shift = t - (dt*ind_t + dt/2.)
#     if ind_t+1 >= len(dspikeV_S):
#         ind_t = len(dspikeV_S)-2
#     out = (dspikeV_S[ind_t]*(dt-shift) + dspikeV_S[ind_t+1]*shift)/dt
#     return out


#########################################################################
### V_Sext functions 
#########################################################################

def V_Sext_func(t, vs_noise_time, vs_noise):
    if vs_noise is None or vs_noise_time is None:
        return 0
    
    if not isinstance(vs_noise_time, np.ndarray):
        vs_noise_time = np.load(vs_noise_time)
    if not isinstance(vs_noise, np.ndarray):
        vs_noise = np.load(vs_noise)
    vs_out = Vi_func(t, vs_noise_time, vs_noise)
    return vs_out

def dV_Sext_func(t, dvsext_time, dvsext):
    if dvsext is None or dvsext_time is None:
        return 0
    
    if not isinstance(dvsext_time, np.ndarray):
        dvsext_time = np.load(dvsext_time)
    if not isinstance(dvsext, np.ndarray):
        dvsext = np.load(dvsext)
    dvsext_out =  dVi_func(t, dvsext_time, dvsext)
    return dvsext_out


#########################################################################
### Ik functions from pinceau PICKMODEL
#########################################################################
# Kmid = {'G': lambda m: m**4,
#          'Gmax': 20, # in pS/cm**2
#          'm': {'V_demi':-24, #in mV
#                'k':20.4, #in mV
#                'y0' : 0},
#         'E':-88
#         }

# def m_inf(V):
#     v = V*1e3
#     p = Kmid['m']
#     val = m_inf_func(p['y0'], v, p['V_demi'], p['k'])
#     return val
# def tau(V):
#     return Kmid_mtau_func(V*1e3)

# def tau(V):
#     return Kfast_mtau_func(V*1e3)

# def tau(V):
#     return Kslow_mtau_func(V*1e3)

# def tauh(V):
#     return Kfast_htau_func(V*1e3)

def m_inf(V):
    """From robertson and southan data, own fit with N =4 """
    Volt = V * 1e3
    V_Demi_1 = -73.95
    k1 = 26.99
    return 1/(1+exp(-(Volt-V_Demi_1)/k1))

def tau(V):
    """Fit of log10(tau) from southan and robertson
    using text values and tau(-20 mV) = 1 ms"""
    Volt = V *1e3
    Vh,k,O = [ 19.36137782,  33.10434917,   0.50615474]
    tau_func1 = lambda V : 1/np.exp((V+k)/Vh)+O
    tau_ms = tau_func1(Volt)
    """ using Q10 = 3 => 3 = (tau_hot/tau_RT)**(10/(T_hot - RT))
    so: tau_hot**X = 3*tau_RT**X
    and: tau_hot = 3**1/(10/(T_hot-RT)) * tau_RT
    """
    #tau_ms *= 1/3**((35-21.5)/10.)
    return tau_ms*1e-3

# mh = None

# def mh(V):
#     v = V*1e3
#     p = Kfast['h']
#     val = m_inf(p['y0'], v, p['V_demi'], p['k'])
#     return val

    
def alpha(tau, m_inf):
    """C_PAlculate HH alpha from tau and m"""
    return m_inf/float(tau)

def beta(tau, m_inf):
    """C_PAlculate HH beta from tau and m"""
    return (1-m_inf)/float(tau)
    
def IK(y, arg):
    if cst.useH:
        arg['gK']*y['n']**arg['cK0']*y['h']*(y['V_BA']-y['V_P']-arg['EK'])
    return arg['gK']*y['n']**arg['cK0']*(y['V_BA']-y['V_P']-arg['EK'])
#########################################################################
### Creating noise
#########################################################################

def V_S_noise_func(t, vs_noise_time, vs_noise):
    if vs_noise is None or vs_noise_time is None:
        return 0
    
    if not isinstance(vs_noise_time, np.ndarray):
        vs_noise_time = np.load(vs_noise_time)
    if not isinstance(vs_noise, np.ndarray):
        vs_noise = np.load(vs_noise)
    vs_out = Vi_func(t, vs_noise_time, vs_noise)
    return vs_out
        
    
    

#########################################################################
### dV funcs
### y = dict with V_D, V_S, V_PA, V_P, n,V_BA, Vi,dVi
### arg = (R_I, R_L, R_AS, R_J, C_BA, C_PA, C_S, C_D, gK, EK, cK0, cK1 )
#########################################################################
def dN(y, arg):
    V = y['V_BA']-y['V_P']
    return (m_inf(V)-y['n'])/(tau(V)*arg['cK1'])

def dH(y, arg):
    V = y['V_BA']-y['V_P']
    return (mh(V)-y['h'])/(tauh(V)*arg['cK1'])

def dV_D(y, arg):
    pace = arg['pace'] if arg.has_key('pace') else 0
    vs_noise = y['vs_noise'] if y.has_key('vs_noise') else O
    
    return (y['V_S'] - y['V_D'])/(arg['R_J']*arg['C_D']) - vs_noise/arg['C_D'] + pace #+ pace + vs_noise

def dV_S(y, arg):
    pace = arg['pace'] if arg.has_key('pace') else 0
    vs_noise = y['vs_noise'] if y.has_key('vs_noise') else O
    
    return 1/arg['C_S']*((y['V_PA']-y['V_S'])/arg['R_AS'] - (y['V_S']- y['V_D'])/arg['R_J'] - vs_noise) + pace + y['dvsext']

def dV_P(y, arg):
    C_eq = 1/(arg['R_I']/(arg['R_AS']*arg['C_PA']) - 1/arg['C_BA'])
    return arg['R_AS']*arg['R_L']/(arg['R_I']*arg['R_AS']+arg['R_I']*arg['R_L']+arg['R_L']*arg['R_AS'])*(
               (y['V_PA']-y['V_S']) / (arg['R_AS']* C_eq)
                + y['dVi'] 
                + dV_S(y, arg) * arg['R_I']/arg['R_AS']
                - y['V_P'] /(arg['C_BA']*arg['R_L'])
                + IK(y, arg)/arg['C_BA'])

def dV_PA(y, arg):
    #ve = y['V_P'] * arg['R_P']/(arg['R_E']+arg['R_P'])
    pace = arg['pace'] if arg.has_key('pace') else 0
    #EIF = phi(y['V_PA']-ve, arg['gLEIF'], arg['V_TEIF'], arg['delta_TEIF'])
    return dV_P(y,arg) - (y['V_PA']-y['V_S'])/(arg['R_AS']*arg['C_PA']) + pace #+EIF

# def dV_BA(y, arg):
#     return 1/arg['C_BA']*((y['Vi']-y['V_BA'])/arg['R_I']-IK(y,arg))+dV_P(y,arg)



#########################################################################

def deriv(t, y, arg, fixedV_S = fixedV_S):
    #creating arg:
    if arg is None:
        arg = getarg()
    if not cst.useH:    
        V_D, V_S, V_PA, V_P, n = y
    else:
        V_D, V_S, V_PA, V_P, n, h = y
    Vi = Vi_func(t, arg['time_In'], arg['spike_In'])
    dVi = dVi_func(t, arg['time_dIn'], arg['dspike_In'])
    
    vs_noise = V_S_noise_func(t, arg['vs_noise_time'],arg['vs_noise'])
    vsext = V_Sext_func(t, arg['vsext_time'],arg['vsext'])
    dvsext = dV_Sext_func(t, arg['dvsext_time'],arg['dvsext'])
    
    V_BA = Vi - arg['R_I'] * ((V_PA-V_S)/arg['R_AS'] + V_P/arg['R_L'])
    ybis = {'V_D':V_D, 
            'V_S':V_S,
            'V_PA':V_PA, 
            'V_P':V_P, 
            'n':n,
            'V_BA':V_BA, 
            'Vi':Vi,
            'dVi':dVi,
            'vs_noise':vs_noise,
            'vsext':vsext,
            'dvsext':dvsext}
    if cst.useH:
        ybis['h'] = h
        y_out = [f(ybis, arg) for f in [dV_D, dV_S, dV_PA, dV_P, dN, dH]]
    else:
        y_out = [f(ybis, arg) for f in [dV_D, dV_S, dV_PA, dV_P, dN]]

    # if fixedV_S:
    #     y_out[1] = dV_S_func(t)
    return y_out


#########################################################################
### Integrating
#########################################################################

def integrate_and_fire(y0, t, args = None, verbose = True, stopAtFirstSpike = False, detect = .5e-3):
    """detect is the place where to stop integration to look for threshold, if detect == 0, spikes
    will be just a bit before threshold, if detect is too big, one might miss local extremum above
    threshold"""
    from scipy import integrate as intgt
    if args is None:
        if verbose: print 'loading args'
        args = getarg()
    arg = copy(args)
    step = max(100, t.size/1000.)
    t_spikes = []
    index_array = np.arange(step)
    y = copy(y0)
    n = 0
    out = np.zeros((t.size, len(y0)))
    end = False
    while n < len(t):
        # set or reset PC
        out[n] = np.array(y)
        res = y0
        #create and initialize solver
        solver = intgt.ode(deriv)
        solver.set_initial_value(y, t[n])
        solver.set_f_params(arg)
        if args['gLEIF'] == 0:
            test = lambda R : R[VPAi]-R[VEi] <args['LIF_th']+detect
        else:
            test = lambda R: True
        while solver.successful() and test(res):
            n += 1
            if n >= len(t):
                # reached the end of time
                end = True
                break
            solver.integrate(t[n])
            out[n] = solver.y
            res = out[n]
        if end:
            break
        n_just = n
        if not test(res):
            # search real position of spike if LIF
            while out[n_just][VPAi]-out[n_just][VEi]>args['LIF_th']:
                n_just -= 1
        # add spike
        if n_just < len(t):
            out[n_just+1][[VDi, VSi,VPAi]] = 0
            tsp = t[n_just+1]
            t_spikes.append(tsp)
            if verbose: print 'Spike at %s ms!'%(tsp*1000)
        else:
            print 'check case, there is probably a spike at the last point'
        # reset cond
        if n_just < len(t)-1:
            n = n_just+2
        else:
            print 'check case, there is probably a spike just before the last point'
            n = min(n_just, len(t)-1)
        if arg['tau_rp'] is not None:
        
            while t[n] < tsp +arg['tau_rp']:
                n+=1
                out[n][[VDi, VSi,VPAi]] = arg['LIF_val']
        y = copy(y0)
        y[VDi] = args['LIF_val']
        y[VSi] = args['LIF_val']
        y[VPAi] = args['LIF_val']
        if stopAtFirstSpike:
            t = t[:n+1]
            out = out[:n+1]
            out[n] = y
            break
    
    out_dict = {}
    out_dict['sp_times'] = np.array(t_spikes)
    out_dict['time'] = t
    out_dict['v_p'] = flatenList([o[VEi] for o in out])
    out_dict['v_e'] = out_dict['v_p'] * args['R_E']/args['R_L']
    out_dict['v_pa'] = flatenList([o[VPAi] for o in out])
    out_dict['n'] = flatenList([o[Ni] for o in out])
    out_dict['vd'] = flatenList([o[VDi] for o in out])
    out_dict['vs'] = flatenList([o[VSi] for o in out])
    out_dict['vi'] = np.array([Vi_func(i, args['time_In'], args['spike_In']) for i in out_dict['time']])
    out_dict['v_ba'] = args['R_I'] * (out_dict['vi']/args['R_I']                   \
                                  - (out_dict['v_pa'] -out_dict['vs'])/args['R_AS']\
                                  - out_dict['v_p']/args['R_L'])
    if args['vsext'] is not None:
        out_dict['vs_ext'] = np.array([V_Sext_func(ti, args['vsext_time'],args['vsext']) for ti in out_dict['time']])
    if args['dvsext'] is not None:
        out_dict['dvs_ext'] = np.array([dV_Sext_func(ti, args['dvsext_time'],args['dvsext']) for ti in out_dict['time']])
    if cst.useH:
        out_dict['h'] = flatenList([o[Hi] for o in out])
    if verbose: print 'integrated!!'
    return out_dict

def big_dict(out, args):
    """
    in "out" you have: 'sp_times', 'time', 'v_p', 'v_e', 'v_pa', 'n', 'vd',
                       'vs','vi', 'v_ba'
    
    in 'args' you have: 'dvsext_time',  'LIF_th',  'spike_In', 'R_AS', 'R_L', 'R_I',
                        'R_J', 'dspike_In', 'gK', 'LIF_val', 'EK', 'vs_noise_time',
                        'time_In', 'cK1', 'cK0', 'dvsext', 'vs_noise', 'vsext',
                        'C_BA', 'vsext_time', 'time_dIn', 'C_PA', 'R_P', 'C_D',
                        'pace', 'C_S', 'R_E'
    """
    #currents:
    
    VSi = out['vs'] - out['vs_ext']
    dV_S = np.diff(VSi)/np.diff(out['time'][:2])
    I_C_S = dV_S*args['C_S']
    
    VPAi = out['v_pa']-out['v_p']
    dV_PA = np.diff(VPAi)/np.diff(out['time'][:2])
    I_C_PA = dV_PA*args['C_PA']
    
    VP = out['v_ba'] - out['v_p']
    dV_BA = np.diff(VP)/np.diff(out['time'][:2])
    I_C_BA = dV_BA*args['C_BA']

    dV_D = np.diff(out['vd'])/np.diff(out['time'][:2])
    I_C_D = dV_D*args['C_D']

    I_R_J = (out['vs']-out['vd'])/args['R_J']
    I_R_AS = (out['v_pa']-out['vs'])/args['R_AS']
    I_R_P = (out['v_p']-out['v_e'])/args['R_P']
    I_K = args['gK']*out['n']*(VP-args['EK'])
    return {'I_R_AS':I_R_AS, 'I_R_J':I_R_J, 'I_R_P': I_R_P, 'I_C_D':I_C_D, 'I_C_BA': I_C_BA,'I_C_PA':I_C_PA, 'I_C_S':I_C_S, 'I_K':I_K}
    
    
#########################################################################
### EIF functions
#########################################################################

def phi(V, gL, V_T, delta_T):
    """from Fourcaud-Trocme & Brunel with the same notations
    
    V_T is threshold voltage
    gL the leak driving the """
    return gL * delta_T*np.exp((V-V_T)/delta_T)

    
