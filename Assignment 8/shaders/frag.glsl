#version 330 core

in vec3 fragNormal;
in vec3 fragPosition;


out vec4 outColor;


uniform vec4 light_pos;
uniform vec3 eye_pos;

uniform vec3 material_color;

uniform float shadeType;
uniform float silhouette;



void main(){
  // Normalize the normal using normalize() function
  vec3 norm = normalize(fragNormal);

  // Setting up light_dir: (2, 2, 2, 1) for the point light and (2, 2, 2, 0) for the directional light
  vec3 light_dir = normalize(light_pos.xyz);
  if (light_pos[3] == 1)   light_dir = normalize(light_pos.xyz - fragPosition);



  // Default diffuse shading
  if ( shadeType == 0 ){

    vec3 color_diffuse_reflection = material_color * clamp(dot(norm, light_dir), 0, 1);

    outColor = vec4(color_diffuse_reflection, 1.0);
  }



  // Toon shading 1
  else if ( shadeType == 1 ){
    // 1. Compute the diffuse intensity of the light source using the dot product between the light direction and the fragment normal.
    float intensity_dot = dot( light_dir, fragNormal );


    // 2. Divide the intensity into n levels (an example with 5 levels is shown below)
    float intensity = 1;
    if ( intensity_dot <= 0.85   &&   intensity_dot >= 0.5 )
      intensity = 0.7;
    else if ( intensity_dot <= 0.5   &&   intensity_dot >= 0.25 )
      intensity = 0.5;
    else if ( intensity_dot <= 0.25   &&   intensity_dot >= 0.1 )
      intensity = 0.3;
    else if ( intensity_dot <= 0.1 )
      intensity = 0.1;

    // 3. Multiply the intensity with the material color to get the final color of the fragment.
    vec3 color = material_color * intensity;

    outColor = vec4(color, 1.0);

    // Silhouette edge is checked
    if ( silhouette == 1 ) {
      vec3 view_dir = normalize(eye_pos - fragPosition);
      if (   dot(fragNormal, view_dir) < 0.2   ){
        vec3 color = material_color * (0, 0, 0);
        outColor = vec4(color, 1.0);
      }
    }
  }

}
