#version 330 core

in vec3 position;
in vec4 color;
in float object_index;

uniform mat4 projection;
uniform mat4 viewworld;
uniform samplerBuffer transformBuffer;
uniform samplerBuffer settingsBuffer;
uniform int setting_length;
uniform bool is_grid;
uniform float pointSize;

out vec4 vertex_color;
out vec3 ec_pos;
out float is_selected;
out float show;
out float show_points;
out float show_lines;
out float show_faces;

void main() {
    mat4 transform = mat4(1.0);
    if (is_grid) {
        is_selected = 0.0;
        show = 1.0;
        show_points = 1.0;
        show_lines = 1.0;
        show_faces = 1.0;
    } else {
        int offset = int(object_index) * 4;
        transform = transpose(mat4(
            texelFetch(transformBuffer, offset + 0),
            texelFetch(transformBuffer, offset + 1),
            texelFetch(transformBuffer, offset + 2),
            texelFetch(transformBuffer, offset + 3)
        ));

        is_selected = texelFetch(settingsBuffer, int(object_index * setting_length)).r;
        show = texelFetch(settingsBuffer, int(object_index * setting_length + 1)).r;
        show_points = texelFetch(settingsBuffer, int(object_index * setting_length + 2)).r;
        show_lines = texelFetch(settingsBuffer, int(object_index * setting_length + 3)).r;
        show_faces = texelFetch(settingsBuffer, int(object_index * setting_length + 4)).r;
    }

    vertex_color = color;
    vec4 worldPos = transform * vec4(position, 1.0);
    vec4 viewPos = viewworld * worldPos;
    gl_Position = projection * viewPos;
    ec_pos = vec3(viewPos);
    gl_PointSize = pointSize;
}
