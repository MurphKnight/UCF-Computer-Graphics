# Assignment 5: Camera.
# Name: Megan Murphy
#######################################################################################################
# Import necessary libraries
import pygame as pg
from OpenGL.GL import *
import numpy as np

from objLoaderV3 import ObjLoader
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
obj = ObjLoader("objects/dragon.obj")
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
aspect = width/height   # : This is the aspect ratio of the window. Set it to width/height, where width and height are the width and height of the window



############################################################################################
# Identity Matrix
# Its a 4x4 model matrix
# No applying any transformations to the model (no translation, scaling or rotation). The rotation sliders are for the camera rotation around the Y and X axis.
model_matrix = pyrr.matrix44.create_identity()



############################################################################################
# Camera variables
eye = (0, 0, dia) # Initially, Set the eye to be dia distance away from the center of the scene along the Z axis.
lookat_pos = center # Set the target to be the center of the scene.
up = (0, 1, 0) # Set the up vector to be [0, 1, 0].

# Create a 4x4 view matrix to transform the scene from world space to camera (view) space.
# The function takes the eye (camera position), target (lookat position), and up vectors of the camera as input parameters.
view_mat = pyrr.matrix44.create_look_at(eye, lookat_pos, up)


fov = 30
near = 0.1 #Set the near plane to be 0.1.
far = 1000 #Set the far plane to be 1000.
# Create a 4x4 projection matrix to define the perspective projection
# The function takes the field of view, aspect ratio, and near and far planes as parameters.
projection_mat = pyrr.matrix44.create_perspective_projection_matrix(fov, aspect, near, far)




######################################################################################################################
# Creating the sliders

# Use the SimpleGUI class from the guiV1.py file to create a slider to change the rotation of the model.
slide_gui = guiV1.SimpleGUI("Assignment 5 Slider")


# Create a slider for the rotation angle around the Y-axis.
# Set the initial value to 0. Set the minimum value to -180 and the maximum value to 180.
y_slide = slide_gui.add_slider(label_text="Rotate Y", min_value=-180.0, max_value=180.0, initial_value=0, resolution=0.01)

# Create a slider for the rotation angle around the X-axis.
# Set the initial value to 0. Set the minimum value to -90 and the maximum value to 90.
x_slide = slide_gui.add_slider(label_text="Rotate X", min_value=-90.0, max_value=90.0, initial_value=0, resolution=0.01)


# Create a slider for the field of view of the camera. You can choose any appropriate range you want for the field of view slider.
# Example: initial value: 45, Min: 20, Max 120
fov_slide = slide_gui.add_slider(label_text="FOV", min_value=20, max_value=120, initial_value=fov, resolution=0.01)




######################################################################################################################
# Upload the model data to the GPU. Create a VAO and VBO for the model data.
#    Create a VAO
vao = glGenVertexArrays(1)  #Generate a VAO using glGenVertexArrays()
glBindVertexArray(vao)  #Bind that VAO, i.e, make it active using glBindVertexArray()

#   Create a VBO
vbo = glGenBuffers(1)  #Generate a buffer using glGenBuffers()
glBindBuffer(GL_ARRAY_BUFFER, vbo)  #Bind that buffer (Make that buffer as the active buffer) using glBindBuffer()
glBufferData(GL_ARRAY_BUFFER, obj.vertices.nbytes, obj.vertices, GL_STATIC_DRAW)  #Finally, upload data to the GPU using glBufferData()



######################################################################################################################
#    Configure vertex attributes
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

view_mat_loc = glGetUniformLocation(shader, "view_mat")

projection_mat_loc = glGetUniformLocation(shader, "projection_mat")



######################################################################################################################
# Run a loop to keep the program running
# The view matrix and projection matrix will be updated every frame in the main loop since the camera position and fov will change interactively.
draw = True
while draw:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            draw = False

    # Clear color buffer and depth buffer before drawing each frame
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)


    # Get scaler's new values.
    y_val = np.deg2rad(   y_slide.get_value()   )
    x_val = np.deg2rad(   x_slide.get_value()   )
    fov_val = fov_slide.get_value()

    # Rotate the camera around the center of the scene, you can do the following:
    # Translate the camera position by the negative of the center of the scene. This will translate the center of the scene to the origin of the world coordinate system.
    transformed_eye = eye - center

    # Rotate the camera position using the rotation matrix. Combine the rotation matrices around the X and Y axes to create a single rotation matrix.
    rotateY_mat = pyrr.matrix44.create_from_y_rotation(  y_val  )
    rotateX_mat = pyrr.matrix44.create_from_x_rotation(  x_val  )
    rotation_mat = pyrr.matrix44.multiply(rotateX_mat, rotateY_mat)    # rotation Y * rotation X


    # Once you have the rotation matrix, you can use pyrr.matrix44.apply_to_vector() to apply the rotation matrix to the camera position.
    rotated_eye = pyrr.matrix44.apply_to_vector(rotation_mat, transformed_eye)

    view_mat = pyrr.matrix44.create_look_at(rotated_eye, lookat_pos, up)

    # Then, use this new camera position to create the view matrix.
    projection_mat = pyrr.matrix44.create_perspective_projection_matrix(fov_val, aspect, near, far)

    # Use glUniformMatrix4fv() to pass the model matrix to the vertex shader.
    glUniformMatrix4fv(model_matrix_locat, 1, GL_FALSE, model_matrix)
    glUniformMatrix4fv(view_mat_loc, 1, GL_FALSE, view_mat)
    glUniformMatrix4fv(projection_mat_loc, 1, GL_FALSE, projection_mat)


    # Use the shader program using glUseProgram()
    glUseProgram(shader)
    # Bind the VAO using glBindVertexArray()
    glBindVertexArray(vao)
    # Draw the triangle using glDrawArrays()
    glDrawArrays(GL_TRIANGLES, 0, n_vertices)


    # Refresh the display to show what's been drawn
    pg.display.flip()



# Cleanup
glDeleteVertexArrays(1, [vao]) # to delete the VAO
glDeleteBuffers(1, [vbo]) # to delete the VBO
glDeleteProgram(shader) # to delete the shader program

pg.quit()   # Close the graphics window
quit()      # Exit the program
