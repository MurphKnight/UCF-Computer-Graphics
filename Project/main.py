# Name: Megan Murphy
# Terrain Generation Project
#######################################################################################################
# Import necessary libraries
import pygame as pg
from OpenGL.GL import *
import numpy as np
import pyrr.matrix44
import random

import shaderLoaderV3
import guiV3
import TerrainFunctions



# Initialize pygame
pg.init()

# Set up OpenGL context version
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)


# Create a window for graphics using OpenGL
width = 1200 #1280 # 980
height = 480
aspect = width/height   # : This is the aspect ratio of the window.
pg.display.set_mode((width, height), pg.OPENGL | pg.DOUBLEBUF)


# Enable depth testing and scissor testing
glClearColor(0.3, 0.4, 0.5, 1.0)
glEnable(GL_DEPTH_TEST)



# Write shaders (vertex and fragment shaders) and compile them
shaderProgram = shaderLoaderV3.ShaderProgram("shaders/vert.glsl", "shaders/frag.glsl")
glUseProgram(shaderProgram.shader)




print("\nRunning\t ... main.py \t ...\n")


# Nummber of square
num_squares = 20
current_noise = 2


# Create initial Terrain object from TerrainFunctions using 20 squares and noiseType random
quad_vertices = TerrainFunctions.create_terrain(squares=num_squares, noiseType=current_noise)



# Establish window parameters based on the quad's size
center = (-num_squares/(10*2), 0, -num_squares/(10*2)) #(-0.5, 0, -0.5)
dia = 2
scale = 2.0/dia



# Vairables about the Terrain object:
size_position = 3 #     size of position coordinates
size_texture = 0 #      size of texture coordinates
size_normal = 3 #       size of normal coordinates
itemsize = 4 #          size of each item in the vertices array (4 bytes)

stride = (size_position + size_normal) * itemsize
offset_position = 0
offset_texture = size_position * itemsize #   offset of texture coordinates in each vertex (size_position * itemsize)
n_vertices = len(quad_vertices) // (size_position + size_texture + size_normal) # number of vertices in the object



############################################################################################
############################################################################################
#                         Identity Matrix for plane
# Creating the inital matrices for the terrain

scale_matrix = pyrr.matrix44.create_from_scale([scale, scale, scale])
translation_matrix = pyrr.matrix44.create_from_translation( center )
model_matrix = pyrr.matrix44.multiply(  translation_matrix, scale_matrix  )


############################################################################################
############################################################################################
#                         Camera variables
# Create a view matrix using the following parameters:
eye = (0, 0, 3) # The camera is located 3 units away from the origin along the positive z-axis.
target = (0, 0, 0) # The camera is looking at the origin.
up = (0, 1, 0)
view_mat = pyrr.matrix44.create_look_at(eye, target, up)

# Create a projection matrix using the following parameters:
fov = 30
near = 0.1
far = 20
projection_mat = pyrr.matrix44.create_perspective_projection_matrix(fov, aspect, near, far)


# Start the camera slightly rotated on the x-axis
initial_x_rotation = 20

######################################################################################################################
######################################################################################################################
#                         Creating the sliders
# Use the SimpleGUI class from the guiV3.py file to create a sliders and radio buttons.
slide_gui = guiV3.SimpleGUI("Terrain Generation")

# Create a slider for the rotations
y_slide = slide_gui.add_slider(label_text="Camera Y Angle", min_value=-180.0, max_value=180.0, initial_value=0, resolution=0.01)
x_slide = slide_gui.add_slider(label_text="Camera X Angle", min_value=-90.0, max_value=90.0, initial_value=initial_x_rotation, resolution=0.01)

# Create a slider for the camera.
fov_slide = slide_gui.add_slider(label_text="FOV", min_value=10, max_value=100, initial_value=fov, resolution=0.01)
camera_position = slide_gui.add_slider(label_text="Z position of Camera", min_value=3, max_value=10, initial_value=3, resolution=1.0)


squares_slide = slide_gui.add_slider(label_text="Number of Squares", min_value=10, max_value=100, initial_value=num_squares, resolution=10.0)
radio_button = slide_gui.add_radio_buttons(label_text="Noise Type", options_dict={"Flat":0, "Random": 1,"Perlin": 2,"Billow": 3,"Ridged": 4}, initial_option="Random")



