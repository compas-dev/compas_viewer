#version 330 core

// Inputs
in vec3 position;
in vec4 color;
in float object_index;

// Uniforms
uniform mat4 projection;
uniform mat4 viewworld;
uniform samplerBuffer transformBuffer;
uniform samplerBuffer settingsBuffer;
uniform bool is_grid;
uniform float pointSize;

// Outputs
out vec4 vertex_color;
out vec3 ec_pos;
out float is_selected;
out float show;
out float show_points;
out float show_lines;
out float show_faces;
out vec4 instance_color;

float getEffectiveShow(float objectIndex) {
    float showValue = texelFetch(settingsBuffer, int(objectIndex * 3)).r;
    float parentIndex = texelFetch(settingsBuffer, int(objectIndex * 3) + 2).r;
    
    while (parentIndex >= 0.0 && showValue > 0.0) {
        showValue *= texelFetch(settingsBuffer, int(parentIndex * 3)).r;
        parentIndex = texelFetch(settingsBuffer, int(parentIndex * 3) + 2).r;
    }
    return showValue;
}

void main() {
    // Initialize transform matrix and handle grid case
    mat4 transform = is_grid ? mat4(1.0) : transpose(mat4(
        texelFetch(transformBuffer, int(object_index * 4) + 0),
        texelFetch(transformBuffer, int(object_index * 4) + 1),
        texelFetch(transformBuffer, int(object_index * 4) + 2),
        texelFetch(transformBuffer, int(object_index * 4) + 3)
    ));

    // Set visibility and display settings
    if (is_grid) {
        show = show_points = show_lines = show_faces = 1.0;
        is_selected = 0.0;
    } else {
        vec4 settings_row1 = texelFetch(settingsBuffer, int(object_index * 3));
        vec4 settings_row2 = texelFetch(settingsBuffer, int(object_index * 3) + 1);
        
        show = getEffectiveShow(object_index);
        show_points = settings_row1.g;
        show_lines = settings_row1.b;
        show_faces = settings_row1.a;
        instance_color = vec4(settings_row2.rgb, 1.0);
        is_selected = settings_row2.a;
    }

    // Calculate final position
    vertex_color = color;
    vec4 worldPos = transform * vec4(position, 1.0);
    vec4 viewPos = viewworld * worldPos;
    gl_Position = projection * viewPos;
    ec_pos = vec3(viewPos);
    gl_PointSize = pointSize;
}
