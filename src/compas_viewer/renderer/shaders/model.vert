#version 330 core

in vec3 position;
in vec4 color;

uniform mat4 projection;
uniform mat4 viewworld;
uniform mat4 transform;

out vec4 vertex_color;
out vec3 ec_pos;

void main() {
    vertex_color = color;
    gl_Position = projection * viewworld * transform * vec4(position, 1.0);
    ec_pos = vec3(viewworld * transform * vec4(position, 1.0));
}
