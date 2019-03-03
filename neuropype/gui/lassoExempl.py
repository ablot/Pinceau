"""
MODIFIED a bit
Show how to use a lasso to select a set of points and get the indices
of the selected points.  A callback is used to change the color of the
selected points

This is currently a proof-of-concept implementation (though it is
usable as is).  There will be some refinement of the API and the
inside polygon detection routine.
"""
 
from matplotlib.widgets import Lasso
from matplotlib.nxutils import points_inside_poly
from matplotlib.colors import colorConverter
from matplotlib.collections import RegularPolyCollection

from matplotlib.pyplot import figure, show
from numpy import nonzero
from numpy.random import rand


class LassoManager:
    def __init__(self, ax, data, colorin = 'blue', colorout = 'black',**kwargs):
        """Data must be a 2D array"""
        self.colorin = colorConverter.to_rgba(colorin)
        self.colorout = colorConverter.to_rgba(colorout)
        self.axes = ax
        self.canvas = ax.figure.canvas
        self.data = data
        
        facecolors = [colorout]*self.data.shape[0]
        fig = ax.figure
        if not kwargs.has_key('sizes'):
            kwargs['sizes'] = (10,)
        self.collection = RegularPolyCollection(
            fig.dpi, 6, 
            facecolors=facecolors,
            offsets = self.data,
            transOffset = ax.transData, **kwargs)

        ax.add_collection(self.collection)

        self.cid = self.canvas.mpl_connect('button_press_event', self.onpress)
        self.ind = None

    def callback(self, verts):
        facecolors = self.collection.get_facecolors()
        self.isinside = points_inside_poly(self.data, verts)
        ind = nonzero(self.isinside)[0]
        for i in range(self.data.shape[0]):
            if i in ind:
                facecolors[i] = self.colorin
            else:
                facecolors[i] = self.colorout

        self.canvas.draw_idle()
        self.canvas.widgetlock.release(self.lasso)
        del self.lasso
    
    def onpress(self, event):
        if self.canvas.widgetlock.locked(): return
        if event.inaxes is None: return
        self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata), self.callback)
        # acquire a lock on the widget drawing
        self.canvas.widgetlock(self.lasso)
        
if __name__ == '__main__':

    data = rand(1e3, 2)

    fig = figure()
    ax = fig.add_subplot(111, xlim=(0,1), ylim=(0,1), autoscale_on=False)
    lman = LassoManager(ax, data)

    show()
