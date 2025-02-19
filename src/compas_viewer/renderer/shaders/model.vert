#version 330 core

in vec3 position;
in vec4 color;
in float object_index;

uniform mat4 projection;
uniform mat4 viewworld;
uniform samplerBuffer transformBuffer;
uniform float pointSize;

out vec4 vertex_color;
out vec3 ec_pos;

void main() {

    int offset = int(object_index) * 4;
    mat4 transform = transpose(mat4(
        texelFetch(transformBuffer, offset + 0),
        texelFetch(transformBuffer, offset + 1),
        texelFetch(transformBuffer, offset + 2),
        texelFetch(transformBuffer, offset + 3)
    ));

    vertex_color = color;
    vec4 worldPos = transform * vec4(position, 1.0);
    vec4 viewPos = viewworld * worldPos;
    gl_Position = projection * viewPos;
    ec_pos = vec3(viewPos);
    gl_PointSize = pointSize;

}
