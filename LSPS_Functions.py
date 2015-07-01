import numpy as np
from arduinoIO import arduino
import time
from os import listdir
from fnmatch import fnmatch
from Load_ABF import importABF
from Video_Capture import CameraThread
from sys import stdout

# Set up Arduino
def Setup_Arduino(ComPort):
    global a
    a = arduino(ComPort)

# Set IO pins for DigiData-Arduino Communication
def Setup_Pins():
    global Pins
    Pins = {'DigiData_Start':16, 'DigiData_DOut':17}

# Set up parameters dictionary
def Setup_Parameters():
    Parameters = {}
    Parameters = {'Calibration':{},
    'X_Length':20,
    'Y_Length':15,
    'Grid_Spacing':50,
    'X_Offset':74.5, 
    'Y_Offset':21.5,
    'Calibration_X':84.86,
    'Calibration_Y':85.7692, 
    'Num_Sites':[],
    'Site_Coordinates':{},
    'Random_Stimulations':{}}
    
    #Calculate number of sites
    Parameters['Num_Sites'] = (Parameters['X_Length'])*(Parameters['Y_Length'])
    
    #Set up Parameters['Calibrations'] keys
    Parameters['Calibration'] = {'Galvo_Voltage': 1500,
    'Scale':3.123,
    'X_Initial':146,
    'Y_Initial':84,
    'X_Final':429,
    'Y_Final':364,
    'X_Cal':1.6972,
    'Y_Cal':1.7154}
    return Parameters
    
def Load_Parameters():
    Initial_Parameters = np.load('Initial_Parameters.npz')['Parameters']
    return Initial_Parameters.all()
    
def Save_Parameters(Parameters):
    np.savez('Initial_Parameters', Parameters = Parameters)

def Site_Coordinates(Parameters):  
    # Site ID Number
    Parameters['Site_Coordinates']['Site_ID'] = np.arange(Parameters['Num_Sites'],dtype = 'int16')
    # X Coordinate Number
    Parameters['Site_Coordinates']['X_Coordinates'] = np.array(range(Parameters['X_Length'])*Parameters['Y_Length'],dtype = 'int16')
    # X Coordinates Scaled by Calibration X
    Parameters['Site_Coordinates']['X_Coordinates_Scaled'] = Parameters['Site_Coordinates']['X_Coordinates'] * int(Parameters['Calibration_X'])
    # X Coordinates for Scatter plot
    Parameters['Site_Coordinates']['X_Coordinates_Scatter'] = Parameters['Site_Coordinates']['X_Coordinates'] * int(Parameters['Grid_Spacing']/Parameters['Calibration']['Scale'])+int(Parameters['X_Offset'])
    # Y Coordinate Number
    Parameters['Site_Coordinates']['Y_Coordinates'] = np.array(np.empty(Parameters['Num_Sites']),dtype = 'int16')
    for n in range(Parameters['Y_Length']):
        Parameters['Site_Coordinates']['Y_Coordinates'][(n*Parameters['X_Length']):(Parameters['X_Length']+(n*Parameters['X_Length']))] = n
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
    
def Execute_Experiment(a, Pins, Parameters, FG):
    a.pinMode(Pins['DigiData_Start'], 'output')
    Parameters = Site_Coordinates(Parameters)
    Parameters = Random_Sites(Parameters)
    time.sleep(1)
    for i in range(Parameters['Num_Sites']):
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
        while temp == 0:
            temp = int(a.digitalRead(Pins['DigiData_DOut']))
        time.sleep(0.3)
        
   # Reset Galvos
    a.analogWrite(20,0)
    a.analogWrite(21,0)
    
   # Capture DIC Image 
    Image = FG.capture()
    time.sleep(1)
   
   # Import Recording Data
    ABF_Files = []
    for file in listdir('C:/Users/RMBradley/Desktop/pClamp Recordings'):
        if fnmatch(file, '*.abf'):
            ABF_Files.append(file)
    Raw_Data = importABF(str('C:/Users/RMBradley/Desktop/pClamp Recordings/'+ ABF_Files[-1])) 
    
   # Save Data
    print 'Saving data...'
    stdout.flush()
    filename = ABF_Files[-1].replace('.abf', '')
    np.savez(str('C:/Users/RMBradley/Desktop/pClamp Recordings/'+ filename),Parameters=Parameters, Image=Image, Raw_Data=Raw_Data)

def Start_Camera():
    Frame_Grabber = CameraThread('Camera')
    Frame_Grabber.startCamera()
    return Frame_Grabber