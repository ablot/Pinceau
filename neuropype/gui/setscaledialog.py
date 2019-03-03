# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_setscaledialog

class SetScaleDialog(QDialog, ui_setscaledialog.Ui_SetScale):

    def __init__(self,chan,maxval,previousScale,parent=None):
        super(SetScaleDialog, self).__init__(parent)
        self.setupUi(self)
        self.maxlimDoubleSpinBox.setRange(-maxval,maxval)
        self.minlimDoubleSpinBox.setRange(-maxval,maxval)
        if previousScale is not None:
            self.minlimDoubleSpinBox.setValue(previousScale[0])
            self.maxlimDoubleSpinBox.setValue(previousScale[1])
        self.label_3.setText("Set scale for channel "+str(chan)+":")
    
    def results(self):
        return (self.minlimDoubleSpinBox.value(),self.maxlimDoubleSpinBox.value())

