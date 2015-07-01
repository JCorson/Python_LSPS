""" Creates QThread and QLabel Widgets to be used in a LSPS GUI
"""
import sys
import numpy as np
from PySide import QtCore, QtGui
import matplotlib

matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PyQt4' 

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from Video_Capture import CameraThread
from LSPS_Functions_GUI import Save_Initial_Parameters

# Load the Parameters
Initial_Parameters = np.load('Initial_Parameters.npz')['Initial_Parameters'].item()        

# Start Camera
cameraFeed = CameraThread()

from LSPS_Functions_GUI import Site_Coordinates

class ScatterWidget(QtGui.QLabel):
    """ QLabel widget that displays a scaterplot of site coordinates 
        corresponding to the LSPS stimulation sites. The QLabel pixmap
        is created from a saved png file (which allows for a transparent
        background).
    """    
    positionClicked = QtCore.Signal(tuple)
    def __init__(self, parent =         None):
        QtGui.QLabel.__init__(self, parent)
        self.setFixedSize(640,480)
        #self.setPixmap('tempScatter.png')
        self.setToolTip('CTRL click to set initial laser position')
    
    def mousePressEvent(self, event):
        self.clickPosition = event.pos().toTuple()
        self.positionClicked.emit(self.clickPosition)        


class ScatterThread(QtCore.QThread):
    """ QThread that creates and updates the ScatterWidget.
        When the site coordinates are changed in any way 
        (e.g., changed initial laser position, changed grid dimensions)
        the updateScatter function is called. This updates the site
        coordinates,clears the scatterplot axes, replots the scatterplot, 
        saves the png file, and updates the ScatterWidget pixmap
    """  
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self,parent)
        self.exiting = False
        self.scatterWidget = ScatterWidget()
        self.scatterSize = QtCore.QSize(640,480)
        self.makeFigure()
        self.updateScatter(Initial_Parameters)
    
    def makeFigure(self): 
        self.fig = plt.Figure(figsize = (6.40,4.80))
        self.canvas = FigureCanvas(self.fig)
        self.scatterAxes = self.fig.add_axes([0,0,1,1])
        self.scatterAxes.tick_params(\
                    axis = 'both',
                    which = 'both',
                    bottom = 'off',
                    top = 'off',
                    left = 'off',
                    right = 'off',
                    labelbottom = 'off',
                    labelleft = 'off')        
      
    def updateScatter(self, Initial_Parameters):
        Parameters = Site_Coordinates(Initial_Parameters)
        self.scatterAxes.cla()
        self.x = Parameters['Site_Coordinates']['X_Coordinates_Scatter']
        self.y = Parameters['Site_Coordinates']['Y_Coordinates_Scatter']
        self.scatterAxes.scatter(self.x, self.y)
        self.scatterAxes.set_xlim(0,self.scatterSize.width())
        self.scatterAxes.set_ylim(0,480)
        self.scatterAxes.invert_yaxis()
        for item in [self.fig, self.scatterAxes]:
            item.patch.set_visible(False)
        self.fig.savefig('tempScatter.png', transparent = True, dpi = 100)
        self.scatterWidget.setPixmap('tempScatter.png')  

class CameraWidget(QtGui.QLabel):
    
    def __init__(self, parent = None):
        QtGui.QLabel.__init__(self, parent)
        self.setFixedSize(640,480)
        self.setupTimer()

    def setupTimer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateImage)
        self.timer.start(50)
        
    def updateImage(self):
        imagePixMap = cameraFeed.capture_GUI()
        self.setPixmap(imagePixMap)
    

class MainApp(QtGui.QWidget):
    
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setup_camera()
        self.setup_scatter()
        self.setup_ui()
        self.setMinimumSize(680, 600)
        

    def setup_ui(self):
        """Initialize widgets.
        """
        self.camera_scatter_layout = QtGui.QStackedLayout()
        self.camera_scatter_layout.setStackingMode(QtGui.QStackedLayout.StackAll)
        self.camera_scatter_layout.addWidget(self.cameraWidget)
        self.camera_scatter_layout.addWidget(self.scatterThread.scatterWidget)
        
        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.addLayout(self.camera_scatter_layout)
        self.setLayout(self.main_layout)
 
    def setup_camera(self):
        """Initialize camera as QLabel.
        """
        self.cameraWidget = CameraWidget()

    def setup_scatter(self):
        """Initialize the scatterplot of stimulation sites.
        """
        self.scatterThread = ScatterThread()
        self.scatterThread.scatterWidget.positionClicked.connect(self.update_stimCoordinate, QtCore.Qt.QueuedConnection)
    
    def update_stimCoordinate(self, pos):
        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier: 
            Initial_Parameters['X_Offset'] = pos[0]
            Initial_Parameters['Y_Offset'] = pos[1]
            Save_Initial_Parameters(Initial_Parameters)
            self.scatterThread.updateScatter(Initial_Parameters)

#win = MainApp()
#win.show()     
               
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    win = MainApp()
    win.show()
    app.exec_()                 