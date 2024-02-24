# Name: Megan Murphy

# Assignment 9: Textures

# Goal: Texture mapping and environment mapping
#   In this assignment, you will learn how to map a texture to a 3D object and how to use a cubemap texture for environment mapping.
#   Your program should be able to render the object with the following texture types:
#    - 2D texture                                    (5 points)
#    - Environment mapping using a cubemap texture   (4 points)
#    - Mix of 2D texture and environment mapping     (1 point)
# Additionally, you will learn how to render a skybox using the cubemap texture.  (Optional: 1 point bonus)

#######################################################################################################
# Import necessary libraries
import pygame as pg
from OpenGL.GL import *
import numpy as np
import pyrr.matrix44

from objLoaderV4 import ObjLoader
import shaderLoaderV3
import guiV3
from utils import load_image


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
shaderProgram = shaderLoaderV3.ShaderProgram("shaders/vert.glsl", "shaders/frag.glsl")
glUseProgram(shaderProgram.shader)


# Read the 3D model of the stormtrooper and create three objects
storm = ObjLoader("objects/stormtrooper.obj")
vertices = np.array(storm.vertices, dtype="float32")
center = storm.center
dia = storm.dia
scale = 2.0/dia





# Useful Methods in ObjloaderV4.py :
#   size_position: size of position coordinates (3)
size_position = storm.size_position
#   size_texture: size of texture coordinates (2)
size_texture = storm.size_texture
#   size_normal: size of normal coordinates (3)
size_normal = storm.size_normal
#   itemsize: size of each item in the vertices array (4 bytes)
itemsize = storm.itemsize
#   offset_texture: offset of texture coordinates in each vertex (size_position * itemsize)
offset_texture = storm.offset_texture
#   n_vertices: number of vertices in the object (len(vertices) // (size_position + size_texture + size_normal))
n_vertices = storm.n_vertices



############################################################################################
############################################################################################
#                         Identity Matrix for the stormtrooper
# Creating a scale matrix
scale_mat = pyrr.matrix44.create_from_scale([scale, scale, scale])

# Placing the stormtrooper in the center
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
fov = 52
near = 0.1
far = 10
projection_mat = pyrr.matrix44.create_perspective_projection_matrix(fov, aspect, near, far)



######################################################################################################################
######################################################################################################################
#                         Creating the sliders
slide_gui = guiV3.SimpleGUI("Assignment 9 Slider")

# Create a slider for the rotation angles
y_slide = slide_gui.add_slider(label_text="Camera Y Angle", min_value=-180.0, max_value=180.0, initial_value=0, resolution=0.01)
x_slide = slide_gui.add_slider(label_text="Camera X Angle", min_value=-90.0, max_value=90.0, initial_value=0, resolution=0.01)

# Create a slider for the field of view of the camera. Range: [25, 120]. Default: 45
fov_slide = slide_gui.add_slider(label_text="FOV", min_value=25, max_value=120, initial_value=fov, resolution=0.01)

# Create radio buttons to switch between the three texture types
texture_type_button = slide_gui.add_radio_buttons(label_text="Texture Type:", options_dict={"Environment Mapping":0, "2D Texture":1, "Mix":2}, initial_option="2D Texture")



######################################################################################################################
###################################################  VAO and VBO  ####################################################
#                         Upload the stormtrooper data to the GPU. Create a VAO and VBO for the stormtrooper.
#    Create a VAO
vao = glGenVertexArrays(1) # Generate a VAO using glGenVertexArrays()
glBindVertexArray(vao)  #Bind that VAO, i.e, make it active using glBindVertexArray()

#   Create a VBO
vbo = glGenBuffers(1) # Generate a buffer using glGenBuffers()
glBindBuffer(GL_ARRAY_BUFFER, vbo) # Bind that buffer (Make that buffer as the active buffer) using glBindBuffer()
glBufferData(GL_ARRAY_BUFFER, storm.vertices.nbytes, storm.vertices, GL_STATIC_DRAW) # Upload data to the GPU using glBufferData()

######################################################################################################################
#                         Define the vertex attributes for the stormtrooper

#   Position attribute
pos_loc = 0
glBindAttribLocation(shaderProgram.shader, pos_loc, "position")
glVertexAttribPointer(index=pos_loc, size=size_position, type=GL_FLOAT, normalized=GL_FALSE, stride=storm.stride, pointer=ctypes.c_void_p(storm.offset_position) )
glEnableVertexAttribArray(pos_loc) # Enable the position attribute

#   Texture attribute
text_loc = 1
glBindAttribLocation(shaderProgram.shader, text_loc, "uv")
glVertexAttribPointer(index=text_loc, size=2, type=GL_FLOAT, normalized=GL_FALSE, stride=storm.stride, pointer=ctypes.c_void_p(storm.offset_texture) )
glEnableVertexAttribArray(text_loc)

