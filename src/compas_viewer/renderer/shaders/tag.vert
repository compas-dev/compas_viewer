#version 330 core

in vec3 position;

uniform mat4 projection;
uniform mat4 viewworld;
uniform mat4 transform;
uniform bool screen_space;
uniform vec2 screen_size;
uniform float text_aspect;
uniform float text_height;
uniform vec3 text_position;
uniform vec2 text_offset;
uniform int vertical_align;
uniform int horizontal_align;

out vec2 texcoord;

void main()
{
    texcoord = vec2(position.x, position.y);

    vec2 position = vec2(position.x, position.y);

    if (horizontal_align == 0) {
        position.x -= 0.5;
    }
    else if (horizontal_align == 1) {
        position.x -= 1.0;
    }

    if (vertical_align == 0) {
        position.y -= 0.5;
    }
    else if (vertical_align == 1) {
        position.y -= 1.0;
    }

    vec4 view_position = viewworld * transform * vec4(text_position, 1.0);
    vec2 size = vec2(text_height * text_aspect, text_height);

    if (screen_space) {
        vec4 screen_position = projection * view_position;
        vec2 pixel_position = position * size + text_offset;
        screen_position.xy += 2.0 * pixel_position / screen_size * screen_position.w;
        gl_Position = screen_position;
    }
    else {
        view_position.xy += position * size + text_offset;
        gl_Position = projection * view_position;
    }
}
