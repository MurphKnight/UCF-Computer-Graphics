#version 330 core

//Declare "position" and "normal" as input attributes
in vec3 position;
in vec3 normal;

//Declare "scale", "center", and "aspect" as uniform variables
uniform float scale;
uniform vec3 center;
uniform float aspect;

//Declare "fragNormal" as output variable. We will use this variable to pass the normal to the fragment shader
out vec3 fragNormal;


void main(){
  // Write the code to transform the position of the vertex: first, translate the vertex by -center, then scale it by scale, then divide the x coordinate by aspect
  vec3 p = position-center;
  p = p * scale;
  p[0] = p[0] / aspect;
  p[2] = p[2] * (-1);

  //Assign the position to gl_Position
  gl_Position = vec4(p, 1.0);

  //Assign the normalized normal to the output variable "fragNormal"
  fragNormal = normalize(normal);
}
