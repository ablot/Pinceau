# -*- coding: utf-8 -*-
import sys
import struct
import datetime
import numpy as np
import matplotlib
import types
import time as tme

# TODO: datafile is importing PclampFile, not sure it's a good idea to import 
# something from datafile here => we could move it somewhere else; however, it
# seems to work nonetheless.
from neuropype.datafile import ChannelType 

#################################################################################
class PclampFile():
    """File handle: holds path to file and vitalstatistics, 
    including date, time, channel geometry..."""
    ##########################################################################  
    
    def __init__(self, pathAndName):
        self.HEADERSIZE = 6144
        self.fileName=pathAndName
        datafile = file(self.fileName, 'rb')
        # Load header as unformatted string.
        self.header = datafile.read(self.HEADERSIZE)
        datafile.close()
        self.policy = None
        # Format version. Note that "<" indicates little endian byte order.
        self._version = struct.unpack_from("<f", self.header, 4)[0]
        lHeaderSize = struct.unpack_from("<I", self.header, 2034)[0]
        
        # Reported date and time for beginning of acquisition.
        td = struct.unpack_from("<I", self.header, 20)[0]
        # The date seems correct without this adjustment described in the format definition.
        #if td >= 80000:
            #td += 19000000
        #else:
            #td += 20000000
        y = np.floor(td/10000)
        td -= y*10000
        mon = np.floor(td/100)
        d = np.floor(td - mon*100)
        
        tt = struct.unpack_from("<I", self.header, 24)[0]
        h = np.floor(tt/3600)
        tt -= h*3600
        mins = np.floor(tt/60)
        s = np.floor(tt - mins*60)
        # Check that rounding by int() of floats that are deprecated in the datetime constructor is OK.
        for i in [y, mon, d, h, mins, s]:
            if (i - int(i)) > 0.1:
                print "Rounding of date components caused an error."
        self.datetime = datetime.datetime(int(y), int(mon), int(d), int(h), int(mins), int(s))
        
        #****** COMMON SECTION ******
        
        # Number of input channels.
        self.numInputChannels = struct.unpack_from("<H", self.header, 120)[0]
        
        # Which channels were acquired? -1 padding = not acquired.
        samplingSeq = struct.unpack_from("<16h", self.header, 410)[0:16]
        
        # WARNING: I do not check for "out of order" acquisition. E.g. where channel 1 comes before channel 0.
        # (Skipping channel numbers is OK.)
        self.channelsAcquired = []
        for i in range(16):
        # Unacquired channels are indicated by -1.
            if samplingSeq[i] > -0.5:
                self.channelsAcquired.append(i)
                
        sADCChannelName = struct.unpack_from("160s", self.header, 442)[0:16]
        # Need to get the first element of tuple returned by struct.unpack_from(), 
        # otherwise brackets and commas from the tuple end up in the string!
        self.inputChanNames = [str(sADCChannelName[0][10*i:10*(i+1)]).strip() for i in range(16)]
        sADCUnits = struct.unpack_from("128s", self.header, 602)[0:16]
        self.inputChanUnits = [str(sADCUnits[0][8*i:8*(i+1)]).strip() for i in range(16)]
        
        # Number of sweeps.
        self.numSweeps = struct.unpack_from("<I", self.header, 16)[0]
        
        # Number of points per sweep.
        self._numPointsPerSweep = struct.unpack_from("<I", self.header, 138)[0]/self.numInputChannels
        
        # Sample interval.
        self._sampleInterval = struct.unpack_from("<f", self.header, 122)[0]*1E-6*self.numInputChannels
        
        # Episode start-to-start time.
        self.sweepInterval = struct.unpack_from("<f", self.header, 178)[0]
        
        # Pretrigger points (probably useless).
        self.preTriggerPoints = struct.unpack_from("<I", self.header, 142)[0]
                
        # Data begin.
        self._dataSectionPtr = struct.unpack_from("<I", self.header, 40)[0]*512
        
        # Input gains.
        self.ADCRange = struct.unpack_from("<f", self.header, 244)[0]
        lADCResolution = struct.unpack_from("<I", self.header, 252)[0]
        self.gains = list(struct.unpack_from("<16f", self.header, 922)[0:16])
        self._ADCFactor = self.ADCRange/lADCResolution
        
        # Output stuff
        # DACRange is in Volts. PClamp already gives much DAC info in user units, but this one is useful for calculating full-scale automatically.
        self.DACRange = list(struct.unpack_from("<4f", self.header, 248))[0:4]
        # Workaround if only the first value makes sense (Clampex bug)
        for i in range(4):
            if self.DACRange[i] < 0.5 or self.DACRange[i] > 20:
                self.DACRange[i] = self.DACRange[0]
        self.fDACResolution = list(struct.unpack_from("<4I", self.header, 256))[0:4]
        # The end of the array is often not initialised. This prevents subsequent division by zero.
        for i in range(4):
            if self.fDACResolution[i] > 1e6 or self.fDACResolution[i] < 100:
                self.fDACResolution[i] = 4096 # Whatever: 12 bits.
        # DACFactor is in user units/V@DAC.
        self.DACFactor = list(struct.unpack_from("<4f", self.header, 1378))[0:4]
        # Prepare for user modification of DAC settings.
        #self.DACFactorCorrection = [1,1,1,1]
        
        sDACChannelName = str(struct.unpack_from("s40", self.header, 1306)[0])
        self.outputChanNames = [str(sDACChannelName[0][10*i:10*(i+1)]).strip() for i in range(4)]
        sDACChannelUnits = str(struct.unpack_from("s32", self.header, 1346)[0])
        self.outputChanUnits = [str(sDACChannelUnits[0][8*i:8*(i+1)]).strip() for i in range(4)]
        
        # Digital outputs.
        self._digitalEnabled = bool(struct.unpack_from("<H", self.header, 1436)[0])
        self.digitalHolding = struct.unpack_from("<H", self.header, 1584)[0]
        self.digitalValues = list(struct.unpack_from("<10H", self.header, 1588))[0:10]

        # NB. There are plenty of things not implemented, notably the two versions of nInterEpisodeLevel. 
        self.fDACHoldingLevel = list(struct.unpack_from("<4f", self.header, 1394))[0:4]
            
        # I would have expected the deprecation of these fields to have coincided with the move
        # to the large header. Unfortunately, this doesn't seem to be the case. For this reason,
        # they are processed outside the header-size-dependent sections below.
        #self.nExperimentType = struct.unpack_from("<H", self.header, 260)[0]
        self._nTelegraphEnable = struct.unpack_from("<H", self.header, 262)[0]
        self._nAutosampleADCNum = struct.unpack_from("<H", self.header, 264)[0]
        self._fAutosampleAdditGain = struct.unpack_from("<f", self.header, 268)[0]
            
        if self._nTelegraphEnable:
            print "Untested telegraphed gain adjustment made - you'd better check carefully!"
            self.gains[self._nAutosampleADCNum] *= self._fAutosampleAdditGain
        
        # lHeaderSize is probably more reliable than my guessing a version number regarding extended header 
        # information. Actually, the changelog suggests version 1.6 and up.
        if lHeaderSize < 2049: # Old style small header.
            print 'big header'
            
            activeDACChannel = struct.unpack_from("<H", self.header, 1440)[0]
            self.channelsOutput = [activeDACChannel]
            # Waveform epochs.
            # Even single numbers are turned into lists or lists of lists 
            # to make them compatible with real lists from the extended header.
            # 0 = disabled; 1 = normal epochs etc; 2 = DAC File.
            self._waveformSource = [0, 0]
            self._waveformSource[activeDACChannel] = struct.unpack_from("<H", self.header, 1438)[0]
            if self._waveformSource[activeDACChannel] == 2:
                # A DAC File has been used.
                # Changelog suggests that version 1.5 and up uses the new DACFile data.
                # This may not correspond exactly to the longer headers (apparently version 1.6). 
                self.lDACFilePtr = [0, 0]
                self.lDACFilePtr[activeDACChannel] = struct.unpack_from("<H", self.header, 60)[0]*512       
                self.lDACFileNumEpisodes = [0, 0]
                self.lDACFileNumEpisodes[activeDACChannel] = struct.unpack_from("<H", self.header, 64)[0]       
                self.fDACFileScale = [0, 0]
                self.fDACFileScale[activeDACChannel] = struct.unpack_from("<f", self.header, 1620)[0]  
                self.sDACFilePath = ["", ""]
                self.sDACFilePath[activeDACChannel] = struct.unpack_from("s84", self.header, 1634)[0:84]  
                    
            else:
                # 0 = disabled; 1 = step, 2 = ramp.
                self.epochType = [[0 for i in range(10)] for i in range(2)]
                # or import copy and use the .deepcopy method (otherwise the internal lists are not copied)
                self.epochType[activeDACChannel] = list(struct.unpack_from("<10H", self.header, 1444))[0:10]
                # Epoch values are in user units.
                self.epochInitLevel = [[0 for i in range(10)] for i in range(2)]
                self.epochInitLevel[activeDACChannel] = list(struct.unpack_from("<10f", self.header, 1464))[0:10]
                self.epochLevelInc = [[0 for i in range(10)] for i in range(2)]
                self.epochLevelInc[activeDACChannel] = list(struct.unpack_from("<10f", self.header, 1504))[0:10]
                # Epoch timings are in "sequence counts".
                self.epochInitDuration = [[0 for i in range(10)] for i in range(2)]
                self.epochInitDuration[activeDACChannel] = list(struct.unpack_from("<10H", self.header, 1544))[0:10]
                self.epochDurationInc = [[0 for i in range(10)] for i in range(2)]
                self.epochDurationInc[activeDACChannel] = list(struct.unpack_from("<10H", self.header, 1564))[0:10]
            
                # User list.
                # ** Need to make these lists of lists allowing [chan] indexing.**
                self.userListEnable = bool(struct.unpack_from("<H", self.header, 1966)[0])
                if self.userListEnable:
                    self.paramToVary = [struct.unpack_from("<H", self.header, 1762)[0]]
                    if self.paramToVary[0] not in range(21,31):
                        # Only epoch init values are implemented here.
                        print "In a user list you have varied a parameter that I have not implemented."
                        exit()
                    paramList = str(struct.unpack_from("s80", self.header, 1764)[0])
                    paramList = paramList.split(",")
                    self.paramList = [[float(s.strip()) for s in paramList]]
            
        else: # lHeaderSize >= 2049 => Extended header.
            
            # fTelegraphAdditGain is garbage in my test file - possibly because it's not enabled...
            # Need to understand whether fTelegraphAdditGain is an additional fInstrumentScaleFactor and 
            # if we should divide or multiply by it.
            # In Guy's files all of these are zeros.
            nTelegraphEnable = list(struct.unpack_from("<16H", self.header, 4512)[0:16])
            fTelegraphAdditGain = list(struct.unpack_from("<16f", self.header, 4576)[0:16])
            # Don't forget fADCProgrammableGain (p4 abfheader.pdf)? Don't have signal conditioner...
            # This is unused and should anyway move into the common part.
            #fADCProgrammableGain = list(struct.unpack_from("<16f", self.header, 730)[0:16])
            for i in range(16):
                # Disabled = 0.
                if nTelegraphEnable[i]:
                    print "Untested telegraphed gain adjustment made - you'd better check carefully!"
                    self.gains[i] *= fTelegraphAdditGain[i]
            
            
            # Small function to avoid recoding untangling of interleaved parameter lists.
            def untwine(numLists, lenList, data):
                l = []
                for i in range(numLists):
                    l.append(data[i*lenList:(i+1)*lenList])
                return l
            
            enabledDACs = list(struct.unpack_from("<2H", self.header, 2296)[0:2])
            self.channelsOutput = []
            if enabledDACs[0] == 1:
                self.channelsOutput += [0]
            if enabledDACs[1] == 1:
                self.channelsOutput += [1]
        
            self._waveformSource = list(struct.unpack_from("<2H", self.header, 2300)[0:2])
            # Check whether you can pick and mix DAC File and waveform; though it seems unlikely that Axon could have 
            # programmed something that complicated.
            if self._waveformSource[0] == 2 or self._waveformSource[1] == 2:
                # A DAC File has been used.
                # Changelog suggests that version 1.5 and up uses the new DACFile data.
                # This may not correspond exactly to the longer headers (apparently version 1.6). 
                self.lDACFilePtr = list(struct.unpack_from("<2H", self.header, 60)[0:2])
                self.lDACFileNumEpisodes = list(struct.unpack_from("<2H", self.header, 64)[0:2])
                self.fDACFileScale = list(struct.unpack_from("<2f", self.header, 1620)[0:2])
                self.sDACFilePath = list([struct.unpack_from("s128", self.header, 2736)[0:128],struct.unpack_from("s128", self.header, 2864)[0:128]]) 
                
            else:
                # 0 = disabled; 1 = step, 2 = ramp.                                    
                epochType = list(struct.unpack_from("<20H", self.header, 2308))[0:20]
                self.epochType = untwine(2, 10, epochType)
                # Epoch values are in user units.
                epochInitLevel = list(struct.unpack_from("<20f", self.header, 2348))[0:20]
                self.epochInitLevel = untwine(2, 10, epochInitLevel)
                epochLevelInc = list(struct.unpack_from("<20f", self.header, 2428))[0:20]
                self.epochLevelInc = untwine(2, 10, epochLevelInc)
                # Epoch timings are in "sequence counts".
                epochInitDuration = list(struct.unpack_from("<20I", self.header, 2508))[0:20]
                self.epochInitDuration = untwine(2, 10, epochInitDuration)
                epochDurationInc = list(struct.unpack_from("<20I", self.header, 2588))[0:20]
                self.epochDurationInc = untwine(2, 10, epochDurationInc)
                
                # User list.
                # TODO: I don't seem to make use of this yet.
                userListEnable = list(struct.unpack_from("<4H", self.header, 3360)[0:4])
                self.userListEnable = [bool(userListEnable[i]) for i in range(4)]
                if True in self.userListEnable:
                    print "User lists are not yet implemented."
                    self.paramToVary = list(struct.unpack_from("<4H", self.header, 3368)[0:4])
                    for i in range(4):
                        if self.paramToVary[i] not in range(21,31):
                            # Only epoch init values are implemented here.
                            # TODO: Need to support all possible parameters (cf custom PPR timings).
                            print "In a user list you have varied a parameter that I have not implemented."
                    paramList = str(struct.unpack_from("1024s", self.header, 3376)[0])
                    self.paramList = []
                    for i in range(4):
                        pL = paramList[i*256:(i+1)*256] 
                        pL = pL.split(",")
                        self.paramList.append([float(s.strip()) for s in pL])
                    self.repeatUserList = list(struct.unpack_from("<4H", self.header, 4400))[0:4]
            
        self.setGains()
        # The reconstituted outputs are already in user units, so there is no need for further conversion, except, it seems, in the case of a DAC file.
        self.outputFactor = [1, 1, 1, 1]
        for i in self.channelsOutput:
            if self._waveformSource[i] == 2:
                self.outputFactor[i] = self.fDACFileScale[i]*self.DACRange[i]*self.DACFactor[i]/self.fDACResolution[i] 

        self.channelInfo = []
        # Removed gain parameter from the channelInfo objects as it seemed redundant with factor; adjusting the gain can be implemented later.
        for i in range(len(self.channelsOutput)):
            j = self.channelsOutput[i]
            self.channelInfo.append(ChannelType(name='Cmd_'+str(j), title=self.outputChanNames[j], units=self.outputChanUnits[j], isinput=False, maxval=self.DACFactor[j]*self.DACRange[j], factor = self.outputFactor[j]))
        for i in range(len(self.channelsAcquired)):
            j = self.channelsAcquired[i]
            self.channelInfo.append(ChannelType(name='Ch_'+str(j), title=self.inputChanNames[j], units=self.inputChanUnits[j], isinput=True, maxval=self.ADCRange/self.gains[j], factor=self.scale[j]))
        
        # We don't load the data at this point.
        self._inMemory = False

    def samplingInterval(self, *args, **kwargs):
        return 'dunno'
    def set_policy(self, value):
        pass
    
    def setGains(self):
        # Telegraph gains garbage in my old files.
        # Separate out this function in case we wish to set/correct them manually.
        self.scale = [self._ADCFactor/g for g in self.gains]
        
    
    def sweepInfo(self, num):
        #TODO: redo it properly this one is just a fake
        out = {'channelInfo': self.channelInfo, 'numChan' : len(self.channelInfo), 'sampling': self._sampleInterval,
                't0': 0}
        return out
    
    def sweep(self, num, chans, dtype = None):
        
        output = np.zeros((len(chans)+1,self._numPointsPerSweep))
        output[0,:] = self.sweept() 
        for i in range(len(chans)):
            j = chans[i]
            #output[i+1,:] = self.inputSweep(num, i)
            if not self.channelInfo[j].isinput:
                output[i+1,:] = self.outputSweep(num, j)
            else:
                output[i+1,:] = self.inputSweep(num, j-len(self.channelsOutput))
        return output
            
    
    def inputSweep(self, num, chan):
        # TODO: we are loading all of the data each time a sweep is requested. This has to be 
        # inefficient. We should therefore use the cache here.
        # num and chan should both be ints.
        j = self.channelsAcquired[chan]
        # Need some try/except blocks here...
        numShorts = self.numSweeps*self.numInputChannels*self._numPointsPerSweep
        datafile = file(self.fileName, 'rb')
        # Seek to beginning of data in hope that np.fromfile reads on from there...
        datafile.seek(self._dataSectionPtr)
        # Empty sep indicates binary.
        self.sweeps = np.fromfile(datafile, dtype=np.int16, count=numShorts, sep="")
        # If the protocol was stopped prematurely, self.sweeps will be shorter than reported.
        # To adapt to this case, we set the self.numSweeps to the real number of sweeps, including
        # any truncated sweep. It seems that truncated sweeps can also be saved. In that case
        # we pad self.sweeps with zeroes to reach a whole number of sweeps.
        # TODO: this after-the-fact adjustment of the number of sweeps may cause problems.
        # It may be necessary to perform the check of data length on loading the file.
        numWholeSweeps = len(self.sweeps)/(self._numPointsPerSweep*self.numInputChannels)
        if self._numPointsPerSweep*self.numInputChannels*numWholeSweeps != len(self.sweeps):
            self.numSweeps = numWholeSweeps + 1            
            self.sweeps = np.append(self.sweeps, np.zeros(self._numPointsPerSweep*self.numInputChannels*self.numSweeps-len(self.sweeps)))
        else:
            self.numSweeps = numWholeSweeps     
        self.sweeps = np.reshape(self.sweeps, (self.numSweeps, self._numPointsPerSweep, self.numInputChannels), order='C')
        datafile.close()
        trace = self.sweeps[num, :, j].astype(float)*self.scale[j]
        datafile.close()
        return trace
    
    def outputSweep(self, num, chan):
        # num and chan should both be ints.
        j = self.channelsOutput[chan]
        trace = np.ndarray(shape=self._numPointsPerSweep)
        slop = self._numPointsPerSweep/64 # This amount at beginning and end should be holding.
        trace[:] = self.fDACHoldingLevel[chan] #0
        if self._waveformSource[j] == 1: # Normal waveform
            index = slop
            for i in range(10):
                if self.epochType[j][i]: # 0 means disabled.
                    eID = self.epochInitDuration[j][i]
                    eDI = self.epochDurationInc[j][i]
                    eD = eID + eDI*num
                    eIL = self.epochInitLevel[j][i]
                    eLI = self.epochLevelInc[j][i]
                    if self.epochType[j][i] == 1: # Step.
                        trace[index:(index + eD)] = eIL + eLI*num
                        index = index + eID + eDI*num
                    else: # Ramp.
                        if i == 0:
                            start = 0
                        else:
                            start = self.epochInitLevel[j][i-1] + self.epochLevelInc[j][i-1]*num
                        if i == 9:
                            stop = 0
                        else:
                            #print chan, i
                            stop = self.epochInitLevel[j][i+1] + self.epochLevelInc[j][i+1]*num
                        #print start, stop
                        start = float(start)
                        stop = float(stop)
                        trace[index:index+eD] = [start + (stop-start)*i/eD for i in range(eD)]
        elif self._waveformSource[j] == 2: # DAC File
            # Need some try/except blocks here...
            numShorts = self._numPointsPerSweep
            datafile = file(self.fileName, 'rb')
            # Seek to beginning of DAC File section.
            datafile.seek(self.lDACFilePtr[j]*512+2*numShorts*num)
            # Empty sep indicates binary.
            self.sweeps = np.fromfile(datafile, dtype=np.int16, count=numShorts, sep="")
            trace = self.sweeps.astype(float)*self.outputFactor[j]
        
            datafile.close()
        return trace
                        
    def sweept(self):
        sweept = np.arange(self._numPointsPerSweep)*self._sampleInterval
        return sweept
#################################################################################
