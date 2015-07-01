""" This file will import and arrange a LSPS experiment into a multi-dimensional
    numpy array. Includes code to import previous LSPS experiments performed in MATLAB as well as current
    experiments performed in Python.
"""

from Load_ABF import importABF, readABF
import numpy as np
from os import listdir
from fnmatch import fnmatch
from scipy.io import loadmat
from sys import stdout

def importMatlabLSPS(directory):
    ABF_Files = []
    MAT_Files = []
    #NPZ_Files = []
    for File in listdir(directory):
        if fnmatch(File, '*.abf'):
            ABF_Files.append(File)
    for File in listdir(directory):
        if fnmatch(File, '*.mat'):
            MAT_Files.append(File)
    #for File in listdir(directory):
    #    if fnmatch(File, '*.npz'):
    #        NPZ_Files.append(File)
    Raw_Recording = importABF(ABF_Files[0])
    for File in ABF_Files[1:]:
        Raw_Recording = addRun(File, Raw_Recording)
    if not np.size(MAT_Files) == 0:    
        Parameters = loadMatlab_LSPS_Parameters(MAT_Files[0])
        Images = loadMatlab_LSPS_Image(MAT_Files[0])    
        for File in MAT_Files[1:]:
            tempParam = loadMatlab_LSPS_Parameters(File)
            for key in Parameters['Random_Stimulations'].keys():
                Parameters['Random_Stimulations'][(key)] = np.dstack((Parameters['Random_Stimulations'][key], tempParam['Random_Stimulations'][key]))
            tempImage = loadMatlab_LSPS_Image(File)
            Images = np.dstack((Images, tempImage))
        # Reorder the recordings based on random stimulation order
        Raw_Recording = reorderMatlabLSPS(Raw_Recording, Parameters) 

    return Raw_Recording, Parameters, Images
    
    
def addRun(filename, Raw_Data):   
    """Add a run of sweeps to the Signal Attribute in each Raw_Data.key. The data will be added to ndim = 2.
        """
    print "Adding {}...".format(filename)
    stdout.flush()

    Run = {} # Create empty dictionary
      
    blk = readABF(filename)
    
    # Get the signal names
    Sweep1 = blk.segments[0].analogsignals 
    Channel_Names = [] # Get the channel names and store in list
    for i in range(len(Sweep1)):
        temp = Sweep1[i].name
        Channel_Names.append(temp)
        
    # Create Run.keys from Channel_Names
    for name in Channel_Names:
        Run[name] = {}

    # Set up initial Signal dictionary key for each analog signal
    for i in range(len(Sweep1)):
        Run[Sweep1[i].name]['Signal'] = np.array(Sweep1[i])
    
    # Add the remaining sweeps to the Signal Key for each analog signal. Sweeps are added in n.dim = 1  
    for sweep in blk.segments[1:]:
        for channel in sweep.analogsignals:
            Run[channel.name]['Signal'] = np.vstack((Run[channel.name]['Signal'], np.array(channel)))
    for channel in sweep.analogsignals:
        Run[channel.name]['Signal'] = Run[channel.name]['Signal'].T  
    
    # Combine this Run with the previous Runs in Raw_Data     
    for name in Channel_Names:
        Raw_Data[name]['Signal'] = np.dstack((Raw_Data[name]['Signal'], Run[name]['Signal']))
    
    return Raw_Data
    
def loadMatlab_LSPS_Parameters(matfile):
    print 'Loading the parameters from {}...'.format(matfile)
    stdout.flush()
    #Load the matlab file into a temporary dictionary
    temp = loadmat(matfile,variable_names = 'Parameters', struct_as_record = True)
    
    # Set up parameters dictionary
    Parameters = {}
    Parameters = {'Calibration':[],
    'X_Length':temp['Parameters'][0][0][1][0],
    'Y_Length':temp['Parameters'][0][0][2][0],
    'Grid_Spacing':temp['Parameters'][0][0][3][0],
    'X_Offset':temp['Parameters'][0][0][4][0], 
    'Y_Offset':temp['Parameters'][0][0][5][0],
    'Calibration_X':temp['Parameters'][0][0][6][0],
    'Calibration_Y':temp['Parameters'][0][0][7][0], 
    'Num_Sites':temp['Parameters'][0][0][8][0],
    'Site_Coordinates':temp['Parameters'][0][0][9],
    'Site_Coordinates_Scatterplot':temp['Parameters'][0][0][10],
    'Random_Stimulations':[]}
    
    #Set up Parameters['Calibrations'] keys
    Calibration_arrays = temp['Parameters'][0][0][0][0][0]
    Parameters['Calibration'] = {'Galvo_Voltage': Calibration_arrays[0][0],
    'Scale':Calibration_arrays[1][0],
    'X_Initial':Calibration_arrays[2][0],
    'Y_Initial':Calibration_arrays[3][0],
    'X_Final':Calibration_arrays[4][0],
    'Y_Final':Calibration_arrays[5][0],
    'X_Cal':Calibration_arrays[6][0],
    'Y_Cal':Calibration_arrays[7][0]}
    
    #Set up Parameters['Random_Stimulations'] keys
    Random_Stimulation_arrays = temp['Parameters'][0][0][11][0][0]
    Parameters['Random_Stimulations'] = {'Coordinate_Order':Random_Stimulation_arrays[0][:,0],
    'Coordinates_X':Random_Stimulation_arrays[1][:,0],
    'Galvo_X':Random_Stimulation_arrays[2][:,0],
    'Coordinates_Y':Random_Stimulation_arrays[3][:,0],
    'Galvo_Y':Random_Stimulation_arrays[4][:,0]}
    
    return Parameters


