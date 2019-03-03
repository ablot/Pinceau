# -*- coding: utf-8 -*-
#import sys
import struct
#import datetime
#import numpy as np
#import matplotlib
#import types
#import time as tme



##############################################################################
class DataFile():
##############################################################################


    def __init__(self, pathAndName):
        
        self.magicNumberDict = {"0x41424620": "abf", "0x5645523d": "wcp"}
        self.fileName=pathAndName
        datafile = file(self.fileName, 'rb')
        datafile.seek(0)
        mn = struct.unpack_from("BBBB", datafile.read(4))
        #  Magic to magically extract magic number.
        self.magicNumberString = "0x" + reduce(lambda x, y: x+y, [hex(z)[2:4] for z in list(mn)])
        try:
            if self.magicNumberDict[self.magicNumberString] == "abf":
                import PclampFile
                self.datafile = PclampFile.PclampFile(pathAndName)
            elif self.magicNumberDict[self.magicNumberString] == "wcp":
                import WCPFile
                self.datafile = WCPFile.WCPFile(pathAndName)
        except KeyError:
            raise IOError('%s is not a valid datafile !'%pathAndName)
        datafile.close()
        self.numSweeps = self.datafile.numSweeps
        self.channelInfo = self.datafile.channelInfo
        self.samplingInterval = self.datafile.samplingInterval
        self.gains = self.datafile.gains
        self.policy = self.datafile.policy
    
    def set_policy(self, value):
        self.datafile.set_policy(value)
    
    def sweepInfo(self, num):
        """Return a dict with 'time_recorded' (s), 'dt' (s), 'numChans',
        'numPoints', 't0' (s), 'duration' (s), 'tend' (s), 'absolute_t0',
        'mult_factor', and channel info
        
        absolute_t0 is the time when the recording started
        time_recorded is the time recorded since the beginning of the file
        mult_factor is the multiplying factor, df, such as:
            int_stored_in_file * df = data_in_true_unit
        channel info is a list of ChannelType instances containing name, title,
        units, isinput, maxval (V), gain (mV/unit)"""
        out = self.datafile.sweepInfo(num)
        listkey = ['time_recorded', 'dt', 'numChans', 'numPoints', 't0', 
                   'duration', 'tend', 'absolute_t0']
        for key in listkey:
            out.setdefault(key, 'nd')
        return out
        
    def scale(self, index_sweep = None):
        return self.datafile.scale(index_sweep)
    
    def sweep(self, num, chans, *args, **kwargs):
        '''Return the data from one sweep. 
        Should accept dtype as third argument if you want to access to integer 
        data (in that case the time line is kept but probably corrupted if you
        don't use int64 or short sweeps)'''
        if num >= self.numSweeps:
            inp = raw_input('index biger than numSweeps, you really wanna try? (y/N)')
            while inp.lower() not in ['y', '','n']:
                inp = raw_input('y for yes, n for no')
            if not inp or inp.lower() == 'n':
                return
        return self.datafile.sweep(num, chans, *args, **kwargs)
    
#################################################################################
class ChannelType():
    """Common channel information: name, title, units, isinput, maxval (V), gain
    (mV/unit), factor (used to pass from int to true unit)"""
#################################################################################
#    def __init__(self, name, title, units, isinput, maxval, gain, factor):
    def __init__(self, name, title, units, isinput, maxval, factor):
        self.name = name
        self.title = title
        self.units = units
        self.isinput = isinput # True means input; False means output.
        self.maxval = maxval
        #self.gain = gain
        self.factor = factor
        

