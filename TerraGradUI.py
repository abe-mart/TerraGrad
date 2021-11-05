# -*- coding: utf-8 -*-
"""
Created on Sat Oct 23 12:25:24 2021

@author: oacom
"""

import numpy as np
import matplotlib.pyplot as plt
from numpy import interp
import imageio
import io
import os
import PySimpleGUI as sg
from PIL import Image

# Define linear interpolation function
def map_range_np(value, leftMin, leftMax, rightMin, rightMax):
    return interp(value,[leftMin,leftMax],[rightMin,rightMax])

def checkfile(path):
     path      = os.path.expanduser(path)

     if not os.path.exists(path):
        return path

     root, ext = os.path.splitext(os.path.expanduser(path))
     dir       = os.path.dirname(root)
     fname     = os.path.basename(root)
     candidate = fname+ext
     index     = 0
     ls        = set(os.listdir(dir))
     while candidate in ls:
             candidate = "{}_{}{}".format(fname,index,ext)
             index    += 1
     return os.path.join(dir,candidate)
    
ter = []
r = 2
    
def main():
    layout = [
        [sg.Image(key="-IMAGE-")],
        [sg.FileBrowse('Choose Terrain',key='file_name_ter',file_types=(("EXR Terrain Files", "*.exr"),),enable_events=True,change_submits=True),
         sg.Button('Add Color',key='add_color'),
         sg.Button('Preview',key='color_terrain'),
         sg.Button('Export',key='export')],
        [sg.Text('Color 1:'), 
         sg.Text('R'),sg.InputText('0',size=(3,1),key='R0'), 
         sg.Text('G'),sg.InputText('0',size=(3,1),key='G0'),
         sg.Text('B'),sg.InputText('0',size=(3,1),key='B0'),
         sg.Text('Elevation'),sg.InputText('-1000',size=(8,1),key='E0'),
        ],
        [sg.Text('Color 2:'), 
         sg.Text('R'),sg.InputText('255',size=(3,1),key='R1'), 
         sg.Text('G'),sg.InputText('255',size=(3,1),key='G1'),
         sg.Text('B'),sg.InputText('255',size=(3,1),key='B1'),
         sg.Text('Elevation'),sg.InputText('1000',size=(8,1),key='E1'),
        ],
        [sg.InputText('2',key='row_count',visible=False)],
    ]
    window = sg.Window("TerraGrad", layout)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "add_color":
            r = int(values["row_count"])
            window.extend_layout(window, [[sg.Text('Color ' + str(r+1) + ':'), 
         sg.Text('R'),sg.InputText('255',size=(3,1),key='R'+str(r)), 
         sg.Text('G'),sg.InputText('255',size=(3,1),key='G'+str(r)),
         sg.Text('B'),sg.InputText('255',size=(3,1),key='B'+str(r)),
         sg.Text('Elevation'),sg.InputText('1000',size=(8,1),key='E'+str(r)),
        ]])
            r = r + 1
            window.Element('row_count').update(str(r))
        if event == "color_terrain" or event == "export":

            # Load elevation map
            ter = imageio.imread(values["file_name_ter"])
            
            # Get elevation min and max (for testing or display)
            elev_min = np.min(ter)
            elev_max = np.max(ter)
            
            # List of col and corresponding elevations
            col = []
            r = int(values["row_count"])
            for i in range(r):
                col.append([values["R"+str(i)],values["G"+str(i)],values["B"+str(i)],values["E"+str(i)]])
            col = np.array(col).astype(np.float)
            
            # Unwrap terrain into 1D array for easier vectorization
            ter_ravel = ter.ravel()
            rgb = np.zeros([len(ter_ravel),3])
            im_out = np.zeros([ter.shape[0],ter.shape[1],3])
            
            # Cycle through col
            for i in range(len(col)-1):
                
                start = tuple(col[i,0:3]/255.0)
                end = tuple(col[i+1,0:3]/255.0)
                
                # Elevation at top and bottom of current range
                elev_min = col[i][3]
                elev_max = col[i+1][3]
                
                # Select points between range
                idx = np.nonzero((ter_ravel >= elev_min) & (ter_ravel <= elev_max))
            
                # Interpolate col based on altitude (in RGB space)
                for i in range(3):
                    rgb[idx,i] = map_range_np(ter_ravel[idx],elev_min,elev_max,start[i],end[i])
            
            # Reshape and write back to 2D rgb image
            for i in range(3):
                im_out[:,:,i] = np.reshape(rgb[:,i],ter.shape)
                
            image = Image.fromarray((im_out*255).astype(np.uint8)).resize((400,400))
            # image.thumbnail((400, 400))
            bio = io.BytesIO()
            image.save(bio, format="PNG")
            window["-IMAGE-"].update(data=bio.getvalue())
            
            if event == "export":
                dirname = os.path.dirname(values["file_name_ter"])
                filename = os.path.join(dirname,"color_output.png")
                filename = checkfile(filename)
                imageio.imwrite(filename,im_out)
    window.close()
if __name__ == "__main__":
    main()