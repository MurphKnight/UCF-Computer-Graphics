#version 420 core

// todo: define all the input variables to the fragment shader
in vec3 fragNormal;
in vec3 fragPosition;
in vec4 fragPosLightSpace;


// todo: define all the uniforms
uniform vec3 light_pos;
uniform vec3 material_color;


layout (binding=0) uniform sampler2D depthTex;  // depth texture bound to texture unit 0
out vec4 outColor;


void main(){

    vec3 norm = normalize( fragNormal );

    // Setting up light directional for point light
    vec3 light_direction = normalize(  light_pos.xyz - fragPosition  );

    // Setting up the diffuse material
    vec3 color_diffuse_reflection = material_color * clamp( dot(norm, light_direction), 0, 1);


    // In the fragment shader, if your fragPosLightSpace is a vec4, first we need to convert it from homogeneous coordinates to 3D coordinates
    //  and map it from the range of clip space (-1 to 1) to the range [0, 1].
    vec3 fragPos3D = fragPosLightSpace.xyz / fragPosLightSpace.w;
    fragPos3D = (fragPos3D + 1.0) / 2.0;

    // Now, we can use the fragPos3D to sample the "depthTex" texture sampler and get the depth of the current fragment.
    float z_current = fragPos3D.z;
    float z_depthTex = texture(depthTex, fragPos3D.xy).r;

    // Compute a bias based on the angle between the light direction and the normal of the current fragment.
    float bias = max(0.0005f * (1.0 - dot(fragNormal, light_direction)), 0.0001f);


    //Compare the z_current and z_depthTex to determine if the current fragment is in shadow or not.
    if(    z_current - bias  >  z_depthTex    )
      outColor = vec4(   material_color * (0, 0, 0),  1.0    );     // in shadow, apply shadow color (e.g. black)
    else
      outColor = vec4( color_diffuse_reflection, 1.0 );     // not in shadow, apply diffuse color

}
