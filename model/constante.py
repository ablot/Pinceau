# -*- coding: utf-8 -*-
import numpy as np
import os
from Pinceau.CONFIG import DATA


class const(object):
    def __init__(self):
        self.t0 = 0
        self.V_D0 = -70e-3
        self.V_S0 = -70e-3
        self.V_PA0 = -70e-3
        self.V_P0 = 0
        self.V_BA0 = -70e-3
        self.n0 = 0.053
        self.h0 = 1
        self.factor = 2
        self.V_Spike_0 = -70e-3
        self.t_peak = 50e-3
        self.time = np.linspace(35e-3, 55e-3, (55-35)*100)
        self.useH = False

        self.rayon_A = 0.4 #µm #diam ~ 0.8 according to Somogyi in rat
        self.rayon_AP = 0.5
        self.l_P = 7
        self.l_A = 10 #17.1 according to Somogyi in rat
        self.C_memb = 1e-2 #pF/µm²
        self.Resistivit_Interne = 150e4 #MOhm.µm

        self.PATH = os.path.join(DATA, 'spike_withexp.npy')


        """
        Conversion:
        C_memb:
        1 µF/cm² = 1e-8 µF/µm² = 1e-2 pF/µm²

        Resistivit_Interne:
        150 Ohm.cm = 150e4 Ohm.µm

        gK:
        11.5 nS = 11.5e-9 S = 11.5e-9 1/Ohm = 11.5e-3 1/MOhm
        """

        self.n_col = 5 #number of col per BC

        self.Surf_A = lambda : self.rayon_A*2*np.pi*self.l_A #µm²
        self.Surf_P = lambda : self.rayon_AP*2*np.pi*self.l_P #µm²

        self.R_I = self.Resistivit_Interne*self.l_P/(self.rayon_AP**2*np.pi) #Ohm
        self.R_E = 1/(4*np.pi*0.4*2.5e-6) #32e3 
        # with 0.4 S/m = sigma conductivity
        # 5e-6 m being the radius of the sphere
        self.R_P = 300e3


        
        self.R_AS =  self.Resistivit_Interne * self.l_A / (self.rayon_A**2*np.pi ) #Ohm
        self.R_J =  5 * 1e6 #Ohm

        self.C_BA = 1*self.Surf_P() * self.C_memb * 1e-12 * self.n_col#F
        # equal to 7e-13
        self.C_PA =  self.Surf_A() * self.C_memb * 1e-12 #F
        self.C_S =  10 * 1e-12 #F
        self.C_D =  750 * 1e-12 #F

        #note: 10 pA/µm² is quite high
        self.surf_cond_K = 15e-12/120e-3 *0.4# S/µm²
        self.gK = self.Surf_P() * self.surf_cond_K * self.n_col
        # equal to 8.7e-9
        # (11.5e-9 Siemens from whole-cell recording of panier)
        self.EK =  -105e-3
        self.cK0 = 4
        self.cK1 =  1/3**((35-20)/10.) # is currently the Q10 to apply to tau

        #compute surface from C_PAp (need to put everything in pF so *1e12)
        self.Surf_S = lambda : (self.C_S*1e12)/self.C_memb #µm²
        self.Surf_D = lambda : (self.C_D*1e12)/self.C_memb #µm²
        self.surf_cond = 0.05e-9 # S/µm²
        #if used by model_3, current in A, if used by model_5 rate of depolarisation in V/s
        # so it can be expressed in V to reach threshold (25e-3) / period
        self.pace =  15e-3*50
        self.gL_s = self.Surf_S() * self.surf_cond #used by model_4
        self.eL_s = -40e-3 #used by model_4
        self.gL_d = self.Surf_D() * self.surf_cond #used by model_4
        self.eL_d = -40e-3 #used by model_4
        """
        surf_cond = 0.1 => 150 Hz
        surf_cond = 0.01 => 10 Hz
        """

        temp_noise = np.load(os.path.join(DATA, 'PC_VC_sw0.npy'))
        self.vs_noise = (temp_noise - np.median(temp_noise))
        self.vs_noise = None

        temp_time =  np.load(os.path.join(DATA, 'PC_VC_time.npy'))
        self.vs_noise_time = temp_time - temp_time[0]
        self.vs_noise_time = 0 #None
        
        self.vsext = np.load(os.path.join(DATA, 'fake_Vsext.npy')) * 1e-6
        self.vsext_time = np.load(os.path.join(DATA, 'fake_Vsext_time.npy')) * 1e-3 + self.t_peak
        self.dvsext = np.diff(self.vsext)/np.diff(self.vsext_time[:2])
        self.dvsext_time = self.vsext_time[:-1]+np.diff(self.vsext_time[:2])
        
        self.vsext = np.zeros_like(self.vsext)
        self.dvsext = np.zeros_like(self.dvsext)
        
        self.LIF_val = -70e-3
        self.LIF_th = -55e-3
        self.gLEIF = 0
        self.V_TEIF =  15e-3 - 70e-3
        self.delta_TEIF = 1.5e-3
        self.tau_rp = 1.7e-3

        #initial value:
        self.y0 = [self.V_D0, self.V_S0, self.V_PA0, self.V_P0, self.n0]
        if self.useH:
            self.y0.append(h0)

        # y0 = [V_D0, V_S0, V_PA0, V_P0, n0, h0]
    def _getx(self):
        return self.R_P + self.R_E
    R_L = property(_getx)

cst = const()
