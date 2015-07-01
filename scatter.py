""" This file will create a scatter plot of the stimulation sites to be overlaid on to the video feed.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from LSPS_Functions_GUI import Site_Coordinates

Parameters = np.load('Initial_Parameters.npz')['Parameters'].item()

Parameters = Site_Coordinates(Parameters)

x = Parameters['Site_Coordinates']['X_Coordinates_Scatter']
y = Parameters['Site_Coordinates']['Y_Coordinates_Scatter']


fig = plt.Figure(figsize=(6.4,4.8))
canvas = FigureCanvas(fig)

scatterAxes = fig.add_axes([0,0,1,1])

scatterAxes.tick_params(axis = 'both',
                    which = 'both',
                    bottom = 'off',
                    top = 'off',
                    left = 'off',
                    right = 'off',
                    labelbottom = 'off',
                    labelleft = 'off')
                    
scatterAxes.scatter(x,y)
scatterAxes.set_xlim(0,640)
scatterAxes.set_ylim(0,480)
scatterAxes.invert_yaxis()

fig.savefig('tempScatter.png', dpi = 100, transparent = True)
