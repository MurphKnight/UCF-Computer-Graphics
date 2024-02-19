# Name: Megan Murphy
# Assignment 8: Toon Shading

# Goal: Toon shading
#   In this assignment, first you will implement diffuse shading. Then, you will implement toon shading.
#   Your program should be able to switch between diffuse shading and toon shading using a radio button.

#######################################################################################################
# Import necessary libraries
import pygame as pg
from OpenGL.GL import *
import numpy as np

from objLoaderV4 import ObjLoader
import shaderLoaderV2
import guiV3
import pyrr.matrix44


# Initialize pygame
pg.init()

# Set up OpenGL context version
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)


# Create a 1280x480 window for graphics using OpenGL
width = 680
height = 480
aspect = width/height   # : This is the aspect ratio of the window.
pg.display.set_mode((width, height), pg.OPENGL | pg.DOUBLEBUF)


# Enable depth testing and scissor testing
glClearColor(0.3, 0.4, 0.5, 1.0)
glEnable(GL_DEPTH_TEST)



# Write shaders (vertex and fragment shaders) and compile them
shaderProgram = shaderLoaderV2.ShaderProgram("shaders/vert.glsl", "shaders/frag.glsl")
glUseProgram(shaderProgram.shader)


# Read the 3D model of the dragon and create three objects
dragon = ObjLoader("objects/dragon.obj")
vertices = np.array(dragon.vertices, dtype="float32")
center = dragon.center
dia = dragon.dia
scale = 2.0/dia





# Useful Methods in ObjloaderV4.py :
#   size_position: size of position coordinates (3)
size_position = dragon.size_position
#   size_texture: size of texture coordinates (2)
size_texture = dragon.size_texture
#   size_normal: size of normal coordinates (3)
size_normal = dragon.size_normal
#   itemsize: size of each item in the vertices array (4 bytes)
itemsize = dragon.itemsize
#   offset_texture: offset of texture coordinates in each vertex (size_position * itemsize)
offset_texture = dragon.offset_texture
#   n_vertices: number of vertices in the object (len(vertices) // (size_position + size_texture + size_normal))
n_vertices = dragon.n_vertices



############################################################################################
############################################################################################
#                         Identity Matrix for the dragon
# Creating a scale matrix
scale_mat = pyrr.matrix44.create_from_scale([scale, scale, scale])

# Distance of the left or right dragon from the center
dist = (dia/2 + dia/8)

# Placing the dragon in the center
translation_mat = pyrr.matrix44.create_from_translation( -center )
model_matrix = pyrr.matrix44.multiply(translation_mat, scale_mat)    # scale * translation


############################################################################################
############################################################################################
#                         Camera variables
# Create a view matrix using the following parameters:
eye = (0, 0, 2)
target = (0, 0, 0) # The camera is looking at the origin.
up = (0, 1, 0)
view_mat = pyrr.matrix44.create_look_at(eye, target, up)

# Create a projection matrix using the following parameters:
fov = 40
near = 0.1
far = 10
projection_mat = pyrr.matrix44.create_perspective_projection_matrix(fov, aspect, near, far)

# Create light and Material
ambient = 0.25 # Ambient intensity
material_color = (1.0, 0.1, 0.1) # Default red

light_pos = np.array([2, 2, 2, None], dtype=np.float32) # light type (0: directional, 1: point) which is changed by radio button



######################################################################################################################
######################################################################################################################
#                         Creating the sliders
# Use the SimpleGUI class from the guiV3.py file to create a slider to change the rotation of the model.
slide_gui = guiV3.SimpleGUI("Assignment 8 Slider")

# Create a slider for the rotation angle around the Y-axis. Range: [-180, 180]. Default: 0
y_slide = slide_gui.add_slider(label_text="Camera Y Angle", min_value=-180.0, max_value=180.0, initial_value=0, resolution=0.01)

# Create a slider for the rotation angle around the X-axis. Range: [-90, 90]. Default: 0
x_slide = slide_gui.add_slider(label_text="Camera X Angle", min_value=-90.0, max_value=90.0, initial_value=0, resolution=0.01)

# Create a slider for the field of view of the camera. Range: [25, 120]. Default: 45
fov_slide = slide_gui.add_slider(label_text="FOV", min_value=25, max_value=120, initial_value=fov, resolution=0.01)


material_color_button = slide_gui.add_color_picker(label_text="Material Color", initial_color=material_color)


light_type_button = slide_gui.add_radio_buttons(label_text="Light Type", options_dict={"point":1, "directional":0}, initial_option="point")
shade_type_button = slide_gui.add_radio_buttons(label_text="Shading Type", options_dict={"Diffuse":0, "Toon Shading":1}, initial_option="Diffuse")


