import matplotlib as mp
mp.use('Qt4Agg')
mp.rcParams['backend.qt4']='PySide'

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MatplotlibWidget(FigureCanvas):
    def __init__(self, parent = None):
        super(MatplotlibWidget,self).__init__(Figure())
        
        self.setParent(parent)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.CameraFeedAxes = mp.pyplot.axes()
        self.ScatterAxes = mp.pyplot.axes()
    