######################################################################################################################
#                         Upload the Terrain Object data to the GPU. Create a VAO and VBO for the Terrain Object.
# Create a VAO for the terrain
vao = glGenVertexArrays(1)
glBindVertexArray(vao)

# Create a VBO
vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, GL_STATIC_DRAW)


######################################################################################################################
#                         Configure vertex attributes for Terrain Object
# Get the location of the attributes "position" and "normal" in the shader using glGetAttribLocation()
position_loc = 0
normal_loc = 1

# Specify how the data is stored in the VBO for the postion attributes
glVertexAttribPointer(index=position_loc, size=size_position, type=GL_FLOAT, normalized=GL_FALSE, stride=stride, pointer=ctypes.c_void_p(offset_position) )
glEnableVertexAttribArray(position_loc)

# Specify how the data is stored in the VBO for the normal attribute
glVertexAttribPointer(index=normal_loc, size=size_normal, type=GL_FLOAT, normalized=GL_FALSE, stride=stride, pointer=ctypes.c_void_p(offset_texture) )
glEnableVertexAttribArray(normal_loc)


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
    eye = (0, 0, camera_position.get_value())


    # Translate the camera position by the negative of the center of the scene. This will translate the center of the scene to the origin of the world coordinate system.
    transformed_eye = eye - np.array([0, 0, 0])

    # Rotate the camera position using the rotation matrix.
    rotateY_mat = pyrr.matrix44.create_from_y_rotation(  y_val  )
    rotateX_mat = pyrr.matrix44.create_from_x_rotation(  x_val  )

    # Combine the rotation matrices around the X and Y axes to create a single rotation matrix.
    rotation_mat = pyrr.matrix44.multiply(rotateX_mat, rotateY_mat)    # rotation Y * rotation X

    # Apply the rotation matrix to the camera position.
    rotated_eye = pyrr.matrix44.apply_to_vector(rotation_mat, transformed_eye)
    view_mat = pyrr.matrix44.create_look_at(rotated_eye, target, up)

    # Use this new camera position to create the view matrix.
    projection_mat = pyrr.matrix44.create_perspective_projection_matrix(fov_val, aspect, near, far)


    shaderProgram["view_mat"] = view_mat
    shaderProgram["projection_mat"] = projection_mat


    ##################################################   Set up    #######################################################
    # Call glViewport() to set the viewport to the desired region of the window.
    glViewport(0, 0, width, height)
    glClearColor(0.3, 0.4, 0.5, 1.0)

    # Clear the color buffer and depth buffer for the viewport.
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)


    #########################################################################################################
    # If the button for noise type isn't the same as the current noise type
    if (   (int(radio_button.get_value()) != current_noise)   or   (squares_slide.get_value() != num_squares)   ):
        current_noise = int(radio_button.get_value())
        num_squares = squares_slide.get_value()

        # Create new Terrain object from TerrainFunctions using NEW squares and NEW noiseType
        quad_vertices = TerrainFunctions.create_terrain(squares=num_squares, noiseType=current_noise)

        # Establish new center based on the quad's size
        center = (-num_squares/(10*2), 0, -num_squares/(10*2))


        scale_matrix = pyrr.matrix44.create_from_scale([scale, scale, scale])
        translation_matrix = pyrr.matrix44.create_from_translation( center )
        model_matrix = pyrr.matrix44.multiply(  translation_matrix, scale_matrix  )

        n_vertices = len(quad_vertices) // (size_position + size_texture + size_normal) # number of vertices in the object

        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, GL_STATIC_DRAW)

    #########################################################################################################
    shaderProgram["model_matrix"] = model_matrix

    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLES, 0, n_vertices)



    ####################################################################################################################
    ####################################################################################################################
    # Refresh the display to show what's been drawn
    pg.display.flip()

print("\n\n\n\n\n")
print("end of main.py")

##############################################################################################
# Cleanup
glDeleteVertexArrays(1, [vao])
glDeleteBuffers(1, [vbo])
glDeleteProgram(shaderProgram.shader)


pg.quit()   # Close the graphics window
quit()      # Exit the program
