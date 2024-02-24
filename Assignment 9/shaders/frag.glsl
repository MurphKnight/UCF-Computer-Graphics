#version 420 core

in vec3 fragNormal;
in vec3 fragPosition;

in vec3 fragColor;
in vec2 fragUV;


layout (binding=0) uniform sampler2D tex2D;
layout (binding=1) uniform samplerCube cubeMapTex;

uniform vec3 eyePostion;
uniform int texture_type;


out vec4 outColor;



void main(){

  //      2D Texture
  if( texture_type == 1){
    vec3 color_tex = texture(tex2D, fragUV).rgb;
    outColor = vec4( color_tex , 1.0 );
  }


  //      Environment Mapping
  else if(  texture_type == 0 ) {
    // Normalize the fragment normal.
    vec3 norm = normalize(fragNormal);

    // Compute view direction using the fragment position and the eye position.
    vec3 view = normalize(eyePostion - fragPosition);

    // Compute the reflection vector using the view direction and the normal.
    vec3 reflect = reflect(-view, norm);

    // Sample the cubemap using the reflection vector.
    vec3 color_env = texture(cubeMapTex, reflect).rgb;

    // Set the color of the fragment to the color of the cubemap.
    outColor = vec4(color_env, 1.0);
  }


  //     Mix
  else if(  texture_type == 2 ) {
    // 2D Texture
    vec3 color_tex = texture(tex2D, fragUV).rgb;

    // Environment Mapping
    vec3 norm = normalize(fragNormal);
    vec3 view = normalize(eyePostion - fragPosition);
    vec3 reflect = reflect(-view, norm);
    vec3 color_env = texture(cubeMapTex, reflect).rgb;

    // To make your object slightly reflective, mix the color due to the 2D texture and the color due to the environment mapping.
    vec3 color_mix = mix(color_tex, color_env, 0.25);

    // Set the color of the fragment.
    outColor = vec4(color_mix, 1.0);
  }

}
