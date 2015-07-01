# Python_LSPS
This library is for executing a laser scanning photostimulation experiment in Python. 

Laser scanning photostimulation is used for activating specific populations of neurons in an in vitro slice preparation. Here the electrophysiological signals are recorded in pClamp which is synced to Python through an Arduino Uno microcontroller. Python controls the laser positioning as well recording the image of the tissue slice being stimulated and the coordinates of each stimulation. The stimulation order is random for each iteration (e.g. pClamp's Run). After a single run is completed (all site stimulated), Python imports the pClamp recording file (*.abf) and saves all data with the same filename. Thus, all analysis and visualization is performed in Python, rather than ClampFit.

I am currently working on interfacing Molecular Devices DigiData with Python to allow for all experimentation to be peformed in Python, negating the need for pClamp in these experiments. An alternative of course is to use a National Instruments DAQ system, but since so many labs use Molecular Devices DigiData DAQ systems and pClamp software, a Python solution would be quite useful.  

An Arduino Uno and digital-to-analog converters (MCP4725, http://www.adafruit.com/products/935) are used to position the scanning mirrors, which keeps the analog outputs on your digitizer free to control the patch clamp amplifiers. These 12-bit boards have plenty of resolution to accurately position the mirrors. 

The scanning mirrors I am currently using are from Thorlabs, but any system will work as you are merely delivering a voltage to position the mirror. For simplicity, I am currently only using positive voltages and merely positioning the tissue slice at the initial stimulation site.

The tissue is visualized through an analog camera (Dage-MTI, IR-1000), connected to a frame grabber. Commercially available digital cameras (e.g., QImaging) have not been tested. 

To run the interface simply type "python GUI.py" at the command prompt. Note that because this uses pClamp for the recordings, the full interface will only work in Windows.

Future plans:

Implement DigiData data acquisition in Python.


Develop a GUI interface for the analysis code.