def loadPython_LSPS_Parameters(npzfile):
    print 'Loading the parameters from {}...'.format(npzfile)
    stdout.flush()
    Parameters = np.load(npzfile)['Parameters'].item()
    return Parameters     
    
    
def loadPython_LSPS_Image(npzfile):
    print 'Loading the image from {}...'.format(npzfile)
    stdout.flush()
    Image = np.load(npzfile)['Image'][:,:,0]
    return Image 
    
    
def loadMatlab_LSPS_Image(matfile):
    print 'Loading the image from {}...'.format(matfile)
    stdout.flush()
    #Load the matlab file into a temporary dictionary
    temp = loadmat(matfile,variable_names = 'Image', struct_as_record = True)
    Image = temp['Image']
    return Image 


def loadPython_LSPS_Recording(npzfile):
    print 'Loading the recording from {}...'.format(npzfile)
    stdout.flush()
    Raw_Recording = np.load(npzfile)['Raw_Data'].item()
    return Raw_Recording


def reorderMatlabLSPS(Recording, Parameters):
    """
    """
    print 'Reordering recordings based on random stimulation order...'
    stdout.flush()
    for Input in Recording.keys():
        for run in range(np.size(Recording[(Input)]['Signal'][0,0,:])):
            Order = list(Parameters['Random_Stimulations']['Coordinate_Order'][:,:,run][0]-1)
            Recording[(Input)]['Signal'][:,:,run] = Recording[(Input)]['Signal'][:,Order,run]
    return Recording

def reorderPythonLSPS(Recording, Parameters):
    """
    """
    print 'Reordering recordings based on random stimulation order...'
    stdout.flush()
    for channel in Recording.keys():
        for run in range(np.size(Recording[(channel)]['Signal'][0,0,:])):
            Order = list(Parameters['Random_Stimulations']['Coordinate_Order'][:,:,run][0])
            Recording[(channel)]['Signal'][:,:,run] = Recording[(channel)]['Signal'][:,Order,run]
    return Recording
   
     
def loadLSPS(directory = '.'):
    """
    """
    # Generate a list of all NPZ files
    NPZ_Files = []
    ABF_Files = []
    
    for File in listdir(directory):
        if fnmatch(File, '*.abf'):
            ABF_Files.append(File[:-4])
            
    for File in listdir(directory):
        if fnmatch(File, '*.npz'):
            if File[:2] == '20':
                NPZ_Files.append(File)
   
    # Load first NPZ file
    Recording = loadPython_LSPS_Recording(NPZ_Files[0])
    Parameters = loadPython_LSPS_Parameters(NPZ_Files[0])
    Images = loadPython_LSPS_Image(NPZ_Files[0])

    # Load the remaining runs
    for File in NPZ_Files[1:]:
        # Load and organize Recordings
        tempRecording = loadPython_LSPS_Recording(File)
        for channel in tempRecording.keys():
            Recording[(channel)]['Signal'] = np.dstack((Recording[channel]['Signal'], tempRecording[channel]['Signal']))
        
        # Load and organize parameters
        tempParam = loadPython_LSPS_Parameters(File)
        for key in Parameters['Random_Stimulations'].keys():
            Parameters['Random_Stimulations'][(key)] = np.dstack((Parameters['Random_Stimulations'][key], tempParam['Random_Stimulations'][key]))
        
        # Load and organize Images
        tempImage = loadPython_LSPS_Image(File)
        Images = np.dstack((Images, tempImage))
        
        
    # Reorder the recordings based on random stimulation order
    Recording = reorderPythonLSPS(Recording, Parameters)  
    
    # Save the data
    saveData(Recording, Parameters, Images)
    
    # Return the Recording, Parameters, and Images
    return Recording, Parameters, Images
    
def saveData(Recording, Parameters, Images, filename = 'data.npz'):
    """ Save the Recording, Parameters, Images, and Results (if exists)
        into an .npz file (default = data.npz). 
    """
    print 'Saving Data...'
    stdout.flush()
    np.savez(filename, Parameters = Parameters, Recording = Recording, Images = Images)
            
    