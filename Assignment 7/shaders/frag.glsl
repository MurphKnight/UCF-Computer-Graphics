#version 330 core

in vec3 fragNormal;
in vec3 fragPosition;


out vec4 outColor;


uniform vec4 light_pos;
uniform vec3 eye_pos;

uniform vec3 material_color;
uniform vec3 specular_color;

uniform float shininess;
uniform float K_s;
uniform float ambient_intensity;

uniform float dragonType;



void main(){
  // Normalize the normal using normalize() function
  vec3 norm = normalize(fragNormal);

  // Setting up light_dir: (2, 2, 2, 1) for the point light and (2, 2, 2, 0) for the directional light
  vec3 light_dir = normalize(light_pos.xyz);
  if (light_pos[3] == 1)   light_dir = normalize(light_pos.xyz - fragPosition);


  // If its the left dragon
  if ( dragonType == 0 ){

    vec3 color_diffuse_reflection = material_color * clamp(dot(norm, light_dir), 0, 1);

    outColor = vec4(color_diffuse_reflection, 1.0);
  }



  // If its the middle dragon
  else if ( dragonType == 1 ){

    //   fragment_pos is the position of the fragment. eye_pos is the position of the camera
    vec3 view_dir = normalize(eye_pos - fragPosition);
    vec3 half_vector = normalize(light_dir + view_dir);
    vec3 color_specular_reflection = specular_color * pow(clamp(dot(norm, half_vector), 0, 1), shininess);

    outColor = vec4(color_specular_reflection, 1.0);
  }



  // If its the right dragon
  else{

    vec3 color_ambient_light = ambient_intensity * material_color;

    vec3 color_diffuse_reflection = material_color * clamp(dot(norm, light_dir), 0, 1);

    vec3 view_dir = normalize(eye_pos - fragPosition);
    vec3 half_vector = normalize(light_dir + view_dir);
    vec3 color_specular_reflection = specular_color * pow(clamp(dot(norm, half_vector), 0, 1), shininess);

    vec3 color = color_ambient_light + color_diffuse_reflection + K_s * color_specular_reflection;


    outColor = vec4(color, 1.0);
  }
}
