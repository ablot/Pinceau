import matplotlib.pyplot as plt
import numpy as np

class nDplot(object):
    """Matplotlib tools to display a NxM matrix

    Used to plot M occurences of N different properties. If label is specified
    it must therefore be of length N"""
    
    def __init__(self, data, label = None):
        self._data = np.array(data, ndmin = 2)
        if label is not None:
            if not isinstance(label, list):
                label = list(label)
            if len(label) != data.shape[0]:
                raise IOError("len(label) != N")
            label = [str(i) for i in label]
        self._label = label
        self._figures = {}
        self._ca = None

    def gca(self):
        """return current axis, create one if needed"""
        if self._ca is not None:
            pass
        else:
            self._ca = self.gcf().add_subplot(111)
        return self._ca

    def gcf(self):
        """return current figure, create one if needed"""
        pas
        
    def simple_plot(self, x, y, ax = None, *args, **kwargs):
        """x and y can be a label or the index of one property"""
        if ax is None:
            ax = self.gca()
        try:
            x = self._label.index(x)
        except ValueError:
            x = int(x)
        try:
            y = self._label.index(y)
        except ValueError:
            y = int(y)
        xd = self._data[x]
        yd = self._data[y] 
        ax.plot(xd, yd, *args, **kwargs)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        return xd, yd
       