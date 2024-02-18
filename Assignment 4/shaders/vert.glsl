#version 330 core

//Declare "position" and "normal" as input attributes
in vec3 position;
in vec3 normal;


uniform mat4 model_matrix;
uniform float aspect;


//Declare "fragNormal" as output variable. We will use this variable to pass the normal to the fragment shader
out vec3 fragNormal;


void main(){
  // Transform the position from object space (a.k.a model space) to clip space. The range of clip space is [-1,1] in all 3 dimensions.
  vec4 pos = model_matrix * vec4(position, 1.0);
  pos.x = pos.x / aspect;

  // Assign the position to gl_Position
  gl_Position = pos;

  // Transform the normal from object (or model) space to world space
  mat4 normal_matrix = transpose(  inverse( model_matrix )  );
  vec3 new_normal = (  normal_matrix * vec4(normal,0)  ).xyz;

  //Assign the new normal to the output variable "fragNormal"
  fragNormal = normalize(new_normal);
}
