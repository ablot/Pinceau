import numpy as np


def m_HH(m_inf, m_0, tau_m, dt):
    """Return m value from steady state properties"""
    return m_inf - (m_inf - m_0) * np.exp(-dt / tau_m)


def m_inf_func(y_0, Vm, V_demi, k):
    """Return m_inf from Boltzman equation parameters,
    y0 is the voltage insensitive fraction of gates"""
    return y_0 + (1 - y_0) / (1 + np.exp(-(Vm - V_demi) / k))


def I(G, Gmax, V, E):
    """return current from  parameters"""
    return G * Gmax * (V - E)


Kfast = {'G': lambda m, h: m ** 3 * h,
         'Gmax': 40,  # in pS/cm**2
         'm': {'V_demi': -24,  # in mV
               'k': 15.4,  # in mV
               'y0': 0},
         'h': {'V_demi': -5.8,  # in mV
               'k': -11.2,  # in mV
               'y0': 0.31},
         'E': -88
         }

Kmid = {'G': lambda m: m ** 4,
        'Gmax': 20,  # in pS/cm**2
        'm': {'V_demi': -24,  # in mV
              'k': 20.4,  # in mV
              'y0': 0},
        'E': -88
        }

Kslow = {'G': lambda m: m ** 4,
         'Gmax': 40,  # in pS/cm**2
         'm': {'V_demi': -16.5,  # in mV
               'k': 18.4,  # in mV
               'y0': 0},
         'E': -88
         }

Ih = {'G': lambda m: m,
      'Gmax': 1,  # in pS/cm**2
      'm': {'V_demi': -90.1,  # in mV
            'k': -9.9,  # in mV
            'y0': 0},
      'E': -30
      }

Leak = {'G': lambda: 1,
        'Gmax': 0.5,
        'E': -60
        }

#########################################################################
### IK functions from Purkinje
#########################################################################
"""From neuron model 'Cerebellar Purkinje Cell: resurgent Na current and
high frequency firing (Khaliq et al 2003)' found at:
http://senselab.med.yale.edu/modeldb/ShowModel.asp?model=48332&file=\purkinje\kpkj.mod
"""


def Kfast_mtau_func(V):  # v(mV), (ms)
    mty0 = .00012851
    mtvh1 = 100.7
    mtk1 = 12.9
    mtvh2 = -56.0
    mtk2 = -23.1
    if V < -35:
        return (3.4225e-5 + .00498 * np.exp(-V / -28.29)) * 3
    else:
        return mty0 + 1 / (np.exp((V + mtvh1) / mtk1) + np.exp((V + mtvh2) / mtk2))


def Kfast_htau_func(V):  # v(mV), (ms)
    if V > 0:
        return .0012 + .0023 * np.exp(-.141 * V)
    else:
        return 1.2202e-5 + .012 * np.exp(-((V + 56.3) / 49.6) ** 2)


def Kmid_mtau_func(V):
    if (V < -20):
        mtau_func = .000688 + 1 / (np.exp((V + 64.2) / 6.5) + np.exp((V - 141.5) / -34.8))
    else:
        mtau_func = .00016 + .0008 * np.exp(-.0267 * V)
    return mtau_func


def Kslow_mtau_func(V):
    return .000796 + 1 / (np.exp((V + 73.2) / 11.7) + np.exp((V - 306.7) / -74.2))
