import streamlit as st
import numpy as np
# from numpy import interp
import imageio
# from PIL import ImageColor
import io
# import os
# from numba import jit
# import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import cv2 as cv
from cmapy import colorize

st.set_page_config(page_title='TerraGrad',layout='wide')

# Initialization
if 'firstRun' not in st.session_state:
    st.session_state['firstRun'] = True
if 'c' not in st.session_state:
    st.session_state['c'] = [[0,0,0],[255,255,255]]


# Install EXR support on first run
if st.session_state['firstRun']:
    imageio.plugins.freeimage.download()
    st.session_state['firstRun'] = False
    
# @st.cache(ttl=60)
def read_image(uploaded_file):
    im = imageio.imread(uploaded_file)
    im = cv.normalize(im,None,0,255,cv.NORM_MINMAX,cv.CV_8U)
    return im

def update_image(c,ev,elev_max,elev_min):
    colors = c.copy()
    elevs = ev.copy()
    # Pad colors if needed
    if elevs[-1] < elev_max:
        colors.append(colors[-1])
        elevs.append(elev_max)
    if elevs[0] > elev_min:
        colors.insert(0,colors[0])
        elevs.insert(0,elev_min)
    nodes = np.interp(elevs,[elev_min,elev_max],[0,1])
    st.write(nodes)
    
    cmap = LinearSegmentedColormap.from_list("mycmap",list(zip(nodes,colors)))
    st.write('Hi!')
    
    im_color = colorize(ter,cmap,True)
    
    st.image(im_color)
    
st.title('Welcome to TerraGrad')
st.write('Upload a terrain file (.exr), pick colors and elevations, and TerraGrad will produce a gradient map. Elevations can be added in any order.')
    
uploaded_file = st.file_uploader("Choose terrain file...", type="exr",accept_multiple_files=False)
    
column1,column2,column3 = st.columns([0.1,0.4,0.5])


# with column1:
    
    
if uploaded_file is not None:
    # st.write('Got a file')
    # file_name_ter = "terrain.exr"
    ter = read_image(uploaded_file)
    # st.write(ter.shape)
    
    # Get elevation min and max (for testing or display)
    elev_min = np.min(ter)
    elev_max = np.max(ter)
    # st.write(elev_min)
    # st.write(type(elev_min))
    # st.write(elev_max)
    
    if 'ev' not in st.session_state:
        st.session_state['ev'] = [elev_min,elev_max]
        
    # def delete_color(i):
    #     del st.session_state['c'][i]
    #     del st.session_state['ev'][i]
        
    # def add_color():
    #     st.session_state['c'].append([255,255,255])
    #     st.session_state['ev'].append(elev_max)
    #     st.write('Adding color')
    with column1:
        if st.button('Add color',key='add'):
            st.session_state['c'].append('#FFFFFF')
            st.session_state['ev'].append(elev_max)
            st.write('Adding color')
    with column2:
        export = st.button('Export')
        if export:
            st.write('See download button below')
    
    c = st.session_state['c']
    ev = st.session_state['ev']
    # N = int(st.number_input('Number of Colors',3))
    # with st.form(key='color_form'):
    for i in range(len(c)):
        # col1, col2 = st.columns([0.1,0.9])
        with column1:
            # hx = '#%02x%02x%02x' % tuple(c[i])
            c[i] = st.color_picker('Color '+str(i+1))
            st.write('')
        with column2:
            ev[i] = (st.slider('Elevation '+str(i+1),float(elev_min),float(elev_max)))
            # ev[i] = st.number_input('Elevation '+str(i),float())
        # submit_button = st.form_submit_button(label='Update',on_click=update_image,args=(c,ev,elev_max,elev_min))
    
    
    
    
    # if submit_button:
    colors = c.copy()
    elevs = ev.copy()
    # st.write('Colors')
    # colors
    # st.write('Elevs')
    # elevs
    zipped_lists = zip(elevs, colors)
    sorted_pairs = sorted(zipped_lists)
    
    tuples = zip(*sorted_pairs)
    elevs, colors = [ list(tuple) for tuple in  tuples]
    # colors, elevs = zip(*sorted(zip(colors, elevs)))
    # colors = list(colors)
    # elevs = list(elevs)

    # Pad colors if needed
    # elevs[-1]
    if elevs[-1] < elev_max:
        colors.append(colors[-1])
        elevs.append(elev_max)
        # elev_max
    if elevs[0] > elev_min:
        colors.insert(0,colors[0])
        elevs.insert(0,elev_min)
    # colors
    # elevs
    nodes = np.interp(elevs,[elev_min,elev_max],[0,1])
    # st.write(nodes)
    
    cmap = LinearSegmentedColormap.from_list("mycmap",list(zip(nodes,colors)))
    # st.write('Hi!')
    
    im_color = colorize(ter,cmap,True)
        
    with column3:
        st.image(im_color)
     
    if export:
        temp = io.BytesIO()
        imageio.imwrite(temp,im_color,format='PNG')
        # st.write('Make sure to wait for app to finish running before downloading!')
        st.download_button('Download Image',data=temp,file_name='terrain_colors.png',mime="image/png")
        # fig = plt.figure()
        # plt.imshow(ter,cmap=cmap)
        # st.write(fig)
        

    
    # im_out = process_terrain(ter,c,ev)
    # # Unwrap terrain into 1D array for easier vectorization
    # ter_ravel = ter.ravel()
    # rgb = np.zeros([len(ter_ravel),3])
    # im_out = np.zeros([ter.shape[0],ter.shape[1],3])
 
    # # Cycle through colors
    # for i in range(len(c)-1):
        
    #     start = tuple(np.array(c[i])/255.0)
    #     end = tuple(np.array(c[i+1])/255.0)
    #     # st.write(start)
    #     # st.write(end)
        
    #     # Elevation at top and bottom of current range
    #     elev_min = ev[i]
    #     elev_max = ev[i+1]
        
    #     # Select points between range
    #     idx = np.nonzero((ter_ravel >= elev_min) & (ter_ravel <= elev_max))
    
    #     # Interpolate colors based on altitude (in RGB space)
    #     for i in range(3):
    #         rgb[idx,i] = map_range_np(ter_ravel[idx],elev_min,elev_max,start[i],end[i])
    
    # # Reshape and write back to 2D rgb image
    # for i in range(3):
    #     im_out[:,:,i] = np.reshape(rgb[:,i],ter.shape)
        
    # st.write(np.mean(im_out))
    # st.image(im_out)
    
    # temp = io.BytesIO()
    # imageio.imwrite(temp,im_out,format='PNG')
    # st.write('Make sure to wait for app to finish running before downloading!')
    # st.download_button('Download Image',data=temp,file_name='terrain_colors.png',mime="image/png")
    
# N = int(st.number_input('How Many?',0))

# rows = []
# for i in range(N):
#     rows.append(st.color_picker('Color ' +str(i)))