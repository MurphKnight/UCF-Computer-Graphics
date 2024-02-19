#version 330 core

in vec3 fragNormal;

out vec4 outColor;


void main(){
  // Normalize the normal using normalize() function
  vec3 norm = normalize(fragNormal);
  norm = abs(norm);

  // Assign the color to "outColor"
  outColor = vec4(norm, 1.0);
}
