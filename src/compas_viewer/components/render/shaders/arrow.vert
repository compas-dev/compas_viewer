#version 120

attribute vec3 position;
attribute vec3 direction;
attribute vec3 color;
attribute float size;

uniform mat4 projection;
uniform mat4 viewworld;
uniform mat4 transform;
uniform float aspect;

varying vec3 vcolor;
varying vec2 direction_2d;


vec2 get_xy(vec4 pos){
    vec3 ndc = pos.xyz / pos.w; //perspective divide/normalize
    return ndc.xy * 0.5 + 0.5; //ndc is -1 to 1 in GL. scale for 0 to 1
}

void main()
{
    vec4 start_position = projection * viewworld * transform * vec4(position, 1.0);
    vec4 end_position = projection * viewworld * transform * vec4(position + direction, 1.0);
    direction_2d = get_xy(end_position) - get_xy(start_position);
    gl_PointSize = size * 100.0;
    gl_Position = start_position;
    vcolor = color;
}