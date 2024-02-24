#version 330 core

//  Declare "position" and "normal" as input attributes
in vec3 position;
in vec3 normal;

//  Declare uniform variables
uniform mat4 model_matrix;
uniform mat4 view_mat;
uniform mat4 projection_mat;

//  Declare "fragNormal" as output variable. We will use this variable to pass the normal to the fragment shader
out vec3 fragNormal;
out vec3 fragPosition;


void main(){
  // Transformation
  vec4 pos = model_matrix * vec4(position, 1.0);

  //Assign the position to gl_Position
  gl_Position = projection_mat * view_mat * pos;

  //Assign the normalized normal to the output variable "fragNormal"
  fragNormal = normalize(normal);
  fragPosition = pos.xyz;

}