silhouette_checkbox = slide_gui.add_checkbox(label_text="Silhouette", initial_state=False)




######################################################################################################################
###################################################  VAO and VBO  ####################################################
#                         Upload the dragon data to the GPU. Create a VAO and VBO for the dragon.
#    Create a VAO
vao = glGenVertexArrays(1) # Generate a VAO using glGenVertexArrays()
glBindVertexArray(vao)  #Bind that VAO, i.e, make it active using glBindVertexArray()

#   Create a VBO
vbo = glGenBuffers(1) # Generate a buffer using glGenBuffers()
glBindBuffer(GL_ARRAY_BUFFER, vbo) # Bind that buffer (Make that buffer as the active buffer) using glBindBuffer()
glBufferData(GL_ARRAY_BUFFER, dragon.vertices.nbytes, dragon.vertices, GL_STATIC_DRAW) # Upload data to the GPU using glBufferData()

######################################################################################################################
#                         Configure vertex attributes for the dragon
# Get the location of the attributes "position" and "normal" in the shader using glGetAttribLocation()
pos_locat = glGetAttribLocation(shaderProgram.shader, "position")
norm_locat = glGetAttribLocation(shaderProgram.shader, "normal")

#   Specify how the data is stored in the VBO for the position attribute
glVertexAttribPointer(index=pos_locat, size=size_position, type=GL_FLOAT, normalized=GL_FALSE, stride=dragon.stride, pointer=ctypes.c_void_p(dragon.offset_position) )
glEnableVertexAttribArray(pos_locat) # Enable the position attribute

#   Specify how the data is stored in the VBO for the normal attribute
glVertexAttribPointer(index=norm_locat, size=size_position, type=GL_FLOAT, normalized=GL_FALSE, stride=dragon.stride, pointer=ctypes.c_void_p(dragon.offset_normal) )
glEnableVertexAttribArray(norm_locat) # Enable the normal attribute



######################################################################################################################
######################################################################################################################


draw = True
while draw:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            draw = False

    # Get scaler's new values.
    y_val = np.deg2rad(   y_slide.get_value()   )
    x_val = np.deg2rad(   x_slide.get_value()   )
    fov_val = fov_slide.get_value()



    # Translate the camera position by the negative of the center of the scene. This will translate the center of the scene to the origin of the world coordinate system.
    transformed_eye = eye - np.array([0, 0, 0])

    # Rotate the camera position using the rotation matrix.
    rotateY_mat = pyrr.matrix44.create_from_y_rotation(  y_val  )
    rotateX_mat = pyrr.matrix44.create_from_x_rotation(  x_val  )

    # Combine the rotation matrices around the X and Y axes to create a single rotation matrix.
    rotation_mat = pyrr.matrix44.multiply(rotateX_mat, rotateY_mat)    # rotation Y * rotation X

    # Apply the rotation matrix to the camera position.
    rotated_eye = pyrr.matrix44.apply_to_vector(rotation_mat, eye)
    view_mat = pyrr.matrix44.create_look_at(rotated_eye, target, up)

    # Use this new camera position to create the view matrix.
    projection_mat = pyrr.matrix44.create_perspective_projection_matrix(fov_val, aspect, near, far)



    shaderProgram["view_mat"] = view_mat
    shaderProgram["projection_mat"] = projection_mat

    shaderProgram["eye_pos"] = eye

    shaderProgram["material_color"] = material_color_button.get_color()

    light_pos[3] = light_type_button.get_value()
    shaderProgram["light_pos"] = light_pos



    ##################################################   Set up    #######################################################
    # Call glViewport() to set the viewport to the desired region of the window.
    glViewport(0, 0, width, height)
    glClearColor(0.3, 0.4, 0.5, 1.0)
    # Clear the color buffer and depth buffer for the viewport.
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)


    ##################################################   Draw the dragon    ##############################################
    shaderProgram["model_matrix"] = model_matrix

    shade = shade_type_button.get_value()
    shaderProgram["shadeType"] = float(shade)

    if( silhouette_checkbox.get_value() == True ):
        shaderProgram["silhouette"] = 1
    else:
        shaderProgram["silhouette"] = 0


    glBindVertexArray(vao)  # Bind the correct VAO
    glDrawArrays(GL_TRIANGLES, 0, dragon.n_vertices)  # Draw the object with glDrawArrays().



    ####################################################################################################################
    ####################################################################################################################
    # Refresh the display to show what's been drawn
    pg.display.flip()


##############################################################################################
# Cleanup
glDeleteVertexArrays(1, [vao])
glDeleteBuffers(1, [vbo])
glDeleteProgram(shaderProgram.shader)

pg.quit()   # Close the graphics window
quit()      # Exit the program
