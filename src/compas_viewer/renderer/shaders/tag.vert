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
uniform float background_padding;
uniform int vertical_align;
uniform int horizontal_align;

out vec2 texcoord;

void main()
{
    vec2 corner = vec2(position.x, position.y);
    vec2 aligned = corner;

    if (horizontal_align == 0) {
        aligned.x -= 0.5;
    }
    else if (horizontal_align == 1) {
        aligned.x -= 1.0;
    }

    if (vertical_align == 0) {
        aligned.y -= 0.5;
    }
    else if (vertical_align == 1) {
        aligned.y -= 1.0;
    }

    vec4 view_position = viewworld * transform * vec4(text_position, 1.0);
    vec2 size = vec2(text_height * text_aspect, text_height);

    if (screen_space) {
        vec4 screen_position = projection * view_position;
        vec2 pixel_position = aligned * size + text_offset;
        pixel_position += (2.0 * corner - 1.0) * background_padding;
        screen_position.xy += 2.0 * pixel_position / screen_size * screen_position.w;
        gl_Position = screen_position;
        texcoord = (corner * (size + 2.0 * background_padding) - background_padding) / size;
    }
    else {
        vec4 anchor_position = projection * view_position;
        vec4 width_position = projection * (view_position + vec4(size.x, 0.0, 0.0, 0.0));
        vec4 height_position = projection * (view_position + vec4(0.0, size.y, 0.0, 0.0));
        vec2 projected_size = vec2(
            abs(width_position.x / width_position.w - anchor_position.x / anchor_position.w) * screen_size.x * 0.5,
            abs(height_position.y / height_position.w - anchor_position.y / anchor_position.w) * screen_size.y * 0.5
        );
        projected_size = max(projected_size, vec2(0.0001));
        view_position.xy += aligned * size + text_offset;
        vec4 screen_position = projection * view_position;
        screen_position.xy += 2.0 * (2.0 * corner - 1.0) * background_padding / screen_size * screen_position.w;
        gl_Position = screen_position;
        texcoord = (corner * (projected_size + 2.0 * background_padding) - background_padding) / projected_size;
    }
}
