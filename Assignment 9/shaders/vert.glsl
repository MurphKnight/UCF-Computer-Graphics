#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec2 uv;
layout (location = 2) in vec3 color;


uniform mat4 model_matrix;
uniform mat4 view_mat;
uniform mat4 projection_mat;

out vec3 fragNormal;
out vec3 fragPosition;

out vec2 fragUV;
out vec3 fragColor;

void main(){

  // For position attribute
  vec4 pos = projection_mat * view_mat * model_matrix * vec4(position, 1.0);
  gl_Position = pos;



  // For normal attribute
  fragPosition = (model_matrix * vec4(position, 1.0)).xyz;

  mat4 normal_matrix = transpose(  inverse( model_matrix )  );
  vec3 new_normal = (  normal_matrix * vec4(color,0)  ).xyz;
  fragNormal = normalize(new_normal);



  fragUV = uv;
  fragColor = color;
}
