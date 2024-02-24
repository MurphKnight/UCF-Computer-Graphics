#version 330 core

//Declare "fragNormal" as input variable (This is the output variable from the vertex shader)
in vec3 fragNormal;
in vec3 fragPosition;

//Declare "outColor" as output variable.
out vec4 outColor;


void main(){
  // Normalize the normal using normalize() function
  vec3 norm = normalize(fragNormal);
  norm = (   (norm + 1.0)  /  2   );

  // Assign the color to "outColor"
  outColor = vec4(norm, 1.0);
}
