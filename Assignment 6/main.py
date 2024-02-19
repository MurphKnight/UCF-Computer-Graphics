# Assignment 6: Multi-Viewport
# Name: Megan Murphy
#######################################################################################################
# Import necessary libraries
import pygame as pg
from OpenGL.GL import *
import numpy as np

from objLoaderV4 import ObjLoader
import shaderLoader
import guiV1
import pyrr.matrix44


# Initialize pygame
pg.init()

# Set up OpenGL context version
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)


# Create a 1280x480 window for graphics using OpenGL
width = 640
height = 480
aspect = width/height   # : This is the aspect ratio of the window.
# Double the width of the display so their is enough space to display both objects
pg.display.set_mode((width*2, height), pg.OPENGL | pg.DOUBLEBUF)


# Enable depth testing and scissor testing
glClearColor(0.3, 0.4, 0.5, 1.0)
glEnable(GL_DEPTH_TEST)
glEnable(GL_SCISSOR_TEST)



# Write shaders (vertex and fragment shaders) and compile them
w_shader = shaderLoader.compile_shader("shaders/vert.glsl", "shaders/w_frag.glsl")
c_shader = shaderLoader.compile_shader("shaders/vert.glsl", "shaders/c_frag.glsl")

glUseProgram(w_shader)
glUseProgram(c_shader)



# Read the 3D model of the wolf.
wolf = ObjLoader("objects/wolf.obj")
w_vertices = np.array(wolf.vertices, dtype="float32")
w_center = wolf.center
w_dia = wolf.dia
w_scale = 2.0/w_dia


# Read the 3D model of the cat.
cat = ObjLoader("objects/cat.obj")
c_vertices = np.array(cat.vertices, dtype="float32")
c_center = cat.center
c_dia = cat.dia
c_scale = 2.0/c_dia



# Useful Methods in ObjloaderV4.py :
#   size_position: size of position coordinates (3)
size_position = wolf.size_position
#   size_texture: size of texture coordinates (2)
size_texture = wolf.size_texture
#   size_normal: size of normal coordinates (3)
size_normal = wolf.size_normal
#   itemsize: size of each item in the vertices array (4 bytes)
itemsize = wolf.itemsize
#   offset_texture: offset of texture coordinates in each vertex (size_position * itemsize)
offset_texture = wolf.offset_texture
#   n_vertices: number of vertices in the object (len(vertices) // (size_position + size_texture + size_normal))
n_vertices = wolf.n_vertices




############################################################################################
#                         Identity Matrix
# Create a model matrix for each object.
w_model_matrix = pyrr.matrix44.create_identity()
c_model_matrix = pyrr.matrix44.create_identity()


# The model matrix should translate the object to the origin and scale the object to fit in the range [-1, 1] along all three axes.
# You can use "-center" as translation vector and "2/dia" as scale factor
w_translation_mat = pyrr.matrix44.create_from_translation(-w_center)
c_translation_mat = pyrr.matrix44.create_from_translation(-c_center)

w_scale_mat = pyrr.matrix44.create_from_scale([w_scale, w_scale, w_scale])
c_scale_mat = pyrr.matrix44.create_from_scale([c_scale, c_scale, c_scale])


# Creating the wolf model_matrix with the translation and scale matrices
w_model_matrix = pyrr.matrix44.multiply(w_translation_mat, w_scale_mat)    # scale * translation

# Creating the cat model_matrix like the wolf but also using a rotation to fix the model's orignal rotation
rotateX_mat = pyrr.matrix44.create_from_x_rotation(  np.deg2rad(90)  )
c_model_matrix = pyrr.matrix44.multiply(c_translation_mat, rotateX_mat)    # rotateX_mat * translation
c_model_matrix = pyrr.matrix44.multiply(c_model_matrix, c_scale_mat)    # scale_mat * rotateX_mat * translation_mat



############################################################################################
#                         Camera variables
# Create a view matrix using the following parameters:
eye = (0, 0, 2) # The camera is located 2 units away from the origin along the positive z-axis.
target = (0, 0, 0) # The camera is looking at the origin.
up = (0, 1, 0)
view_mat = pyrr.matrix44.create_look_at(eye, target, up) # Create a 4x4 view matrix to transform the scene from world space to camera (view) space.

