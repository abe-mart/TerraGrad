import streamlit as st
import numpy as np
from numpy import interp
import imageio
from PIL import ImageColor
import io

# Initialization
if 'firstRun' not in st.session_state:
    st.session_state['firstRun'] = True

# Install EXR support on first run
if st.session_state['firstRun']:
    imageio.plugins.freeimage.download()
    st.session_state['firstRun'] = False

# Define linear interpolation function
def map_range_np(value, leftMin, leftMax, rightMin, rightMax):
    return interp(value,[leftMin,leftMax],[rightMin,rightMax])

uploaded_file = st.file_uploader("Choose terrain file...", type="exr",accept_multiple_files=False)


if uploaded_file is not None:
    # st.write('Got a file')
    # file_name_ter = "terrain.exr"
    ter = imageio.imread(uploaded_file)
    
    # Get elevation min and max (for testing or display)
    elev_min = np.min(ter)
    elev_max = np.max(ter)
    # st.write(elev_min)
    # st.write(type(elev_min))
    # st.write(elev_max)
    
    # Unwrap terrain into 1D array for easier vectorization
    ter_ravel = ter.ravel()
    rgb = np.zeros([len(ter_ravel),3])
    im_out = np.zeros([ter.shape[0],ter.shape[1],3])
    
    c = []
    ev = []
    N = int(st.number_input('Number of Colors',3))
    for i in range(N):
        c.append(ImageColor.getcolor(st.color_picker('Color '+str(i)), "RGB"))
        ev.append(st.slider('Elevation '+str(i),float(elev_min),float(elev_max)))
 
    # Cycle through colors
    for i in range(len(c)-1):
        
        start = tuple(np.array(c[i])/255.0)
        end = tuple(np.array(c[i+1])/255.0)
        # st.write(start)
        # st.write(end)
        
        # Elevation at top and bottom of current range
        elev_min = ev[i]
        elev_max = ev[i+1]
        
        # Select points between range
        idx = np.nonzero((ter_ravel >= elev_min) & (ter_ravel <= elev_max))
    
        # Interpolate colors based on altitude (in RGB space)
        for i in range(3):
            rgb[idx,i] = map_range_np(ter_ravel[idx],elev_min,elev_max,start[i],end[i])
    
    # Reshape and write back to 2D rgb image
    for i in range(3):
        im_out[:,:,i] = np.reshape(rgb[:,i],ter.shape)
        
    # st.write(np.mean(im_out))
    st.image(im_out)
    
    temp = io.BytesIO()
    imageio.imwrite(temp,im_out,format='PNG')
    st.download_button('Download Image',data=temp,file_name='terrain_colors.png',mime="image/png")
    
# N = int(st.number_input('How Many?',0))

# rows = []
# for i in range(N):
#     rows.append(st.color_picker('Color ' +str(i)))