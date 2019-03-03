# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_displaySweep
import setscaledialog, setRangeDlg
from numpy import random
import neuropype.ressources.progressbar as pgb

class displaySweep(QWidget, ui_displaySweep.Ui_displaySweep):
    
    def __init__(self,parent=None):
        super(displaySweep, self).__init__(parent)
        self.setupUi(self)
        self.verticalLayout_7.setStretchFactor(self.chanVBoxLayout, 10)
        self.horizontalLayout_2.setStretchFactor(self.displayVLayout, 10)
        #PyQt4 doesn't support the stretch method
        self._node = None
        self._group = None
        self.lastSweep = None
        self.sweepNum=0
        self.MPLNav.initToolbar(self.MPLFig.fig.canvas)
        
        self.time = {'ms': 1000,
                     'index': 'ind',
                     's': 1,
                     'min': 1/60.,
                     'micros': 1000*1000,
                     'h': 1/60./60.}
        self.currentunit = 'index'
        listitems = sorted([(j, i) for i, j in self.time.items()])
        
        self.xUnitComboBox.addItems(QStringList([i[1] for i in listitems]))
        self.xUnitComboBox.setCurrentIndex(self.xUnitComboBox.findText('s'))
        #multiplot argument:
        self.range = None
        self.listSweeps = None
        
        
    def _factor(self):
        if self.currentunit == 'index':
            return 1/self.lastSweep.dt
        else:
            return self.time[self.currentunit]
                
            
    
    def setNode(self,node, grName):
        self._node = node
        self._group = node._outputGroups[grName]
        for attrName, value in self._group.items():
            setattr(self, attrName, getattr(node, value))
        self.sweepNum = 0
        self.NumSpinBox.setValue(0)
        self.manscale=[None for i in self.chanNames()]
        
        self.NumSpinBox.setMaximum(self.numSweeps()-1)
        self.loadNewSweep()
        self.updatescrollArea()
        self.displaySweep()
        time = self.lastSweep._data[0][:]
        self.xmaxDoubleSpinBox.setValue(time[-1])
        self.xminDoubleSpinBox.setValue(time[0])
        self.range = None
        self.numSweepSpinBox.setRange(1,self.numSweeps())
    
    #def setchans(self,chans):
        #if all([(i>=0) & (i<len(channelInfo)) for i in chans]):
            #self.__chans__= chans
    
    def updateFig(self,value=None):
        if self.sender()!=self.NumSpinBox:
            self.NumSpinBox.setValue(self.sweepNum)
        
        if value is not None and value != self.sweepNum:
                self.sweepNum = value
                self.loadNewSweep()
                self.displaySweep()
        else:
            self.actualiseDisplay()
            
            
    def updatescrollArea(self):
        self.cleanscrollArea()
        self.listScrollWidget=[]
        self.listScrollButtonGroup=[]
        self.listScrollLayout=[]
        for index, chanName in enumerate(self.lastSweep.chanNames()):
            self.doLine(index, getattr(self.lastSweep, chanName))
            self.chanVBoxLayout.addLayout(self.listScrollLayout[index],index)
        
    def cleanscrollArea(self):
        #removes everything in chanVBowLayout
        if hasattr(self,'listScrollLayout'):
        #just to avoid the deletion before the initialisation
            for i in range(len(self.listScrollLayout)):
                for widget in self.listScrollWidget[i]:
                    widget.deleteLater()
                self.listScrollLayout[i].deleteLater()
                #delete the Layout doesn't delete the child widgets
    
    def doLine(self,index,channelType):
        '''add a list to listScrollWidget with [Label, ShowCheckBox, 
        ManCheckBox, AutoCheckBox, FullCheckBox]'''
        buttonName=str(index)+"_"+channelType.title
        self.listScrollWidget.append([])
        self.listScrollLayout.append(QHBoxLayout())
        self.listScrollWidget[-1].append(QLabel())
        self.listScrollWidget[-1][-1].setText("Chan\n"+buttonName+":")
        self.listScrollWidget[-1][-1].setObjectName(buttonName+"Label")
        self.listScrollWidget[-1][-1].setMaximumWidth(50)
        self.listScrollWidget[-1][-1].setMinimumWidth(50)
        self.listScrollLayout[-1].addWidget(self.listScrollWidget[-1][-1])
        
        self.listScrollWidget[-1].append(QCheckBox())
        self.listScrollWidget[-1][-1].setObjectName(buttonName+ "ShowCheckBox")
        self.listScrollWidget[-1][-1].setChecked(True)
        self.connect(self.listScrollWidget[-1][-1], SIGNAL('clicked()'), 
                     self.showChan)
        self.listScrollLayout[-1].addWidget(self.listScrollWidget[-1][-1])
        
        self.listScrollButtonGroup.append(QButtonGroup())
        self.listScrollButtonGroup[-1].setExclusive(True)
        self.listScrollWidget[-1].append(QCheckBox())
        self.listScrollWidget[-1][-1].setObjectName(buttonName+"ManCheckBox")
        self.listScrollWidget[-1][-1].setChecked(False)
        self.listScrollButtonGroup[-1].addButton(self.listScrollWidget[-1][-1])
        self.connect(self.listScrollWidget[-1][-1], SIGNAL('clicked()'), 
                     self.manScale)
        self.listScrollLayout[-1].addWidget(self.listScrollWidget[-1][-1])
        self.listScrollWidget[-1].append(QCheckBox())
        self.listScrollWidget[-1][-1].setObjectName(buttonName+"AutoCheckBox")
        self.listScrollWidget[-1][-1].setChecked(True)
        self.connect(self.listScrollWidget[-1][-1], SIGNAL('clicked()'), 
                     self.updateFig)
        self.listScrollButtonGroup[-1].addButton(self.listScrollWidget[-1][-1])
        self.listScrollLayout[-1].addWidget(self.listScrollWidget[-1][-1])
        self.listScrollWidget[-1].append(QCheckBox())
        self.listScrollWidget[-1][-1].setObjectName(buttonName+"FullCheckBox")
        self.listScrollWidget[-1][-1].setChecked(False)
        self.connect(self.listScrollWidget[-1][-1], SIGNAL('clicked()'), 
                     self.updateFig)
        self.listScrollButtonGroup[-1].addButton(self.listScrollWidget[-1][-1])
        self.listScrollLayout[-1].addWidget(self.listScrollWidget[-1][-1])
    
    def loadNewSweep(self):
        index = self.sweepNum
        
        self.lastSweep = self.sweep(index)
        time = self.lastSweep._data[0][:]
        fac = self._factor()
        self.xminDoubleSpinBox.setMaximum(time[-1]*fac)
        self.xminDoubleSpinBox.setMinimum(time[0]*fac)
        self.xmaxDoubleSpinBox.setMaximum(time[-1]*fac)
        self.xmaxDoubleSpinBox.setMinimum(time[0]*fac)
        
    def displaySweep(self, clear=True):
        #print "loading sweep ..."
        #load the sweep self.sweepNum, of the File self.__File__ with channel self.__chans__
        #TODO add the Autoscale, manual scale and fullscale option.
        
        #matplotlib.pyplot.ioff()
        # Is this needed?
        # Hold probably interacts badly with the approach of using set_data on the first line of the subplot.
        '''if clear:
            matplotlib.pyplot.hold(False)
        else:
            matplotlib.pyplot.hold(True)
        '''
        #TODO: add a true loadSweep function and call this one displaySweep
        sw = self.lastSweep
        chanNames = sw.chanNames()
        chan=[i for i in range(len(chanNames)) if
                                   self.listScrollWidget[i][1].isChecked()]
        if clear:
            self.MPLFig.fig.clear()
        self.subplots = []
        sweepData = sw.get_data()
        
        for (subplotIndex,chanIndex) in enumerate(chan):
            if subplotIndex == 0:
                self.subplots.append(self.MPLFig.fig.add_subplot(len(chan), 1, 
                                     subplotIndex+1))
            else:
                self.subplots.append(self.MPLFig.fig.add_subplot(len(chan), 1,
                                     subplotIndex+1, sharex = self.subplots[0]))
            sy = self.subplots[subplotIndex]
            # Dummy line to allow use of set_data elsewhere.
            #sy.line = self.subplots[subplotIndex].plot([0,1])
            currentChan = getattr(sw, chanNames[chanIndex])
            sy.set_ylabel(currentChan.title+" ("+currentChan.units+")")
            sy.set_title(currentChan.name)
            # I can't get matplotlib autoscaling to work - it doesn't seem to register set_data data. So I do it my self.
            #sy.set_autoscale_on(self.autoscale[i])
            xticklabel = sy.get_xticklabels()
            sy.xaxis.set_visible(False)
            #chanIndex might not be the index of the data (i think 
            #they are some dict, but I'm not sure)
            indChan = sw._name2index[currentChan.name]
            sy.plot(sweepData[0,:]*self._factor(), sweepData[indChan,:], 
                    label = sw.name)
            
        self.actualiseDisplay()
    
    def actualiseDisplay(self,legend = False):
        sw = self.lastSweep
        xlimits=(sw.get_data()[0][0]*self._factor(),sw.get_data()[0][-1]*self._factor())
        chanNames = sw.chanNames()
        chan=[i for i in range(len(chanNames)) if
                                   self.listScrollWidget[i][1].isChecked()]
        for (subplotIndex,chanIndex) in enumerate(chan):
            sy = self.subplots[subplotIndex]
            currentChan = getattr(sw, chanNames[chanIndex])
            if self.listScrollWidget[chanIndex][4].isChecked(): #full is checked
                minlim = -currentChan.maxval
                maxlim = currentChan.maxval
                totlim = maxlim - minlim
                sy.set_ylim(minlim-totlim*0.1, maxlim+totlim*0.1)
                sy.set_xlim(xlimits)
                #print "full mode"
            elif self.listScrollWidget[chanIndex][2].isChecked(): #man is checked
                 sy.set_ylim(self.manscale[chanIndex][0], 
                             self.manscale[chanIndex][1])
                 #print "manual mode"
            else: #if self.listScrollWidget[chanIndex][3].isChecked() or no checkBox checked
                #print "auto mode"
                self.listScrollWidget[chanIndex][3].setChecked(True)
                #just in case no checkBox is checked (dunno how it could happend)
                Min = []
                Max = []
                for line in sy.lines:
                    sweepData = line.get_ydata()
                    Min.append(sweepData.min())
                    Max.append(sweepData.max())
                minlim = min(Min)
                maxlim = max(Max)
                totlim = maxlim - minlim
                sy.set_ylim(minlim-totlim*0.1,
                            maxlim+totlim*0.1)
                sy.set_xlim(xlimits)
            if legend:
                sy.legend(loc = 0)
                
        # Put the ticks back on the last subplot. I know.
        sy.xaxis.set_visible(True)
        # This would solve the issue that the xaxis is not tight, but it also causes the y axis of just the last plot to be tight also.
        #sy.axis('tight')
        sy.set_xlabel("Time (%s)"%self.currentunit)
             
        #self.MPLFig.fig.suptitle(df.fileName+": "+str(sweepNum),fontsize=12)
        
        # line[0] needs be set at initially (returned by a plot command) so that set_data has something to operate on.
        
        if self.xscaleCheckBox.isChecked():
            pass
            #if self.xminDoubleSpinBox.value() == self.xmaxDoubleSpinBox.value():
                #v=self.xminDoubleSpinBox.value()
                #self.xmaxDoubleSpinBox.setValue(float(v)+1)
        else:
            self.subplots[0].set_xlim(self.xminDoubleSpinBox.value(), 
                                      self.xmaxDoubleSpinBox.value())
          
        self.MPLFig.fig.canvas.draw()
        #print "______\n\n"
    
    def manScale(self,chan=None):
        if not chan:
            checkBox=self.sender()
            chan=int(checkBox.objectName()[0])
        lab, show, man, auto, full = self.listScrollWidget[chan]
        if not show.isChecked():
            prev =  (0,0)
        else:
            maxval=getattr(self.lastSweep, self.lastSweep.chanNames()[chan]).maxval
            axes =  [i for i, j in enumerate(self.listScrollWidget) if j[1].isChecked()]
            prev = self.MPLFig.fig.axes[axes.index(chan)].get_ylim()
        form = setscaledialog.SetScaleDialog(chan, maxval, prev, self)
        if form.exec_():
            #print "form.exec"
            self.manscale[chan]=form.results()
            #print form.results()
            self.updateFig()
            return
        #self.listScrollWidget[chan][3].setChecked(True)
        #print "form canceled"
        if self.manscale[chan] is None:
            self.listScrollWidget[chan][3].setChecked(True)
            #go back to auto scale if no manscale information
        self.updateFig()
    
    def allowxmodification(self):
        if self.xscaleCheckBox.isChecked():
            self.xminDoubleSpinBox.setEnabled(False)
            self.xmaxDoubleSpinBox.setEnabled(False)
            
        else:
            self.xminDoubleSpinBox.setEnabled(True)
            self.xmaxDoubleSpinBox.setEnabled(True)
    
    def showChan(self):
        if self.tabWidget.currentIndex() == 0:
            #simple  plot
            self.displaySweep()
        else:
            self.multiplot(self.listSweeps)
    
    def multiplot(self, listSweeps = None):
        if listSweeps is None:
            numSweeps = self.numSweepSpinBox.value()
            if self.range is None:
                self.range = range(self.numSweeps())
            if numSweeps >= len(self.range):
                self.listSweeps = self.range
            elif self.randomCheckBox.isChecked():
                self.listSweeps = []
                for n in range(numSweeps):
                    index = random.randint(0, len(self.range))
                    self.listSweeps.append(self.range.pop(index))
            else:
                self.listSweeps = [self.range[i] for i in range(numSweeps)]
        
        chan=[j for i, j in enumerate(self.chanNames()) if
                                   self.listScrollWidget[i][1].isChecked()]
        self.MPLFig.fig.clear()
        self.subplots = []
        sw = self.sweep(self.listSweeps[0])
        #loading one sweep only to have access to channelInfo
        for (subplotIndex,chanName) in enumerate(chan):
            if subplotIndex == 0:
                self.subplots.append(self.MPLFig.fig.add_subplot(len(chan), 1, 
                                     subplotIndex+1))
            else:
                self.subplots.append(self.MPLFig.fig.add_subplot(len(chan), 1,
                                     subplotIndex+1, sharex = self.subplots[0]))
            sy = self.subplots[subplotIndex]
            # Dummy line to allow use of set_data elsewhere.
            #sy.line = self.subplots[subplotIndex].plot([0,1])
            currentChan = getattr(sw, chanName)
            sy.set_ylabel(currentChan.units)
            sy.set_title(currentChan.title)
            # I can't get matplotlib autoscaling to work - it doesn't seem to register set_data data. So I do it my self.
            #sy.set_autoscale_on(self.autoscale[i])
            xticklabel = sy.get_xticklabels()
            sy.xaxis.set_visible(False)
            #chanIndex might not be the index of the data (i think 
            #they are some dict, but I'm not sure)
        length = len(self.listSweeps)
        print 'Multiplot ... %s traces to draw'%length
        pbar = pgb.ProgressBar(maxval=length,term_width = 79 ).start()
        for ind,index_sweep in enumerate(self.listSweeps):
            pbar.update(ind+1)
            sw = self.sweep(index_sweep, chan)
            if self.xjitterCheckBox.isChecked():
                sw._data[0] += random.rand() * sw.dt
            if self.subMeanCheckBox.isChecked():
                for i in range(1, sw._data.shape[0]):
                    sw._data[i] -= sw._data[i].mean()
            for subplotIndex, chanName in enumerate(chan):
                i = sw._name2index[chanName]
                self.subplots[subplotIndex].plot(sw._data[0] * self._factor(),
                                                 sw._data[i], 'k', lw = .05)
        self.actualiseDisplay()
        pbar.finish()
                
            
    @pyqtSignature("")
    def on_replotPushButton_clicked(self):
        self.showChan()
            
    @pyqtSignature("")
    def on_pltPushButton_clicked(self):
        self.multiplot()
    
    @pyqtSignature("")
    def on_rangePushButton_clicked(self):
        maxval = self.numSweeps()
        form = setRangeDlg.setRangeDlg(maxval, self.range, self)
        if form.exec_():
            self.listSweeps=form.results()
            print form.results()
            return
    
    @pyqtSignature("")
    def on_startButton_clicked(self):
        #print "start button"
        self.NumSpinBox.setValue(0)
        
    @pyqtSignature("")
    def on_nextButton_clicked(self):
        #print "next button"
        if self.sweepNum<self.numSweeps()-1:
            self.NumSpinBox.setValue(int(self.NumSpinBox.value())+1)
            
    @pyqtSignature("")
    def on_next10Button_clicked(self):
        if self.sweepNum+10<=self.numSweeps()-1:
            self.NumSpinBox.setValue(int(self.NumSpinBox.value())+10)
            
    @pyqtSignature("")
    def on_prevButton_clicked(self):
        if self.sweepNum>0:
            self.NumSpinBox.setValue(int(self.NumSpinBox.value())-1)
            
    @pyqtSignature("")
    def on_prev10Button_clicked(self):
        if self.sweepNum>10:
            self.NumSpinBox.setValue(int(self.NumSpinBox.value())-10)
            
    @pyqtSignature("")
    def on_endButton_clicked(self):
        self.NumSpinBox.setValue(self.numSweeps()-1)
        
    @pyqtSignature("int")
    def on_NumSpinBox_valueChanged(self,value):
        self.updateFig(value)
    
    @pyqtSignature("")
    def on_xscaleCheckBox_clicked(self):
        self.allowxmodification()
        xm, xM = self.MPLFig.fig.axes[0].get_xlim()
        self.xminDoubleSpinBox.setValue(xm)
        self.xmaxDoubleSpinBox.setValue(xM)
        self.updateFig()
    
    @pyqtSignature("double")
    def on_xminDoubleSpinBox_valueChanged(self,d):
        if self.xscaleCheckBox.isChecked():
            return
        else:
            self.updateFig()
    @pyqtSignature("double")
    def on_xmaxDoubleSpinBox_valueChanged(self,d):
        if self.xscaleCheckBox.isChecked():
            return
        else:
            self.updateFig()
    
    @pyqtSignature("QString")
    def on_xUnitComboBox_currentIndexChanged(self,d):
        self.currentunit = str(d)
        #self.updateFig()
#from pynaptix import *

#File=DataFile('/home/blot/Data/Pair_P-IN/090710A_001.wcp')
 
 
 
''' 
 def __init__(self):
        self.dataFile = None
        self.fig = matplotlib.pyplot.figure()
        self.chans = None
        # TODO add full scale option.
        self.autoscale=[]
'''
