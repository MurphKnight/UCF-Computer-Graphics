#version 420 core

// Attributes
layout (location = 0) in vec3 position;    // we can also use layout to specify the location of the attribute
layout (location = 1) in vec2 uv;
layout (location = 2) in vec3 normal;


// todo: define all the out variables
out vec3 fragNormal;
out vec3 fragPosition;
out vec4 fragPosLightSpace;


// todo: define all the uniforms
uniform mat4 model_mat_obj;
uniform mat4 view_mat;
uniform mat4 projection_mat;

uniform mat4 lightViewMatrix;
uniform mat4 lightProjectionMatrix;


void main(){
    // For position attribute
    vec4 pos = projection_mat * view_mat * model_mat_obj * vec4(position, 1.0);
    gl_Position = pos;


    // For normal attribute
    mat4 normal_matrix = transpose(  inverse(model_mat_obj)  );
    vec3 new_normal = (  normal_matrix * vec4(normal, 0)  ).xyz;


    fragNormal = normalize(  new_normal  );
    fragPosition = (model_mat_obj * vec4(position, 1.0)).xyz;
    fragPosLightSpace = lightProjectionMatrix * lightViewMatrix * model_mat_obj * vec4(position, 1.0);
}
