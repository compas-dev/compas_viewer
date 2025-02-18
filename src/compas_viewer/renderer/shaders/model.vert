#version 330 core

in vec3 position;
in vec4 color;
in float instance_index;

uniform mat4 projection;
uniform mat4 viewworld;
uniform samplerBuffer transformBuffer;

out vec4 vertex_color;
out vec3 ec_pos;

void main() {
    int offset = int(0) * 4;
    // mat4 transform = mat4(
    //     texelFetch(transformBuffer, offset),
    //     texelFetch(transformBuffer, offset + 1),
    //     texelFetch(transformBuffer, offset + 2),
    //     texelFetch(transformBuffer, offset + 3)
    // );

    mat4 transform = mat4(
        texelFetch(transformBuffer, offset),
        texelFetch(transformBuffer, offset + 1),
        texelFetch(transformBuffer, offset + 2),
        texelFetch(transformBuffer, offset + 3)
    );
    
    vertex_color = color;
    gl_Position = projection * viewworld * transform * vec4(position, 1.0);
    ec_pos = vec3(viewworld * transform * vec4(position, 1.0));
}
