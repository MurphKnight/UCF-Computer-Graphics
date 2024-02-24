import numpy as np
import pyrr.matrix44
import random
from perlin_noise import PerlinNoise



#####################################################################################################################
# Radio Button value: 0
def inital_plane(squares):
    quad_vertices = []

    for row in range(squares): # rows
        for z in range(squares): # column
            unit = 0.1      # The length of each square
            left = row/10     # The left most x-value of the triangle
            down = z/10     # The top most z-value of the triangle

            #             R     G      B
            red_normal = [1,    0,     0] # The top left triangle is red
            blue_normal = [0,    0,     1] # The bottom right triangle is blue

            # Left triangle
            quad_vertices.extend( [left,          0,          down] ) # Top left point of  Left triangle
            quad_vertices.extend( red_normal )
            quad_vertices.extend( [left,         0,       down+unit] ) # Bottom left point of  Left triangle
            quad_vertices.extend( red_normal )
            quad_vertices.extend( [left+unit,     0,       down] ) # Top right point of  Left triangle
            quad_vertices.extend( red_normal )


            # Right triangle
            quad_vertices.extend( [left,         0,        down+unit] ) # Bottom left point of left triangle
            quad_vertices.extend( blue_normal )
            quad_vertices.extend( [left+unit,     0,      down+unit] ) # Bottom left point of left triangle
            quad_vertices.extend( blue_normal )
            quad_vertices.extend( [left+unit,     0,        down] ) # Top left point of left triangle
            quad_vertices.extend( blue_normal )

    quad_vertices = tuple(quad_vertices)

    quad_vertices = np.array(quad_vertices, dtype=np.float32)
    return quad_vertices


#####################################################################################################################
# Radio Button value: 1
random_range = 1

def random_values_map(squares):
    print("\n\n random_values_map()")
    random_values = []

    for x in range(squares+1):
        row = []
        for y in range(squares+1):
            row.append(  random.randint(-random_range, random_range) / 10  )
        random_values.append(row)

    print(random_values)
    return random_values


#####################################################################################################################
# Radio Button value: 2
noise = PerlinNoise(octaves=10, seed=1)

def perlin_values_map(squares):
    print("\n\n perlin_values_map()")
    perlin_map = []
    for x in range(squares+1):
        row = []
        for y in range(squares+1):
            row.append(    noise([x/(squares+1), y/(squares+1)])    )
        perlin_map.append(row)

    print(perlin_map)
    return perlin_map


#####################################################################################################################
# Radio Button value: 3
def billow_values_map(squares):
    print("\n\n billow_values_map()")
    perlin_map = []
    for x in range(squares+1):
        row = []
        for y in range(squares+1):
            row.append(    abs(noise([x/(squares+1), y/(squares+1)]))    )
        perlin_map.append(row)

    print(perlin_map)
    return perlin_map


#####################################################################################################################
# Radio Button value: 4
def ridged_values_map(squares):
    print("\n\n ridged_values_maps()")
    perlin_map = []
    for x in range(squares+1):
        row = []
        for y in range(squares+1):
            row.append(    0.5 - abs(noise([x/(squares+1), y/(squares+1)]))    )
        perlin_map.append(row)

    print(perlin_map)
    return perlin_map


#####################################################################################################################

def create_terrain(squares, noiseType):
    map = []
    if (noiseType == 0):
        return inital_plane(squares)
    elif (noiseType == 1):
        map = random_values_map(squares)
    elif (noiseType == 2):
        map = perlin_values_map(squares)
    elif (noiseType == 3):
        map = billow_values_map(squares)
    else:
        map = ridged_values_map(squares)

    quad_vertices = []

    for row in range(squares): # rows
        for z in range(squares): # column
            unit = 0.1      # The length of each square
            left = row/10     # The left most x-value of the triangle
            down = z/10     # The top most z-value of the triangle

            #           x               y                               z
            first = [left,          map[row][z],          down] # Top left point of  Left triangle
            second = [left,         map[row][z+1],       down+unit] # Bottom left point of  Left triangle
            third = [left+unit,     map[row+1][z],       down] # Top right point of  Left triangle
            cross_array = np.cross(np.subtract(second, first), np.subtract(third, first))

            quad_vertices.extend(first)
            quad_vertices.extend( cross_array/np.linalg.norm(cross_array) )

            quad_vertices.extend(second)
            quad_vertices.extend( cross_array/np.linalg.norm(cross_array) )

            quad_vertices.extend(third)
            quad_vertices.extend( cross_array/np.linalg.norm(cross_array) )


            #           x               y                               z
            fourth = [left,         map[row][z+1],        down+unit] # Bottom left point of left triangle
            fifth = [left+unit,     map[row+1][z+1],      down+unit] # Bottom left point of left triangle
            sixth = [left+unit,     map[row+1][z],        down] # Top left point of left triangle
            cross_array = np.cross(np.subtract(fourth,fifth), np.subtract(fourth,sixth))

            quad_vertices.extend(fourth)
            quad_vertices.extend( cross_array/np.linalg.norm(cross_array) )

            quad_vertices.extend(fifth)
            quad_vertices.extend( cross_array/np.linalg.norm(cross_array) )

            quad_vertices.extend(sixth)
            quad_vertices.extend( cross_array/np.linalg.norm(cross_array) )


    quad_vertices = tuple(quad_vertices)

    quad_vertices = np.array(quad_vertices, dtype=np.float32)
    return quad_vertices
