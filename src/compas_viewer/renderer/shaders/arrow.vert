#version 120

attribute vec3 position;
attribute vec4 color;

uniform mat4 projection;
uniform mat4 viewworld;
uniform mat4 transform;
uniform float scale;

varying vec4 vertex_color;

void main() {
    vertex_color = color;
    gl_Position = projection * viewworld * transform * vec4(position * scale, 1.);
}
