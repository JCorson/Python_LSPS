from PySide import QtCore, QtGui
import sys
import time
from os import listdir, stat
from fnmatch import fnmatch
import numpy as np

from Video_Capture_GUI import ScatterThread, CameraWidget
from Video_Capture import CameraThread
import LSPS_Functions_GUI as LSPS
from Load_ABF import importABF

# Set up the Hardware
print('Connecting to the Arduino')
sys.stdout.flush()
a = LSPS.Setup_Arduino('COM8') # Change COM port to match where the Arduino Uno is connected
Pins = LSPS.Setup_Pins()
#print('Connecting to the camera...')
#sys.stdout.flush()
cameraFeed = CameraThread()

# Load the Parameters
print('Loading Initial Parameters')
sys.stdout.flush()
Initial_Parameters = LSPS.Load_Initial_Parameters()

            
class Experiment(QtCore.QThread):
    """ This QThread executes the random scanning photostimulation experiment
        when the Experiment.start() function is called from the GUI. It 
        requires an arduino on COM11 (a), a Pins variable declared containing
        the arduino pins to sync python and the DigiData, and the Initial_Parameters
        variable containing the parameters to generate the Site_Coordinates
        and Random Stimulation Order. 
    """
    ExperimentRunSignal = QtCore.Signal(int)
    ExperimentSweepSignal = QtCore.Signal(int)
    
    
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self,parent)
        self.exiting = False
        
    def run(self):
        for run in range(int(win.numRunsBox.text())):
            if not self.exiting:
                self.ExperimentRunSignal.emit(run) # Update the Run Progress status bar.
                print ""
                print('Executing Run #%i' % (run+1))
                sys.stdout.flush()
                self.Execute_Run(a, Pins, Initial_Parameters)
            else:
                print "Terminating Experiment..."
                sys.stdout.flush()
                self.exit()
                self.exiting = False
                break

        win.Reset()
    ####################### Main Experiment Function #########################
    def Execute_Run(self, a, Pins, Initial_Parameters):
        self.stopped = 0 # Break variable
        a.pinMode(Pins['DigiData_Start'], 'output')         
        
        # Generate Site Coordinates               
        Parameters = LSPS.Site_Coordinates(Initial_Parameters)
        Parameters = LSPS.Random_Sites(Parameters)
        time.sleep(1)
        
        for i in range(Parameters['Num_Sites']):
            if self.exiting:
                self.exit()
                break
            else:    
                self.ExperimentSweepSignal.emit(i)# Update Signal Progress Bar
                
                # Set Galvos
                a.analogWrite(20,Parameters['Random_Stimulations']['Galvo_X'][i])
                a.analogWrite(21,Parameters['Random_Stimulations']['Galvo_Y'][i])
                time.sleep(0.1)
                
                # DigiData Start
                a.digitalWrite(Pins['DigiData_Start'], 1)
                time.sleep(0.1)
                a.digitalWrite(Pins['DigiData_Start'], 0)
                
                # Wait until recording finishes
                temp = int(a.digitalRead(Pins['DigiData_DOut']))
                break_time = time.clock()+5 # Timeout time
                
                while temp == 0:
                    temp = int(a.digitalRead(Pins['DigiData_DOut']))
                    # Check for timeout
                    if time.clock() > break_time:
                        a.analogWrite(20,0)
                        a.analogWrite(21,0)
                        win.progBarRun.setValue(0)#set(handles.runProgress, 'String', '')
                        win.progBarSweep.setValue(0)#set(handles.sweepProgress, 'String', '')
                        win.startExperimentButton.setText('Start Experiment')#set(handles.startExperiment, 'String', 'Start Experiment')
                        print('Digital Read Timed Out...')
                        sys.stdout.flush()
                        self.exiting = True
                        break                
                time.sleep(0.3)
            
        # Reset Galvos
        a.analogWrite(20,0)
        a.analogWrite(21,0)
        
        if not self.exiting:    
            # Capture DIC Image 
            print('Capturing DIC Image')
            sys.stdout.flush()
            Image = cameraFeed.capture()
            time.sleep(1)
        
            """ These directories are system specific and should be modified by the user to match where the data will be stored.
            """
            # Import Recording Data
            ABF_Files = []
            for file in listdir("C:/Users/RMBradley/Desktop/pClamp Recordings"):
                if fnmatch(file, '*.abf'):
                    if stat("C:/Users/RMBradley/Desktop/pClamp Recordings/"+file).st_size>100000: # Only include files over 100kB. pClamp saves a temp file for the next recording that should be ignored.
                        ABF_Files.append(file)
    
            Raw_Data = importABF(str("C:/Users/RMBradley/Desktop/pClamp Recordings/"+ ABF_Files[-1]))
            
            # Save Data
            print 'Saving data...'
            sys.stdout.flush()
            filename = ABF_Files[-1].replace('.abf', '')
            
            np.savez(str("C:/Users/RMBradley/Desktop/pClamp Recordings/"+ filename),Parameters=Parameters, Image=Image, Raw_Data=Raw_Data)
            #time.sleep(2)
        ###########################################################################   
        
