# Assignment 4: Transformations.
# Name: Megan Murphy
#######################################################################################################
# Import necessary libraries
import pygame as pg
from OpenGL.GL import *
import numpy as np

from objLoaderV2 import ObjLoader
import shaderLoader
import guiV1
import pyrr.matrix44


# Initialize pygame
pg.init()

# Set up OpenGL context version
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)


# Create a window for graphics using OpenGL
width = 640
height = 480
pg.display.set_mode((width, height), pg.OPENGL | pg.DOUBLEBUF)


glClearColor(0.3, 0.4, 0.5, 1.0)
# Todo: Enable depth testing here using glEnable()
glEnable(GL_DEPTH_TEST)



# Write shaders (vertex and fragment shaders) and compile them
shader = shaderLoader.compile_shader("shaders/vert.glsl", "shaders/frag.glsl")
glUseProgram(shader)



# Read the 3D model by setting up scene geometry.
obj = ObjLoader("objects/raymanModel.obj")
vertices = np.array(obj.vertices, dtype="float32")
center = obj.center
dia = obj.dia


# Defining the vertex attributes  # vertices = [ x,y,z, u,v, xn,yn,zn,    x,y,z, u,v, xn,yn,zn,   ...]
size_position = 3   # number of components per vertex for position data
size_texture = 2   # number of components per vertex for texture data
size_normal = 3   # number of components per vertex for normal data

# Defining the offsets
stride = (size_position  +  size_texture  +  size_normal) * 4   # number of bytes between each vertex
offset_position = 0   # offset of the position data
offset_texture = (size_position) * 4   # offset of the texture data (We won't be using texture data in this assignment)
offset_normal = (size_position  +  size_texture) * 4   # offset of the normal data
n_vertices = len(obj.vertices) // (size_position  +  size_texture  +  size_normal)   # number of vertices

# Other variables needed: scale, center, and aspect
scale = 2.0/dia   # : This is the scale factor for the model. Set it to 2.0/dia, where dia is the diameter of the model
center = center   # : This is the center of the 3D model that you load.
aspect = width/height   # t: This is the aspect ratio of the window. Set it to width/height, where width and height are the width and height of the window



# Create a 4x4 translation matrix to translate the object to the origin of the world coordinate system.
# - Use pyrr.matrix44.create_from_translation() to create the translation matrix. This function takes the translation vector as input.
# - The translation vector is -center, where center is the center of the model.
translation_mat = pyrr.matrix44.create_from_translation(-center)

# Create a 4x4 scaling matrix to scale the object to fit the window.
# - Use pyrr.matrix44.create_from_scale() to create the scaling matrix. This function takes the scale factor as input.
# - The scale factor is 2/dia, where dia is the diameter of the model.
scale_mat = pyrr.matrix44.create_from_scale([scale, scale, scale])



# Use the SimpleGUI class from the guiV1.py file to create a slider to change the rotation of the model.
slide_gui = guiV1.SimpleGUI("Assignment 4 Slider")

# Create a slider for the rotation angle around the Z axis. Set the initial value to 0. Set the minimum value to -90 and the maximum value to 90.
z_slide = slide_gui.add_slider(label_text="Rotate Z", min_value=-90.0, max_value=90.0, initial_value=0, resolution=0.01)

# Create a slider for the rotation angle around the Y axis.
# But, Set the initial value to 0. Set the minimum value to -180 and the maximum value to 180.
y_slide = slide_gui.add_slider(label_text="Rotate Y", min_value=-180.0, max_value=180.0, initial_value=0, resolution=0.01)

# Create a slider for the rotation angle around the X axis.
# But, Set the initial value to 0. Set the minimum value to -90 and the maximum value to 90.
x_slide = slide_gui.add_slider(label_text="Rotate X", min_value=-90.0, max_value=90.0, initial_value=0, resolution=0.01)




# Upload the model data to the GPU. Create a VAO and VBO for the model data.
#    Create a VAO
vao = glGenVertexArrays(1)  #Generate a VAO using glGenVertexArrays()
glBindVertexArray(vao)  #Bind that VAO, i.e, make it active using glBindVertexArray()

