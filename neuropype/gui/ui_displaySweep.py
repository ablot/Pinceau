# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/blot/share/Python/neuropype/gui/displaySweep.ui'
#
# Created: Tue Apr 23 10:06:44 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_displaySweep(object):
    def setupUi(self, displaySweep):
        displaySweep.setObjectName(_fromUtf8("displaySweep"))
        displaySweep.setEnabled(True)
        displaySweep.resize(730, 468)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(5)
        sizePolicy.setHeightForWidth(displaySweep.sizePolicy().hasHeightForWidth())
        displaySweep.setSizePolicy(sizePolicy)
        self.horizontalLayout_3 = QtGui.QHBoxLayout(displaySweep)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.displayVLayout = QtGui.QVBoxLayout()
        self.displayVLayout.setObjectName(_fromUtf8("displayVLayout"))
        self.MPLFig = MPLQTFig(displaySweep)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.MPLFig.sizePolicy().hasHeightForWidth())
        self.MPLFig.setSizePolicy(sizePolicy)
        self.MPLFig.setObjectName(_fromUtf8("MPLFig"))
        self.displayVLayout.addWidget(self.MPLFig)
        self.MPLNav = MPLQTNav(displaySweep)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MPLNav.sizePolicy().hasHeightForWidth())
        self.MPLNav.setSizePolicy(sizePolicy)
        self.MPLNav.setObjectName(_fromUtf8("MPLNav"))
        self.displayVLayout.addWidget(self.MPLNav)
        self.horizontalLayout_3.addLayout(self.displayVLayout)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.tabWidget = QtGui.QTabWidget(displaySweep)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMaximumSize(QtCore.QSize(320, 16777215))
        self.tabWidget.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.simplePlotTab = QtGui.QWidget()
        self.simplePlotTab.setObjectName(_fromUtf8("simplePlotTab"))
        self.gridLayout = QtGui.QGridLayout(self.simplePlotTab)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.startButton = QtGui.QPushButton(self.simplePlotTab)
        self.startButton.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startButton.sizePolicy().hasHeightForWidth())
        self.startButton.setSizePolicy(sizePolicy)
        self.startButton.setMinimumSize(QtCore.QSize(40, 20))
        self.startButton.setMaximumSize(QtCore.QSize(80, 40))
        self.startButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.startButton.setAutoRepeat(True)
        self.startButton.setObjectName(_fromUtf8("startButton"))
        self.gridLayout.addWidget(self.startButton, 0, 1, 1, 1)
        self.prev10Button = QtGui.QPushButton(self.simplePlotTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.prev10Button.sizePolicy().hasHeightForWidth())
        self.prev10Button.setSizePolicy(sizePolicy)
        self.prev10Button.setMinimumSize(QtCore.QSize(40, 20))
        self.prev10Button.setMaximumSize(QtCore.QSize(80, 40))
        self.prev10Button.setFocusPolicy(QtCore.Qt.TabFocus)
        self.prev10Button.setAutoRepeat(True)
        self.prev10Button.setObjectName(_fromUtf8("prev10Button"))
        self.gridLayout.addWidget(self.prev10Button, 1, 1, 1, 1)
        self.prevButton = QtGui.QPushButton(self.simplePlotTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.prevButton.sizePolicy().hasHeightForWidth())
        self.prevButton.setSizePolicy(sizePolicy)
        self.prevButton.setMinimumSize(QtCore.QSize(40, 20))
        self.prevButton.setMaximumSize(QtCore.QSize(80, 40))
        self.prevButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.prevButton.setAutoRepeat(True)
        self.prevButton.setObjectName(_fromUtf8("prevButton"))
        self.gridLayout.addWidget(self.prevButton, 2, 1, 1, 1)
        self.sweepNumLabel = QtGui.QLabel(self.simplePlotTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sweepNumLabel.sizePolicy().hasHeightForWidth())
        self.sweepNumLabel.setSizePolicy(sizePolicy)
        self.sweepNumLabel.setMaximumSize(QtCore.QSize(100, 40))
        self.sweepNumLabel.setObjectName(_fromUtf8("sweepNumLabel"))
        self.gridLayout.addWidget(self.sweepNumLabel, 3, 0, 1, 1)
        self.NumSpinBox = QtGui.QSpinBox(self.simplePlotTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.NumSpinBox.sizePolicy().hasHeightForWidth())
        self.NumSpinBox.setSizePolicy(sizePolicy)
        self.NumSpinBox.setMinimumSize(QtCore.QSize(40, 20))
        self.NumSpinBox.setMaximumSize(QtCore.QSize(80, 40))
        self.NumSpinBox.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.NumSpinBox.setCorrectionMode(QtGui.QAbstractSpinBox.CorrectToNearestValue)
        self.NumSpinBox.setKeyboardTracking(False)
        self.NumSpinBox.setObjectName(_fromUtf8("NumSpinBox"))
        self.gridLayout.addWidget(self.NumSpinBox, 3, 1, 1, 1)
        self.nextButton = QtGui.QPushButton(self.simplePlotTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nextButton.sizePolicy().hasHeightForWidth())
        self.nextButton.setSizePolicy(sizePolicy)
        self.nextButton.setMinimumSize(QtCore.QSize(40, 20))
        self.nextButton.setMaximumSize(QtCore.QSize(80, 40))
        self.nextButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.nextButton.setAutoRepeat(True)
        self.nextButton.setObjectName(_fromUtf8("nextButton"))
        self.gridLayout.addWidget(self.nextButton, 4, 1, 1, 1)
        self.next10Button = QtGui.QPushButton(self.simplePlotTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.next10Button.sizePolicy().hasHeightForWidth())
        self.next10Button.setSizePolicy(sizePolicy)
        self.next10Button.setMinimumSize(QtCore.QSize(40, 20))
        self.next10Button.setMaximumSize(QtCore.QSize(80, 40))
        self.next10Button.setFocusPolicy(QtCore.Qt.TabFocus)
        self.next10Button.setAutoRepeat(True)
        self.next10Button.setObjectName(_fromUtf8("next10Button"))
        self.gridLayout.addWidget(self.next10Button, 5, 1, 1, 1)
        self.endButton = QtGui.QPushButton(self.simplePlotTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.endButton.sizePolicy().hasHeightForWidth())
        self.endButton.setSizePolicy(sizePolicy)
        self.endButton.setMinimumSize(QtCore.QSize(40, 20))
        self.endButton.setMaximumSize(QtCore.QSize(80, 40))
        self.endButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.endButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.endButton.setAutoRepeat(True)
        self.endButton.setObjectName(_fromUtf8("endButton"))
        self.gridLayout.addWidget(self.endButton, 6, 1, 1, 1)
        self.tabWidget.addTab(self.simplePlotTab, _fromUtf8(""))
        self.multiplotTab = QtGui.QWidget()
        self.multiplotTab.setObjectName(_fromUtf8("multiplotTab"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.multiplotTab)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.numSweepHLayout = QtGui.QHBoxLayout()
        self.numSweepHLayout.setObjectName(_fromUtf8("numSweepHLayout"))
        self.numSweepLabel = QtGui.QLabel(self.multiplotTab)
        self.numSweepLabel.setObjectName(_fromUtf8("numSweepLabel"))
        self.numSweepHLayout.addWidget(self.numSweepLabel)
        self.numSweepSpinBox = QtGui.QSpinBox(self.multiplotTab)
        self.numSweepSpinBox.setMinimum(1)
        self.numSweepSpinBox.setObjectName(_fromUtf8("numSweepSpinBox"))
        self.numSweepHLayout.addWidget(self.numSweepSpinBox)
        self.verticalLayout_3.addLayout(self.numSweepHLayout)
        self.rangeOptionHLayout = QtGui.QHBoxLayout()
        self.rangeOptionHLayout.setObjectName(_fromUtf8("rangeOptionHLayout"))
        self.rangePushButton = QtGui.QPushButton(self.multiplotTab)
        self.rangePushButton.setObjectName(_fromUtf8("rangePushButton"))
        self.rangeOptionHLayout.addWidget(self.rangePushButton)
        self.optionsPushButton = QtGui.QPushButton(self.multiplotTab)
        self.optionsPushButton.setObjectName(_fromUtf8("optionsPushButton"))
        self.rangeOptionHLayout.addWidget(self.optionsPushButton)
        self.verticalLayout_3.addLayout(self.rangeOptionHLayout)
        self.subMeanCheckBox = QtGui.QCheckBox(self.multiplotTab)
        self.subMeanCheckBox.setObjectName(_fromUtf8("subMeanCheckBox"))
        self.verticalLayout_3.addWidget(self.subMeanCheckBox)
        self.randomCheckBox = QtGui.QCheckBox(self.multiplotTab)
        self.randomCheckBox.setObjectName(_fromUtf8("randomCheckBox"))
        self.verticalLayout_3.addWidget(self.randomCheckBox)
        self.xjitterCheckBox = QtGui.QCheckBox(self.multiplotTab)
        self.xjitterCheckBox.setObjectName(_fromUtf8("xjitterCheckBox"))
        self.verticalLayout_3.addWidget(self.xjitterCheckBox)
        self.plotPushHLayout = QtGui.QHBoxLayout()
        self.plotPushHLayout.setObjectName(_fromUtf8("plotPushHLayout"))
        self.replotPushButton = QtGui.QPushButton(self.multiplotTab)
        self.replotPushButton.setObjectName(_fromUtf8("replotPushButton"))
        self.plotPushHLayout.addWidget(self.replotPushButton)
        self.pltPushButton = QtGui.QPushButton(self.multiplotTab)
        self.pltPushButton.setObjectName(_fromUtf8("pltPushButton"))
        self.plotPushHLayout.addWidget(self.pltPushButton)
        self.verticalLayout_3.addLayout(self.plotPushHLayout)
        self.tabWidget.addTab(self.multiplotTab, _fromUtf8(""))
        self.verticalLayout_2.addWidget(self.tabWidget)
        self.scrollArea = QtGui.QScrollArea(displaySweep)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMaximumSize(QtCore.QSize(320, 16777215))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaVBoxLayout = QtGui.QWidget()
        self.scrollAreaVBoxLayout.setGeometry(QtCore.QRect(0, 0, 302, 100))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollAreaVBoxLayout.sizePolicy().hasHeightForWidth())
        self.scrollAreaVBoxLayout.setSizePolicy(sizePolicy)
        self.scrollAreaVBoxLayout.setObjectName(_fromUtf8("scrollAreaVBoxLayout"))
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.scrollAreaVBoxLayout)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.labelHLayout = QtGui.QHBoxLayout()
        self.labelHLayout.setObjectName(_fromUtf8("labelHLayout"))
        self.chanLabel = QtGui.QLabel(self.scrollAreaVBoxLayout)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chanLabel.sizePolicy().hasHeightForWidth())
        self.chanLabel.setSizePolicy(sizePolicy)
        self.chanLabel.setObjectName(_fromUtf8("chanLabel"))
        self.labelHLayout.addWidget(self.chanLabel)
        self.showLabel = QtGui.QLabel(self.scrollAreaVBoxLayout)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.showLabel.sizePolicy().hasHeightForWidth())
        self.showLabel.setSizePolicy(sizePolicy)
        self.showLabel.setObjectName(_fromUtf8("showLabel"))
        self.labelHLayout.addWidget(self.showLabel)
        self.manLabel = QtGui.QLabel(self.scrollAreaVBoxLayout)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.manLabel.sizePolicy().hasHeightForWidth())
        self.manLabel.setSizePolicy(sizePolicy)
        self.manLabel.setObjectName(_fromUtf8("manLabel"))
        self.labelHLayout.addWidget(self.manLabel)
        self.autoLabel = QtGui.QLabel(self.scrollAreaVBoxLayout)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.autoLabel.sizePolicy().hasHeightForWidth())
        self.autoLabel.setSizePolicy(sizePolicy)
        self.autoLabel.setObjectName(_fromUtf8("autoLabel"))
        self.labelHLayout.addWidget(self.autoLabel)
        self.fullLabell = QtGui.QLabel(self.scrollAreaVBoxLayout)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fullLabell.sizePolicy().hasHeightForWidth())
        self.fullLabell.setSizePolicy(sizePolicy)
        self.fullLabell.setObjectName(_fromUtf8("fullLabell"))
        self.labelHLayout.addWidget(self.fullLabell)
        self.verticalLayout_7.addLayout(self.labelHLayout)
        self.headerLine = QtGui.QFrame(self.scrollAreaVBoxLayout)
        self.headerLine.setFrameShape(QtGui.QFrame.HLine)
        self.headerLine.setFrameShadow(QtGui.QFrame.Sunken)
        self.headerLine.setObjectName(_fromUtf8("headerLine"))
        self.verticalLayout_7.addWidget(self.headerLine)
        self.chanVBoxLayout = QtGui.QVBoxLayout()
        self.chanVBoxLayout.setObjectName(_fromUtf8("chanVBoxLayout"))
        self.verticalLayout_7.addLayout(self.chanVBoxLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_7.addItem(spacerItem)
        self.scrollArea.setWidget(self.scrollAreaVBoxLayout)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.groupBox = QtGui.QGroupBox(displaySweep)
        self.groupBox.setMaximumSize(QtCore.QSize(320, 16777215))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.xscaleCheckBox = QtGui.QCheckBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.xscaleCheckBox.sizePolicy().hasHeightForWidth())
        self.xscaleCheckBox.setSizePolicy(sizePolicy)
        self.xscaleCheckBox.setChecked(True)
        self.xscaleCheckBox.setObjectName(_fromUtf8("xscaleCheckBox"))
        self.horizontalLayout_2.addWidget(self.xscaleCheckBox)
        self.line = QtGui.QFrame(self.groupBox)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout_2.addWidget(self.line)
        spacerItem1 = QtGui.QSpacerItem(10, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.xUnitLabel = QtGui.QLabel(self.groupBox)
        self.xUnitLabel.setObjectName(_fromUtf8("xUnitLabel"))
        self.horizontalLayout_2.addWidget(self.xUnitLabel)
        self.xUnitComboBox = QtGui.QComboBox(self.groupBox)
        self.xUnitComboBox.setObjectName(_fromUtf8("xUnitComboBox"))
        self.horizontalLayout_2.addWidget(self.xUnitComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.xminLabel = QtGui.QLabel(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.xminLabel.sizePolicy().hasHeightForWidth())
        self.xminLabel.setSizePolicy(sizePolicy)
        self.xminLabel.setMaximumSize(QtCore.QSize(50, 16777215))
        self.xminLabel.setObjectName(_fromUtf8("xminLabel"))
        self.horizontalLayout.addWidget(self.xminLabel)
        self.xminDoubleSpinBox = QtGui.QDoubleSpinBox(self.groupBox)
        self.xminDoubleSpinBox.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.xminDoubleSpinBox.sizePolicy().hasHeightForWidth())
        self.xminDoubleSpinBox.setSizePolicy(sizePolicy)
        self.xminDoubleSpinBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.xminDoubleSpinBox.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedKingdom))
        self.xminDoubleSpinBox.setDecimals(4)
        self.xminDoubleSpinBox.setSingleStep(0.01)
        self.xminDoubleSpinBox.setObjectName(_fromUtf8("xminDoubleSpinBox"))
        self.horizontalLayout.addWidget(self.xminDoubleSpinBox)
        self.xmaxLabel = QtGui.QLabel(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.xmaxLabel.sizePolicy().hasHeightForWidth())
        self.xmaxLabel.setSizePolicy(sizePolicy)
        self.xmaxLabel.setMaximumSize(QtCore.QSize(50, 16777215))
        self.xmaxLabel.setObjectName(_fromUtf8("xmaxLabel"))
        self.horizontalLayout.addWidget(self.xmaxLabel)
        self.xmaxDoubleSpinBox = QtGui.QDoubleSpinBox(self.groupBox)
        self.xmaxDoubleSpinBox.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.xmaxDoubleSpinBox.sizePolicy().hasHeightForWidth())
        self.xmaxDoubleSpinBox.setSizePolicy(sizePolicy)
        self.xmaxDoubleSpinBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.xmaxDoubleSpinBox.setDecimals(4)
        self.xmaxDoubleSpinBox.setSingleStep(0.001)
        self.xmaxDoubleSpinBox.setObjectName(_fromUtf8("xmaxDoubleSpinBox"))
        self.horizontalLayout.addWidget(self.xmaxDoubleSpinBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.sweepNumLabel.setBuddy(self.NumSpinBox)
        self.numSweepLabel.setBuddy(self.numSweepSpinBox)
        self.xUnitLabel.setBuddy(self.xUnitComboBox)
        self.xminLabel.setBuddy(self.xminDoubleSpinBox)
        self.xmaxLabel.setBuddy(self.xmaxDoubleSpinBox)

        self.retranslateUi(displaySweep)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(displaySweep)
        displaySweep.setTabOrder(self.tabWidget, self.startButton)
        displaySweep.setTabOrder(self.startButton, self.prev10Button)
        displaySweep.setTabOrder(self.prev10Button, self.prevButton)
        displaySweep.setTabOrder(self.prevButton, self.NumSpinBox)
        displaySweep.setTabOrder(self.NumSpinBox, self.nextButton)
        displaySweep.setTabOrder(self.nextButton, self.next10Button)
        displaySweep.setTabOrder(self.next10Button, self.endButton)
        displaySweep.setTabOrder(self.endButton, self.scrollArea)
        displaySweep.setTabOrder(self.scrollArea, self.xscaleCheckBox)
        displaySweep.setTabOrder(self.xscaleCheckBox, self.xminDoubleSpinBox)
        displaySweep.setTabOrder(self.xminDoubleSpinBox, self.xmaxDoubleSpinBox)
        displaySweep.setTabOrder(self.xmaxDoubleSpinBox, self.numSweepSpinBox)
        displaySweep.setTabOrder(self.numSweepSpinBox, self.rangePushButton)
        displaySweep.setTabOrder(self.rangePushButton, self.optionsPushButton)
        displaySweep.setTabOrder(self.optionsPushButton, self.subMeanCheckBox)
        displaySweep.setTabOrder(self.subMeanCheckBox, self.randomCheckBox)
        displaySweep.setTabOrder(self.randomCheckBox, self.xjitterCheckBox)

    def retranslateUi(self, displaySweep):
        displaySweep.setWindowTitle(QtGui.QApplication.translate("displaySweep", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.startButton.setText(QtGui.QApplication.translate("displaySweep", "&Start", None, QtGui.QApplication.UnicodeUTF8))
        self.prev10Button.setText(QtGui.QApplication.translate("displaySweep", "-10", None, QtGui.QApplication.UnicodeUTF8))
        self.prevButton.setText(QtGui.QApplication.translate("displaySweep", "&Prev", None, QtGui.QApplication.UnicodeUTF8))
        self.sweepNumLabel.setText(QtGui.QApplication.translate("displaySweep", "S&weep num:", None, QtGui.QApplication.UnicodeUTF8))
        self.nextButton.setText(QtGui.QApplication.translate("displaySweep", "&Next", None, QtGui.QApplication.UnicodeUTF8))
        self.next10Button.setText(QtGui.QApplication.translate("displaySweep", "+10", None, QtGui.QApplication.UnicodeUTF8))
        self.endButton.setText(QtGui.QApplication.translate("displaySweep", "&End", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.simplePlotTab), QtGui.QApplication.translate("displaySweep", "Simple plo&t", None, QtGui.QApplication.UnicodeUTF8))
        self.numSweepLabel.setText(QtGui.QApplication.translate("displaySweep", "# of &sweeps:", None, QtGui.QApplication.UnicodeUTF8))
        self.rangePushButton.setText(QtGui.QApplication.translate("displaySweep", "Ran&ge", None, QtGui.QApplication.UnicodeUTF8))
        self.optionsPushButton.setText(QtGui.QApplication.translate("displaySweep", "Op&tions", None, QtGui.QApplication.UnicodeUTF8))
        self.subMeanCheckBox.setText(QtGui.QApplication.translate("displaySweep", "s&ubstract mean", None, QtGui.QApplication.UnicodeUTF8))
        self.randomCheckBox.setToolTip(QtGui.QApplication.translate("displaySweep", "If checked, select randomly the sweeps in sweep_list\n"
"Otherwise take the firsts", None, QtGui.QApplication.UnicodeUTF8))
        self.randomCheckBox.setText(QtGui.QApplication.translate("displaySweep", "&random", None, QtGui.QApplication.UnicodeUTF8))
        self.xjitterCheckBox.setText(QtGui.QApplication.translate("displaySweep", "x &jitter", None, QtGui.QApplication.UnicodeUTF8))
        self.replotPushButton.setToolTip(QtGui.QApplication.translate("displaySweep", "plot the same sweeps as previous call of Plot!", None, QtGui.QApplication.UnicodeUTF8))
        self.replotPushButton.setText(QtGui.QApplication.translate("displaySweep", "r&eplot", None, QtGui.QApplication.UnicodeUTF8))
        self.pltPushButton.setText(QtGui.QApplication.translate("displaySweep", "&Plot!", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.multiplotTab), QtGui.QApplication.translate("displaySweep", "&Multiplot", None, QtGui.QApplication.UnicodeUTF8))
        self.chanLabel.setText(QtGui.QApplication.translate("displaySweep", "Chan", None, QtGui.QApplication.UnicodeUTF8))
        self.showLabel.setText(QtGui.QApplication.translate("displaySweep", "Show", None, QtGui.QApplication.UnicodeUTF8))
        self.manLabel.setText(QtGui.QApplication.translate("displaySweep", "Man", None, QtGui.QApplication.UnicodeUTF8))
        self.autoLabel.setText(QtGui.QApplication.translate("displaySweep", "Auto", None, QtGui.QApplication.UnicodeUTF8))
        self.fullLabell.setText(QtGui.QApplication.translate("displaySweep", "Full", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("displaySweep", "x scale:", None, QtGui.QApplication.UnicodeUTF8))
        self.xscaleCheckBox.setText(QtGui.QApplication.translate("displaySweep", "&Auto", None, QtGui.QApplication.UnicodeUTF8))
        self.xUnitLabel.setText(QtGui.QApplication.translate("displaySweep", "&x units:", None, QtGui.QApplication.UnicodeUTF8))
        self.xminLabel.setText(QtGui.QApplication.translate("displaySweep", "&x min:", None, QtGui.QApplication.UnicodeUTF8))
        self.xmaxLabel.setText(QtGui.QApplication.translate("displaySweep", "x &Max:", None, QtGui.QApplication.UnicodeUTF8))

from neuropype.gui.MPLQTclasses import MPLQTFig, MPLQTNav
