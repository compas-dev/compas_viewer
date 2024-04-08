#version 120

attribute vec3 position;
attribute vec3 color;
// attribute float alpha;

uniform mat4 projection;
uniform mat4 viewworld;
uniform mat4 transform;

varying vec3 vertex_color;
// varying float vertex_alpha;
varying vec3 ec_pos;

void main()
{
    vertex_color = color;
    // vertex_alpha = alpha;
    gl_Position = projection * viewworld * transform * vec4(position, 1.0);
    ec_pos = vec3(viewworld * transform * vec4(position, 1.0));
    
}
