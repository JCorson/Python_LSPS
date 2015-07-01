import threading
import cv2
import time

from PySide import QtGui
  
class CameraThread(object):
    
    def __init__(self):
        self.name = "Camera"
        self.window_name = self.name
        #self.win = cv2.namedWindow(self.window_name)
        self.video = cv2.VideoCapture(0)
        print "Starting " + self.name  
        self.stopped = threading.Event()
           
    def startCamera(self):
        self.stopped.clear()
        t = threading.Thread(target=self.runCamera)
        t.start()
    
    def runCamera(self):    
        while not self.stopped.is_set():
            _, image = self.video.read()
            cv2.imshow(self.window_name, image)     
          
    def stopCamera(self):
        self.stopped.set()
    
    def closeCamera(self):
        self.stopCamera()
        time.sleep(1)
        self.video.release()
        time.sleep(1)
        cv2.destroyAllWindows()
            
    def capture(self):
        ret, image = self.video.read()
        return image  
        
    def capture_GUI(self):
        ret, frame = self.video.read()
        frame = cv2.cvtColor(frame, cv2.cv.CV_BGR2RGB)
        image = QtGui.QImage(frame, frame.shape[1], frame.shape[0],
                frame.strides[0], QtGui.QImage.Format_RGB888)
        imagePixMap = QtGui.QPixmap.fromImage(image)
        return imagePixMap    