# Create a projection matrix using the following parameters:
fov = 45
near = 0.1
far = 10
projection_mat = pyrr.matrix44.create_perspective_projection_matrix(fov, aspect, near, far)




######################################################################################################################
#                         Creating the sliders
# Use the SimpleGUI class from the guiV1.py file to create a slider to change the rotation of the model.
slide_gui = guiV1.SimpleGUI("Assignment 6 Slider")

# Create a slider for the rotation angle around the Y-axis. Range: [-180, 180]. Default: 0
y_slide = slide_gui.add_slider(label_text="Camera Y Angle", min_value=-180.0, max_value=180.0, initial_value=0, resolution=0.01)

# Create a slider for the rotation angle around the X-axis. Range: [-90, 90]. Default: 0
x_slide = slide_gui.add_slider(label_text="Camera X Angle", min_value=-90.0, max_value=90.0, initial_value=0, resolution=0.01)

# Create a slider for the field of view of the camera. Range: [25, 120]. Default: 45
fov_slide = slide_gui.add_slider(label_text="FOV", min_value=25, max_value=120, initial_value=fov, resolution=0.01)



######################################################################################################################
######################################################################################################################
#                         Upload the wolf data to the GPU. Create a VAO and VBO for the wolf.
#    Create a VAO
w_vao = glGenVertexArrays(1) # Generate a VAO using glGenVertexArrays()
glBindVertexArray(w_vao)  #Bind that VAO, i.e, make it active using glBindVertexArray()

#   Create a VBO
w_vbo = glGenBuffers(1) # Generate a buffer using glGenBuffers()
glBindBuffer(GL_ARRAY_BUFFER, w_vbo) # Bind that buffer (Make that buffer as the active buffer) using glBindBuffer()
glBufferData(GL_ARRAY_BUFFER, wolf.vertices.nbytes, wolf.vertices, GL_STATIC_DRAW) # Upload data to the GPU using glBufferData()



######################################################################################################################
#                         Configure vertex attributes from wolf's shader
# Get the location of the attributes "position" and "normal" in the w_shader using glGetAttribLocation()
w_pos_locat = glGetAttribLocation(w_shader, "position")
w_norm_locat = glGetAttribLocation(w_shader, "normal")

#   Specify how the data is stored in the VBO for the position attribute
glVertexAttribPointer(index=w_pos_locat, size=size_position, type=GL_FLOAT, normalized=GL_FALSE, stride=wolf.stride, pointer=ctypes.c_void_p(wolf.offset_position) )
glEnableVertexAttribArray(w_pos_locat) # Enable the position attribute

#   Specify how the data is stored in the VBO for the normal attribute
glVertexAttribPointer(index=w_norm_locat, size=size_position, type=GL_FLOAT, normalized=GL_FALSE, stride=wolf.stride, pointer=ctypes.c_void_p(wolf.offset_normal) )
glEnableVertexAttribArray(w_norm_locat) # Enable the normal attribute



######################################################################################################################
######################################################################################################################
#                         Upload the cat data to the GPU. Create a VAO and VBO for the cat.
#    Create a VAO
c_vao = glGenVertexArrays(1) # Generate a VAO using glGenVertexArrays()
glBindVertexArray(c_vao)  #Bind that VAO, i.e, make it active using glBindVertexArray()

#   Create a VBO
c_vbo = glGenBuffers(1) # Generate a buffer using glGenBuffers()
glBindBuffer(GL_ARRAY_BUFFER, c_vbo) # Bind that buffer (Make that buffer as the active buffer) using glBindBuffer()
glBufferData(GL_ARRAY_BUFFER, cat.vertices.nbytes, cat.vertices, GL_STATIC_DRAW) # Upload data to the GPU using glBufferData()




######################################################################################################################
#                         Configure vertex attributes from cat's shader
# Get the location of the attributes "position" and "normal" in the c_shader using glGetAttribLocation()
c_pos_locat = glGetAttribLocation(c_shader, "position")
c_norm_locat = glGetAttribLocation(c_shader, "normal")

#   Specify how the data is stored in the VBO for the position attribute
glVertexAttribPointer(index=c_pos_locat, size=size_position, type=GL_FLOAT, normalized=GL_FALSE, stride=cat.stride, pointer=ctypes.c_void_p(cat.offset_position) )
glEnableVertexAttribArray(c_pos_locat) # Enable the position attribute

