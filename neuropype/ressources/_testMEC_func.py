import numpy as np
from neuropype.ressources.recurtime import recurtime

def cleanInt(t0, t1, bef, aft, killIfNot1 = False):
    if killIfNot1 and not t1.size:
        return np.zeros(t0.size, dtype = 'bool')
    if not t0.size:
        return np.zeros(t0.size, dtype = 'bool')
    tbef, taft = recurtime(t0,t1)
    OK = np.ones(t0.size)
    if bef is not None:
        OK = np.logical_and(OK, tbef > bef)
    if aft is not None:
        OK = np.logical_and(OK, taft > aft)
    return OK
