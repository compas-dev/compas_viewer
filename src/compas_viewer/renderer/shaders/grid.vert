#version 120

attribute vec3 position;
attribute vec3 color;

uniform mat4 projection;
uniform mat4 viewworld;
uniform mat4 transform;

varying vec3 vertex_color;

void main()
{
    vertex_color = color;
    gl_Position = projection * viewworld * transform * vec4(position, 1.0);
}
