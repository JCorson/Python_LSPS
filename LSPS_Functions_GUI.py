import numpy as np
from arduinoIO import arduino
from os import name

# Set up Arduino
def Setup_Arduino(ComPort):
    a = arduino(ComPort)
    return a

# Set IO pins for DigiData-Arduino Communication
def Setup_Pins():
    Pins = {'DigiData_Start':16, 'DigiData_DOut':17}
    return Pins

# Set up parameters dictionary
def Setup_Parameters():
    Parameters = {}
    Parameters = {'Calibration':{},
    'X_Length':20,
    'Y_Length':15,
    'Grid_Spacing':50,
    'X_Offset':56, # Pixels of X-Offset
    'Y_Offset':32, # Pixels of Y-Offset
    'Calibration_X':84.3, # Voltage required to move laser spot 50um in x axis. Based on Calibrations below.
    'Calibration_Y':84.25, # Voltage required to move laser spot 50um in y axis. Based on Calibrations below.
    'Num_Sites':[],
    'Site_Coordinates':{},
    'Random_Stimulations':{}}
    
    #Calculate number of sites
    Parameters['Num_Sites'] = (Parameters['X_Length'])*(Parameters['Y_Length'])
    
    #Set up Parameters['Calibrations'] keys
    Parameters['Calibration'] = {'Galvo_Voltage': 1500,
    'Scale':3.123,
    'X_Initial':48,
    'Y_Initial':29,
    'X_Final':336,
    'Y_Final':314,
    'X_Cal':1.686,
    'Y_Cal':1.685}
    return Parameters
    
def Reset_Parameters(Parameters):
    Parameters['Site_Coordinates'] = {}
    Parameters['Random_Stimulations'] = {}
    
def Load_Initial_Parameters():
    """ These directories are system specific and should be modified by the user to match where the data will be stored.
    """
    if name == 'posix':
        Initial_Parameters = np.load('Initial_Parameters.npz')['Initial_Parameters']
    else: 
        Initial_Parameters = np.load('C:/Users/RMBradley/Box Sync/Python_Files/LSPS_Python/Initial_Parameters.npz')['Initial_Parameters']
    return Initial_Parameters.all()
    
def Save_Initial_Parameters(Initial_Parameters):
    """ These directories are system specific and should be modified by the user to match where the data will be stored.
    """
    if name == 'posix':
        np.savez('/Volumes/Corson/Users/Jim/Box Sync/Python_Files/LSPS_Python/Initial_Parameters.npz', Initial_Parameters = Initial_Parameters)
    else:
        np.savez('C:/Users/RMBradley/Box Sync/Python_Files/LSPS_Python/Initial_Parameters.npz', Initial_Parameters = Initial_Parameters)

def Site_Coordinates(Initial_Parameters):
    Parameters = Initial_Parameters.copy()
    # Set the number of sites
    Parameters['Num_Sites'] = (Parameters['X_Length'])*(Parameters['Y_Length']) 
    # Site ID Number
    Parameters['Site_Coordinates']['Site_ID'] = np.arange(Parameters['Num_Sites'],dtype = 'int16')
    # X Coordinate Number
    Parameters['Site_Coordinates']['X_Coordinates'] = np.array(range(int(Parameters['X_Length']))*int(Parameters['Y_Length']),dtype = 'int16')
    # X Coordinates Scaled by Calibration X
    Parameters['Site_Coordinates']['X_Coordinates_Scaled'] = Parameters['Site_Coordinates']['X_Coordinates'] * int(Parameters['Calibration_X'])
    # X Coordinates for Scatter plot
    Parameters['Site_Coordinates']['X_Coordinates_Scatter'] = Parameters['Site_Coordinates']['X_Coordinates'] * int(Parameters['Grid_Spacing']/Parameters['Calibration']['Scale'])+int(Parameters['X_Offset'])
    # Y Coordinate Number
    Parameters['Site_Coordinates']['Y_Coordinates'] = np.array(np.empty(Parameters['Num_Sites']),dtype = 'int16')
    for n in range(int(Parameters['Y_Length'])):
        Parameters['Site_Coordinates']['Y_Coordinates'][(n*int(Parameters['X_Length'])):(int(Parameters['X_Length'])+(n*int(Parameters['X_Length'])))] = n
    # Y Coordinates Scaled by Calibration Y
    Parameters['Site_Coordinates']['Y_Coordinates_Scaled'] = Parameters['Site_Coordinates']['Y_Coordinates'] * int(Parameters['Calibration_Y'])
    # Column 6: Y Coordinates for Scatter plot
    Parameters['Site_Coordinates']['Y_Coordinates_Scatter'] = Parameters['Site_Coordinates']['Y_Coordinates'] * int(Parameters['Grid_Spacing']/Parameters['Calibration']['Scale'])+int(Parameters['Y_Offset'])

    return Parameters

def Random_Sites(Parameters):
    Parameters['Random_Stimulations']['Coordinate_Order'] = np.empty(Parameters['Num_Sites'],dtype = 'int16')
    Parameters['Random_Stimulations']['Coordinate_Order'][0] = 0
    Parameters['Random_Stimulations']['Coordinate_Order'][1:] = np.random.permutation(Parameters['Site_Coordinates']['Site_ID'][1:])
    Parameters['Random_Stimulations']['X_Coordinates'] = Parameters['Site_Coordinates']['X_Coordinates'][list(Parameters['Random_Stimulations']['Coordinate_Order'])]
    Parameters['Random_Stimulations']['Galvo_X'] = np.array(Parameters['Random_Stimulations']['X_Coordinates'] * Parameters['Calibration_X'],dtype = 'int16')
    Parameters['Random_Stimulations']['Y_Coordinates'] = Parameters['Site_Coordinates']['Y_Coordinates'][list(Parameters['Random_Stimulations']['Coordinate_Order'])]
    Parameters['Random_Stimulations']['Galvo_Y'] = np.array(Parameters['Random_Stimulations']['Y_Coordinates'] * Parameters['Calibration_Y'],dtype = 'int16')
    return Parameters
    