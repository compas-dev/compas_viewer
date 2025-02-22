#version 330 core

in vec3 position;

uniform mat4 projection;
uniform mat4 viewworld;
uniform mat4 transform;
uniform float screen_aspect;
uniform float screen_height;
uniform float text_aspect;
uniform float text_height;
uniform vec3 text_position;
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

    vec4 screen_position = projection * viewworld * transform * vec4(text_position, 1.0);
    vec2 adjustedPos = vec2(position.x / screen_aspect * text_aspect, position.y) * text_height / screen_height;
    vec4 offset = vec4(adjustedPos * screen_position.w, 0.0, 0.0);
    screen_position += offset;
    gl_Position = screen_position;
}
