# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_setRangeDlg

class setRangeDlg(QDialog, ui_setRangeDlg.Ui_setRangeDlg):

    def __init__(self, maxval, previousRange,parent=None):
        super(setRangeDlg, self).__init__(parent)
        self.setupUi(self)
        self.endSpinBox.setRange(0,maxval)
        self.endSpinBox.setValue(maxval)
        self.startSpinBox.setRange(0,maxval)
        self.stepSpinBox.setRange(1,maxval)
        if previousRange is not None:
            label = str(previousRange)
            label.strip('[]')
            self.listIndicesLineEdit.setText(QString(label))
    
    @pyqtSignature("")
    def on_applyPushButton_clicked(self):
        value = range(self.startSpinBox.value(), self.endSpinBox.value(),
                      self.stepSpinBox.value())
        label = str(value).strip('[]')
        self.listIndicesLineEdit.setText(QString(label))
    
    def results(self):
        out = str(self.listIndicesLineEdit.text())
        out = out.split(',')
        out = [int(i) for i in out]
        return out

