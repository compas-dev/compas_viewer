#version 120

attribute vec3 position;

uniform mat4 projection;
uniform mat4 viewworld;
uniform mat4 transform;
uniform float scale;

void main()
{
    gl_Position = projection * viewworld * transform * vec4(position * scale, 1.0);
}