#   Specify how the data is stored in the VBO for the normal attribute
glVertexAttribPointer(index=c_norm_locat, size=size_position, type=GL_FLOAT, normalized=GL_FALSE, stride=cat.stride, pointer=ctypes.c_void_p(cat.offset_normal) )
glEnableVertexAttribArray(c_norm_locat) # Enable the normal attribute



######################################################################################################################
######################################################################################################################
#                          Configure uniform variables for both wolf and cat.
# Wolf
w_model_matrix_locat = glGetUniformLocation(w_shader, "model_matrix")
w_view_mat_loc = glGetUniformLocation(w_shader, "view_mat")
w_projection_mat_loc = glGetUniformLocation(w_shader, "projection_mat")

# Cat
c_model_matrix_locat = glGetUniformLocation(c_shader, "model_matrix")
c_view_mat_loc = glGetUniformLocation(c_shader, "view_mat")
c_projection_mat_loc = glGetUniformLocation(c_shader, "projection_mat")



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
    rotated_eye = pyrr.matrix44.apply_to_vector(rotation_mat, transformed_eye)

    view_mat = pyrr.matrix44.create_look_at(rotated_eye, target, up)

    # Use this new camera position to create the view matrix.
    projection_mat = pyrr.matrix44.create_perspective_projection_matrix(fov_val, aspect, near, far)




    ##################################################   Wolf    #######################################################
    # Call glViewport() to set the viewport to the desired region of the window.
    glViewport(0, 0, width, height)
    # Set the scissor region to the desired region of the window. The scissor region should be the same as the viewport region.
    glScissor(0, 0, width, height)

    # Clear color for the viewport. Set the clear color to different values for each viewport.
    glClearColor(0.3, 0.4, 0.5, 1.0)
    # Clear the color buffer and depth buffer for the viewport.
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)


    # Draw the object in the viewport.
    glUseProgram(w_shader)

    w_model_matrix_locat = glGetUniformLocation(w_shader, "model_matrix")

    glUniformMatrix4fv(w_model_matrix_locat, 1, GL_FALSE, w_model_matrix)
    glUniformMatrix4fv(w_view_mat_loc, 1, GL_FALSE, view_mat)
    glUniformMatrix4fv(w_projection_mat_loc, 1, GL_FALSE, projection_mat)

    glBindVertexArray(w_vao)  # Bind the correct VAO
    glDrawArrays(GL_TRIANGLES, 0, wolf.n_vertices)  # Draw the object with glDrawArrays().



    ####################################################################################################################
    ##################################################   Cat    ########################################################
    # Call glViewport() to set the viewport to the desired region of the window.
    glViewport(width, 0, width, height)
    # Set the scissor region to the desired region of the window. The scissor region should be the same as the viewport region.
    glScissor(width, 0, width, height)

    # Clear color for the viewport. Set the clear color to different values for each viewport.
    glClearColor(0.3, 0.4, 0.5, 1.0)
    # Clear the color buffer and depth buffer for the viewport.
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)


    # Draw the object in the viewport.
    glUseProgram(c_shader)

    c_model_matrix_locat = glGetUniformLocation(c_shader, "model_matrix")

    glUniformMatrix4fv(c_model_matrix_locat, 1, GL_FALSE, c_model_matrix)
    glUniformMatrix4fv(c_view_mat_loc, 1, GL_FALSE, view_mat)
    glUniformMatrix4fv(c_projection_mat_loc, 1, GL_FALSE, projection_mat)

    glBindVertexArray(c_vao)  # Bind the correct VAO
    glDrawArrays(GL_TRIANGLES, 0, cat.n_vertices)  # Draw the object with glDrawArrays().


    ####################################################################################################################
    # Refresh the display to show what's been drawn
    pg.display.flip()


##############################################################################################
# Cleanup
glDeleteVertexArrays(1, [w_vao])
glDeleteVertexArrays(1, [c_vao])

glDeleteBuffers(1, [w_vbo])
glDeleteBuffers(1, [c_vbo])

glDeleteProgram(w_shader)
glDeleteProgram(c_shader)

pg.quit()   # Close the graphics window
quit()      # Exit the program
