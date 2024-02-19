#version 330 core

//Declare "fragNormal" as input variable (This is the output variable from the vertex shader)
in vec3 fragNormal;

//Declare "outColor" as output variable.
out vec4 outColor;


void main(){
  // Normalize the normal using normalize() function
  vec3 norm = normalize(fragNormal);

  // For this assignment, you may simply take the absolute value of the normal, OR add 1.0 to each component of the normal, and divide each component by 2.
  norm = (   (norm + 1.0)  /  2   );

  // Assign the color to "outColor"
  outColor = vec4(norm, 1.0);
}
