#version 330 core

in vec3 position;
in vec3 normal;

uniform mat4 model_matrix;
uniform mat4 view_mat;
uniform mat4 projection_mat;

out vec3 fragNormal;
out vec3 fragPosition;


void main(){

  // For position attribute, transform the position of the vertex by the model, view, and projection matrices.
  vec4 pos = projection_mat * view_mat * model_matrix * vec4(position, 1.0);

  // Assign the position to gl_Position
  gl_Position = pos;


  // For normal attribute, transform the normal of the vertex by using the transpose of the inverse of the model matrix
  mat4 normal_matrix = transpose(  inverse( model_matrix )  );
  vec3 new_normal = (  normal_matrix * vec4(normal,0)  ).xyz;


  fragNormal = normalize(new_normal);
  fragPosition = (model_matrix * vec4(position, 1.0)).xyz;
}
