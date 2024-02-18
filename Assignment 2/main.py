# Assignment 2: Getting Ready for OpenGL Programming
# Name: Megan Murphy
#######################################################################################################
# Import necessary libraries
import pygame as pg
from OpenGL.GL import *
import numpy as np

# Initialize pygame
pg.init()

# Set up OpenGL context version
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)

# Create a window for graphics using OpenGL
width = 640
height = 480
pg.display.set_mode((width, height), pg.OPENGL | pg.DOUBLEBUF)

#######################################################################################################
# Todo: Part 1
# Set the background color (clear color)
# glClearColor takes 4 arguments: red, green, blue, alpha. Each argument is a float between 0 and 1.
glClearColor(1.0, 0.0, 0.0, 1.0)


# Todo: Part 2
from objLoaderV1 import ObjLoader

object = ObjLoader('objects/raymanModel.obj')
print("\n\nDimension of v: ", object.v.shape)
print("Dimension of vt: ", object.vt.shape)
print("Dimension of vn: ", object.vn.shape)
print("Dimension of vertices: ", object.vertices.shape)



# Todo: Part 3
def findMin(v):
    min = v[0]
    for ind in v:
    # Check for Min.
        if min[0] > ind[0]:
            min[0] = ind[0]
        if min[1] > ind[1]:
            min[1] = ind[1]
        if min[2] > ind[2]:
            min[2] = ind[2]
    return min

def findMax(v):
    max = v[0]
    for ind in v:
    # Check for Min.
        if max[0] < ind[0]:
            max[0] = ind[0]
        if max[1] < ind[1]:
            max[1] = ind[1]
        if max[2] < ind[2]:
            max[2] = ind[2]
    return max

def printMinMaxCenterDiameter(v):
    min = np.copy(findMin(v))
    max = np.copy(findMax(v))
    print("Min: ", min)
    print("Max: ", max)

    x = (min[0] + max[0])/2
    y = (min[1] + max[1])/2
    z = (min[2] + max[2])/2

    center = [round(x,8), round(y,8), round(z,8)]
    print("Center: ", center)

    diameter = [max[0]-min[0], max[1]-min[1], max[2]-min[2]]
    print("Diameter: ", diameter)

printMinMaxCenterDiameter(object.v)



# Todo: Part 4
#Generate a buffer using glGenBuffers()
vbo = glGenBuffers(1)
#Bind the buffer using glBindBuffer()
glBindBuffer(GL_ARRAY_BUFFER, vbo)
#Upload the "vertices" data by using glBufferData().
glBufferData(GL_ARRAY_BUFFER, object.vertices.nbytes, object.vertices, GL_STATIC_DRAW)

# Cleanup
glDeleteBuffers(1, [vbo])

#######################################################################################################
# Run a loop to keep the program running
draw = True
while draw:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            draw = False

    # Clear the screen (or clear the color buffer), and set it to the background color chosen earlier
    glClear(GL_COLOR_BUFFER_BIT)

    # Refresh the display to show what's been drawn
    pg.display.flip()


pg.quit()   # Close the graphics window
quit()      # Exit the program