#   Normal attribute
normal_loc = 2
glBindAttribLocation(shaderProgram.shader, normal_loc, "color")
glVertexAttribPointer(index=normal_loc, size=3, type=GL_FLOAT, normalized=GL_FALSE, stride=storm.stride, pointer=ctypes.c_void_p(storm.offset_normal) )
glEnableVertexAttribArray(normal_loc)



######################################################################################################################
############################################## Create a 2D texture ###################################################
#       Load the texture image.
img_data, img_w, img_h = load_image("objects/stormtrooper.jpg", flip=True)

#       Generate a texture ID using glGenTextures()
text_id = glGenTextures(1)

#       Bind the texture as a 2D texture using glBindTexture()
glBindTexture(GL_TEXTURE_2D, text_id)

#       Set the texture wrapping and filtering parameters using glTexParameteri()
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_NEAREST)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

#       Upload the texture data to the GPU using glTexImage2D()
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img_w, img_h, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

#       Optionally, generate mipmaps using glGenerateMipmap(). If you do this, also set the minification filter in step 4) to any of the mipmapping filters (e.g. GL_LINEAR_MIPMAP_NEAREST)
glGenerateMipmap(GL_TEXTURE_2D)


################################################# Texture Unit #######################################################
# Attach the sampler variable to the same texture unit using shaderProgram["tex2D"] = 0
shaderProgram["tex2D"] = 0

# Attach the texture object to a texture unit using glActiveTexture() and glBindTexture()
glActiveTexture(GL_TEXTURE0)
glBindTexture(GL_TEXTURE_2D, text_id)




######################################################################################################################
################################################# Cubemap Texture #####################################################

cubemap_names = ["skybox/right.png", "skybox/left.png", "skybox/top.png", "skybox/bottom.png", "skybox/front.png", "skybox/back.png"]
faces_num = [GL_TEXTURE_CUBE_MAP_POSITIVE_X, GL_TEXTURE_CUBE_MAP_NEGATIVE_X, GL_TEXTURE_CUBE_MAP_POSITIVE_Y, GL_TEXTURE_CUBE_MAP_NEGATIVE_Y, GL_TEXTURE_CUBE_MAP_POSITIVE_Z, GL_TEXTURE_CUBE_MAP_NEGATIVE_Z]


#        2) Generate a texture ID using glGenTextures()
cube_id = glGenTextures(1)

#        3) Bind the texture as a cubemap using glBindTexture()
glBindTexture(GL_TEXTURE_CUBE_MAP, cube_id)


for ind in range(6):
    img_data, img_w, img_h = load_image(cubemap_names[ind], flip=False) # 1) Load the cubemap images.
    glTexImage2D(faces_num[ind], 0, GL_RGB, img_w, img_h, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data) # 5) Upload the texture data to the GPU using glTexImage2D()


#        4) Set the texture wrapping and filtering parameters using glTexParameteri()
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_NEAREST)
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

#        5) Upload the texture data to the GPU using glTexImage2D()
#        6) Optionally, generate mipmaps using glGenerateMipmap(). If you do this, also set the minification filter in step 4) to any of the mipmapping filters (e.g. GL_LINEAR_MIPMAP_NEAREST)
glGenerateMipmap(GL_TEXTURE_CUBE_MAP)

# Unbind the texture
#glBindTexture(GL_TEXTURE_CUBE_MAP, 0)

################################################# Cubemap Unit #######################################################
# Attach the sampler variable to the same texture unit
shaderProgram["cubeMapTex"] = 1

# Attach the texture object to a texture unit using glActiveTexture() and glBindTexture()
glActiveTexture(GL_TEXTURE1)
glBindTexture(GL_TEXTURE_CUBE_MAP, cube_id)



######################################################################################################################
##################################################### Skybox #########################################################
# Create a proxy geometry for the skybox.
# A window sized quad: 2 triangles covering the whole clip box(with coordinates -1 to +1 in x, -1 to +1 in y)
sky_vertices = ( -1, -1,    1, -1,    1,  1,          1,  1,   -1,  1,   -1, -1 )

######################################################################################################################
################################################# Cubemap Texture #####################################################


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
    shaderProgram["eyePostion"] = rotated_eye



    ##################################################   Set up    #######################################################
    # Call glViewport() to set the viewport to the desired region of the window.
    glViewport(0, 0, width, height)
    glClearColor(0.3, 0.4, 0.5, 1.0)

    # Clear the color buffer and depth buffer for the viewport.
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)



    ##################################################   Draw the stormtrooper    ##############################################
    # Choose texture types
    shaderProgram["texture_type"] = int(  texture_type_button.get_value()  )

    shaderProgram["model_matrix"] = model_matrix


    glBindVertexArray(vao)  # Bind the correct VAO
    glDrawArrays(GL_TRIANGLES, 0, storm.n_vertices)  # Draw the object with glDrawArrays().


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