#   Create a VBO
vbo = glGenBuffers(1)  #Generate a buffer using glGenBuffers()
glBindBuffer(GL_ARRAY_BUFFER, vbo)  #Bind that buffer (Make that buffer as the active buffer) using glBindBuffer()
glBufferData(GL_ARRAY_BUFFER, obj.vertices.nbytes, obj.vertices, GL_STATIC_DRAW)  #Finally, upload data to the GPU using glBufferData()





#    Configure vertex attributes using the variables defined in Part 1
# Get the location of the attributes "position" and "normal" in the shader using glGetAttribLocation()
pos_locat = glGetAttribLocation(shader, "position")
norm_locat = glGetAttribLocation(shader, "normal")

#   Specify how the data is stored in the VBO for the position attribute using glVertexAttribPointer()
glVertexAttribPointer(index=pos_locat, size=size_position, type=GL_FLOAT, normalized=GL_FALSE, stride=stride, pointer=ctypes.c_void_p(offset_position) )
#   Enable the position attribute using glEnableVertexAttribArray()
glEnableVertexAttribArray(pos_locat)

#   Specify how the data is stored in the VBO for the normal attribute using glVertexAttribPointer()
glVertexAttribPointer(index=norm_locat, size=size_position, type=GL_FLOAT, normalized=GL_FALSE, stride=stride, pointer=ctypes.c_void_p(offset_normal) )
#   Enable the normal attribute using glEnableVertexAttribArray()
glEnableVertexAttribArray(norm_locat)




#    Configure uniform variables.
# Get the location of the uniform variable in the vertex shader using glGetUniformLocation().
model_matrix_locat = glGetUniformLocation(shader, "model_matrix")

# Get the location of the uniform variable in the vertex shader using glGetUniformLocation().
aspec_locat = glGetUniformLocation(shader, "aspect")
# Use glUniform1f() to pass the aspect ratio to the vertex shader. This function takes the location of the uniform variable and the aspect ratio as input.
glUniform1f(aspec_locat, aspect)





# Run a loop to keep the program running
draw = True
while draw:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            draw = False

    # Clear color buffer and depth buffer before drawing each frame
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)


    # Get scaler's new value and use np.deg2rad() to convert degrees to radians.
    z_val = np.deg2rad(   z_slide.get_value()   )
    y_val = np.deg2rad(   y_slide.get_value()   )
    x_val = np.deg2rad(   x_slide.get_value()   )


    # Set the NEW value of the uniform variable for model_matrix
    rotateZ_mat = pyrr.matrix44.create_from_z_rotation(  z_val  )
    rotateY_mat = pyrr.matrix44.create_from_y_rotation(  y_val  )
    rotateX_mat = pyrr.matrix44.create_from_x_rotation(  x_val  )

    # model_matrix = scale_mat * rotateZ_mat * rotateY_mat * rotateX_mat * translation_mat
    model_matrix = pyrr.matrix44.multiply(translation_mat, rotateX_mat)    # rotation X * translation
    model_matrix = pyrr.matrix44.multiply(model_matrix, rotateY_mat)    # rotation Y * rotation X * translation
    model_matrix = pyrr.matrix44.multiply(model_matrix, rotateZ_mat)
    model_matrix = pyrr.matrix44.multiply(model_matrix, scale_mat)


    # Use the shader program using glUseProgram()
    glUseProgram(shader)
    # Bind the VAO using glBindVertexArray()
    glBindVertexArray(vao)
    # Draw the triangle using glDrawArrays()
    glDrawArrays(GL_TRIANGLES, 0, n_vertices)

    # Use glUniformMatrix4fv() to pass the model matrix to the vertex shader.
    glUniformMatrix4fv(model_matrix_locat, 1, GL_FALSE, model_matrix)

    # Refresh the display to show what's been drawn
    pg.display.flip()



# Cleanup
glDeleteVertexArrays(1, [vao]) # to delete the VAO
glDeleteBuffers(1, [vbo]) # to delete the VBO
glDeleteProgram(shader) # to delete the shader program

pg.quit()   # Close the graphics window
quit()      # Exit the program