class MainApp(QtGui.QWidget):  
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.video_size = QtCore.QSize(640, 480)
        self.setup_camera()
        self.setup_scatter()
        self.experimentThread = Experiment()
        self.setup_ui()
        self.setMinimumSize(680, 600)
        
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message', 
        "Are you sure you want to quit?", QtGui.QMessageBox.Yes |
        QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        
        if reply == QtGui.QMessageBox.Yes:
            LSPS.Save_Initial_Parameters(Initial_Parameters)
            self.scatterThread.exiting = True
            self.scatterThread.quit()
            event.accept()
        else:
            event.ignore()
 
    def setup_ui(self):
        """Initialize widgets.
        """
        # Stimulation Parameters
        self.rowsBox = QtGui.QLineEdit(str(Initial_Parameters['Y_Length']))
        self.colsBox = QtGui.QLineEdit(str(Initial_Parameters['X_Length']))
        self.rowsBox.editingFinished.connect(self.update_InitialParameters, QtCore.Qt.QueuedConnection)
        self.colsBox.editingFinished.connect(self.update_InitialParameters, QtCore.Qt.QueuedConnection) 
        self.numRunsBox = QtGui.QLineEdit('10')
        self.numRunsBox.editingFinished.connect(self.set_RunProgressBar, QtCore.Qt.QueuedConnection)
        self.cellIDBox = QtGui.QLineEdit('None')
        self.param_layout = QtGui.QFormLayout()
        self.param_layout.addRow('# Rows', self.rowsBox)
        self.param_layout.addRow('# Cols', self.colsBox)
        self.param_layout.addRow('# Runs', self.numRunsBox)
        self.param_layout.addRow('Cell ID', self.cellIDBox)
        
        # Start Experiment Buttons
        self.startExperimentButton = QtGui.QPushButton('Start Experiment')
        self.startExperimentButton.clicked.connect(self.Execute_Experiment, QtCore.Qt.QueuedConnection)
        self.experimentThread.ExperimentRunSignal.connect(self.update_RunProgressBar, QtCore.Qt.QueuedConnection)
        self.experimentThread.ExperimentSweepSignal.connect(self.update_SweepProgressBar, QtCore.Qt.QueuedConnection)

        
        # Progress Bars
        self.progBarRunLabel = QtGui.QLabel('Run Progress')
        self.progBarRun = QtGui.QProgressBar()
        self.progBarRun.setFormat('%m')
        self.progBarRun.setTextVisible(True)
        self.progBarRun.setValue(0)
        self.set_RunProgressBar()
        self.progBarSweepLabel = QtGui.QLabel('Sweep Progress')
        self.progBarSweep = QtGui.QProgressBar()
        self.progBarSweep.setFormat('%m')        
        self.progBarSweep.setTextVisible(True)
        self.progBarSweep.setValue(0)
        self.set_SweepProgressBar()
        self.progress_layout = QtGui.QVBoxLayout()
        self.progress_layout.addWidget(self.progBarSweepLabel)
        self.progress_layout.addWidget(self.progBarSweep)
        self.progress_layout.addWidget(self.progBarRunLabel)
        self.progress_layout.addWidget(self.progBarRun)

        
        # Video Feed
        self.camera_scatter_layout = QtGui.QStackedLayout()
        self.camera_scatter_layout.setStackingMode(QtGui.QStackedLayout.StackAll)
        self.camera_scatter_layout.addWidget(self.cameraWidget)
        self.camera_scatter_layout.addWidget(self.scatterThread.scatterWidget)
        
        # Parameter and Status Bar Layout
        self.experiment_layout = QtGui.QHBoxLayout()
        self.experiment_layout.addLayout(self.param_layout)
        self.experiment_layout.addLayout(self.progress_layout)
        
        # Main Layout
        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.addLayout(self.experiment_layout)
        self.main_layout.addLayout(self.camera_scatter_layout)
        self.main_layout.addWidget(self.startExperimentButton)
        self.setLayout(self.main_layout)
 
    def setup_camera(self):
        """Initialize camera as QThread.
        """
        self.cameraWidget = CameraWidget()
 
    def setup_scatter(self):
        """Initialize the scatterplot of stimulation sites.
        """
        self.scatterThread = ScatterThread()
        self.scatterThread.scatterWidget.positionClicked.connect(self.update_InitialLaserPosition, QtCore.Qt.QueuedConnection)
        if not self.scatterThread.isRunning():
            self.scatterThread.start()
            
    def update_InitialParameters(self):
        try:
            Initial_Parameters['X_Length'] = int(self.colsBox.text())
        except ValueError:
            Initial_Parameters['X_Length'] = 0
            self.colsBox.setText(u'0')
        try:         
            Initial_Parameters['Y_Length'] = int(self.rowsBox.text())
        except ValueError:
            Initial_Parameters['Y_Length'] = 0
            self.rowsBox.setText(u'0')   
            
        self.set_SweepProgressBar()
        self.scatterThread.updateScatter(Initial_Parameters)
            
    def update_stimCoordinates(self):
        self.scatterThread.updateScatter(Initial_Parameters)
    
    def update_InitialLaserPosition(self, pos):
        """ Update initial laser position by Control-Clicking on the video feed window.
        """
        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier: 
            Initial_Parameters['X_Offset'] = int(pos[0])
            Initial_Parameters['Y_Offset'] = int(pos[1])
            self.scatterThread.updateScatter(Initial_Parameters)
    
    def update_RunProgressBar(self,run):
        """ Updates the run progress bar. Slot connected to the 
            Experiment.ExperimentRunSignal signal.
        """
        self.progBarRun.setValue(run)
        
    def update_SweepProgressBar(self,sweep):
        """ Updates the sweep progress bar. Slot connected to the 
            Experiment.ExperimentSweepSignal signal.
        """
        self.progBarSweep.setValue(sweep)
    
    def set_RunProgressBar(self):
        """ Sets the Run Progress Bar range when parameters change.
        """
        self.progBarRun.setRange(0,int(self.numRunsBox.text()))    
    
    def set_SweepProgressBar(self):
        """ Sets the Sweep Progress Bar range when parameters change.
        """
        self.progBarSweep.setRange(0,int(self.rowsBox.text())*int(self.colsBox.text()))    
                
                
    def Execute_Experiment(self):
        """ Executes the Experiment.
        """
        if self.startExperimentButton.text() == 'Start Experiment':
            # Start Experiment
            self.startExperimentButton.setText('Stop Experiment')
            self.experimentThread.start()
        
        elif self.startExperimentButton.text() == 'Stop Experiment':
            self.experimentThread.exiting = True 
            # Reset
            self.Reset()
  
    def Reset(self):
        """ Resets the progress bars and Start Experiment Button to their
            initial states.
        """
        self.progBarRun.setValue(0)
        self.progBarSweep.setValue(0)
        self.startExperimentButton.setText('Start Experiment')
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    win = MainApp()
    win.show()
    sys.exit(app.exec_())