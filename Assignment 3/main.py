# Assignment 3: OpenGL Programming: Simple rendering.
# Name: Megan Murphy
#######################################################################################################
# Import necessary libraries
import pygame as pg
from OpenGL.GL import *
import numpy as np

from objLoaderV2 import ObjLoader
import shaderLoader
import guiV1


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



# Todo: Part 3: Write shaders (vertex and fragment shaders) and compile them here
#   Use the shaderLoader.py file to compile the shaders.
shader = shaderLoader.compile_shader("shaders/vert.glsl", "shaders/frag.glsl")
#   Use the compile_shader() function to compile the shaders.
glUseProgram(shader)



# Todo: Part 1: Read the 3D model
# Lets setup our scene geometry.
obj = ObjLoader("objects/raymanModel.obj")
vertices = np.array(obj.vertices, dtype="float32")
center = obj.center
dia = obj.dia


# Defining the vertex attributes used Part 4
#   vertices = [ x,y,z, u,v, xn,yn,zn,    x,y,z, u,v, xn,yn,zn,   ...]
size_position = 3   # number of components per vertex for position data
size_texture = 2   # number of components per vertex for texture data (We won't be using texture data in this assignment, but texture data is usually 2D (u, v))
size_normal = 3   # number of components per vertex for normal data

# defining offsets
stride = (size_position  +  size_texture  +  size_normal) * 4   # number of bytes between each vertex
offset_position = 0   # offset of the position data
offset_texture = (size_position) * 4   # offset of the texture data (We won't be using texture data in this assignment)
offset_normal = (size_position  +  size_texture) * 4   # offset of the normal data
n_vertices = len(obj.vertices) // (size_position  +  size_texture  +  size_normal)   # number of vertices

# Other variables needed: scale, center, and aspect
scale = 2.0/dia   # : This is the scale factor for the model. Set it to 2.0/dia, where dia is the diameter of the model
center = center   # : This is the center of the 3D model that you load.
aspect = width/height   # t: This is the aspect ratio of the window. Set it to width/height, where width and height are the width and height of the window





# Todo: Part 2: Upload the model data to the GPU. Create a VAO and VBO for the model data.
#    Create a VAO
vao = glGenVertexArrays(1)  #Generate a VAO using glGenVertexArrays()
glBindVertexArray(vao)  #Bind that VAO, i.e, make it active using glBindVertexArray()

#   Create a VBO
vbo = glGenBuffers(1)  #Generate a buffer using glGenBuffers()
glBindBuffer(GL_ARRAY_BUFFER, vbo)  #Bind that buffer (Make that buffer as the active buffer) using glBindBuffer()
glBufferData(GL_ARRAY_BUFFER, obj.vertices.nbytes, obj.vertices, GL_STATIC_DRAW)  #Finally, upload data to the GPU using glBufferData()





# Todo: Part 4: Configure vertex attributes using the variables defined in Part 1
#   Get the location of the attributes "position" and "normal" in the shader using glGetAttribLocation()
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




# Todo: Part 5: Configure uniform variables.
#   Get the location of the uniform variables 'scale', 'center', and 'aspect' from the shader using glGetUniformLocation()
scal_locat = glGetUniformLocation(shader, "scale")
cent_locat = glGetUniformLocation(shader, "center")
aspec_locat = glGetUniformLocation(shader, "aspect")

# Set the value of the uniform variable 'scale' using glUniform1f()
glUniform1f(scal_locat, scale)
# Set the value of the uniform variable 'center' using glUniform3f() or glUniform3fv(). Note the number of components for the center is 3.
glUniform3fv(cent_locat, 1, center) # i tried using 3 but it throw an error
# Set the value of the uniform variable 'aspect' using glUniform1f()
glUniform1f(aspec_locat, aspect)



# Todo: Part 6: Do the final rendering. In the rendering loop, do the following:
    # Clear the color buffer and depth buffer before drawing each frame using glClear()
    # Use the shader program using glUseProgram()
    # Bind the VAO using glBindVertexArray()
    # Draw the triangle using glDrawArrays()


# Bonus (optional), 1 extra point for completion (no partial points):
# Use the SimpleGUI class from the guiV1.py file to create a slider to change the scale of the model.
slide_gui = guiV1.SimpleGUI("Assignment 3 Slider")

# Set the minimum value of the slider to 0.5*scale and the maximum value to 2.0*scale. You can set the initial value to scale.
active_slide = slide_gui.add_slider(label_text="Scale", min_value=scale*0.5, max_value=scale*2.0, initial_value=scale, resolution=0.01)
active_slide_val = active_slide.get_value()



# Run a loop to keep the program running
draw = True
while draw:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            draw = False

    # Clear color buffer and depth buffer before drawing each frame
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)

    # Use the shader program using glUseProgram()
    glUseProgram(shader)
    # Bind the VAO using glBindVertexArray()
    glBindVertexArray(vao)
    # Draw the triangle using glDrawArrays()
    glDrawArrays(GL_TRIANGLES, 0, n_vertices)

    # Get scaler's new value
    active_slide_val = active_slide.get_value()
    # Set the NEW value of the uniform variable for scale
    glUniform1f(scal_locat, active_slide_val)


    # Refresh the display to show what's been drawn
    pg.display.flip()



# Cleanup
glDeleteVertexArrays(1, [vao]) # to delete the VAO
glDeleteBuffers(1, [vbo]) # to delete the VBO
glDeleteProgram(shader) # to delete the shader program

pg.quit()   # Close the graphics window
quit()      # Exit the program
