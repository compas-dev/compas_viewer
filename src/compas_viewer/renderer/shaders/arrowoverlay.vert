#version 330 core

in vec3 position;

uniform mat4 projection;
uniform mat4 viewworld;
uniform mat4 transform;
uniform vec2 screen_size;
uniform vec3 start_position;
uniform vec3 end_position;
uniform float line_width;
uniform float head_length;
uniform float head_width;

void main()
{
    vec4 start_clip = projection * viewworld * transform * vec4(start_position, 1.0);
    vec4 end_clip = projection * viewworld * transform * vec4(end_position, 1.0);
    vec2 start_pixel = (start_clip.xy / start_clip.w * 0.5 + 0.5) * screen_size;
    vec2 end_pixel = (end_clip.xy / end_clip.w * 0.5 + 0.5) * screen_size;
    vec2 delta = end_pixel - start_pixel;
    float length_pixels = length(delta);
    vec2 direction = length_pixels > 0.0 ? delta / length_pixels : vec2(1.0, 0.0);
    vec2 normal = vec2(-direction.y, direction.x);

    float base_distance = max(0.0, length_pixels - min(head_length, length_pixels));
    float distance_along = position.x == 0.0 ? 0.0 : (position.x == 1.0 ? base_distance : length_pixels);
    float width = position.z < 0.5 ? line_width : head_width;
    vec2 pixel = start_pixel + direction * distance_along + normal * position.y * width;
    vec2 ndc = pixel / screen_size * 2.0 - 1.0;

    float interpolation = length_pixels > 0.0 ? distance_along / length_pixels : 0.0;
    float clip_w = mix(start_clip.w, end_clip.w, interpolation);
    float clip_z = mix(start_clip.z / start_clip.w, end_clip.z / end_clip.w, interpolation) * clip_w;
    gl_Position = vec4(ndc * clip_w, clip_z, clip_w);
}
