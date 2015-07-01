""" This interface is heavily modified from the MATLAB arduinoIO interface. It is specific for the UNO 
    board with the Uno_LSPS sketch loaded.
"""

import serial
import numpy as np

class arduino(object):
    
    def __init__(self, port, baudrate=115200):
        self.serial = serial.Serial(port, baudrate)
 
    #deletes the object
    def delete_arduino(self):
        self.serial.close()
        return True
    #
    def __str__(self):
        return "Arduino is on port %s at %d baudrate" %(self.serial.port, self.serial.baudrate)

######################### CHANGE PIN MODE #################################
    def pinMode(self,pin,string):
        
        # determine input or output
        if string[0].lower() == 'o': 
            val=1 
        else:
            val=0
            
        # send mode, pin and value
        self.__sendFunction(48)
        self.__sendPin(pin)
        self.__sendData(48+val)           
        
######################### PERFORM DIGITAL INPUT ###########################                        
    def digitalRead(self,pin):            
                
        # send mode and pin()
        self.__sendFunction(49)
        self.__sendPin(pin)
        
        # get value
        val=self.__getData()
        return val

######################### PERFORM DIGITAL OUTPUT ##########################        
    def digitalWrite(self,pin,val):
     
        # send mode, pin and value
        self.__sendFunction(50)
        self.__sendPin(pin)
        self.__sendData(48+val)

######################### PERFORM ANALOG INPUT ############################        
    def analogRead(self,pin):
                   
        # send mode and pin
        self.__sendFunction(51)
        self.__sendPin(pin)
        
        # get value
        val=self.__getData()
        return val     

######################### PERFORM ANALOG OUTPUT ###########################        
    def analogWrite(self,pin,val):
               
        temp = np.array([val], dtype=np.uint16).view(np.uint8)
        
        val1 = temp[0]
        val2 = temp[1]
                
        # send mode, pin and value
        self.__sendFunction(52)
        self.serial.write(chr(pin))
        self.serial.write(chr(val1))
        self.serial.write(chr(val2))

#################### CHANGE ANALOG INPUT REFERENCE #########################        
    def analogReference(self,string):
                
        if string[0].lower() == 'e':
            num=2
        elif string[0].lower() == 'i':
            num=1
        else:
            num=0
                        
        # send mode, pin and value
        self.__sendFunction(82)
        self.serial.write(str(48+num))

#################### SUPPORT FUNCTIONS ######################################
    def __sendFunction(self, serial_data):
        self.serial.write(chr(serial_data))
        
    def __sendData(self, serial_data):
        self.serial.write(chr(serial_data))
    
    def __sendPin(self, pin):
        pin = pin+97
        self.__sendData(pin)
        
    def __getData(self):
        return self.serial.readline().replace("\r\n","")
    
    def __formatPinState(self, pinValue):
        if pinValue=='1':
            return True
        else:
            return False
