#version 120

attribute vec3 position;

uniform mat4 projection;
uniform mat4 viewworld;
uniform mat4 transform;
uniform float scale;

uniform int text_height;
uniform int text_num;

void main()
{   
    gl_PointSize = text_height * text_num;
    gl_Position = projection * viewworld * transform * vec4(position * scale, 1.0);
}
