#version 330 core

in vec3 position;
in vec4 color;
in float object_index;

uniform mat4 projection;
uniform mat4 viewworld;
uniform samplerBuffer transformBuffer;
uniform samplerBuffer settingsBuffer;
uniform bool is_grid;
uniform float pointSize;

out vec4 vertex_color;
out vec3 ec_pos;
out float is_selected;
out float show;
out float show_points;
out float show_lines;
out float show_faces;
out vec4 instance_color;

void main() {
    mat4 transform = mat4(1.0);
    if (is_grid) {
        is_selected = 0.0;
        show = 1.0;
        show_points = 1.0;
        show_lines = 1.0;
        show_faces = 1.0;
    } else {

        // get the transform
        transform = transpose(mat4(
            texelFetch(transformBuffer, int(object_index * 4) + 0),
            texelFetch(transformBuffer, int(object_index * 4) + 1),
            texelFetch(transformBuffer, int(object_index * 4) + 2),
            texelFetch(transformBuffer, int(object_index * 4) + 3)
        ));

        // get the settings
        vec4 settings_row1 = texelFetch(settingsBuffer, int(object_index * 2));
        vec4 settings_row2 = texelFetch(settingsBuffer, int(object_index * 2) + 1);
        show = settings_row1.r;
        show_points = settings_row1.g;
        show_lines = settings_row1.b;
        show_faces = settings_row1.a;
        instance_color = vec4(settings_row2.rgb, 1.0);
        is_selected = settings_row2.a;
    }


    vertex_color = color;
    vec4 worldPos = transform * vec4(position, 1.0);
    vec4 viewPos = viewworld * worldPos;
    gl_Position = projection * viewPos;
    ec_pos = vec3(viewPos);
    gl_PointSize = pointSize;
}
