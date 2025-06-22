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
uniform int element_type;

// Outputs
out vec4 vertex_color;
out vec3 ec_pos;
out float is_selected;
out float show;
out float show_points;
out float show_lines;
out float show_faces;
out vec4 instance_color;
out float object_opacity;
out float linewidth;

float getEffectiveShow(float objectIndex) {
    float showValue = texelFetch(settingsBuffer, int(objectIndex * 3)).r;
    float parentIndex = texelFetch(settingsBuffer, int(objectIndex * 3) + 2).r;
    
    while (parentIndex >= 0.0 && showValue > 0.0) {
        showValue *= texelFetch(settingsBuffer, int(parentIndex * 3)).r;
        parentIndex = texelFetch(settingsBuffer, int(parentIndex * 3) + 2).r;
    }
    return showValue;
}

float getEffectiveSelection(float objectIndex) {
    float selectionValue = texelFetch(settingsBuffer, int(objectIndex * 3) + 1).a;
    float parentIndex = texelFetch(settingsBuffer, int(objectIndex * 3) + 2).r;
    
    while (parentIndex >= 0.0 && selectionValue == 0.0) {  // Continue until we find a selected parent
        selectionValue = max(selectionValue, texelFetch(settingsBuffer, int(parentIndex * 3) + 1).a);
        parentIndex = texelFetch(settingsBuffer, int(parentIndex * 3) + 2).r;
    }
    return selectionValue;
}

mat4 getEffectiveTransform(float objectIndex) {
    mat4 transform = transpose(mat4(
        texelFetch(transformBuffer, int(objectIndex * 4) + 0),
        texelFetch(transformBuffer, int(objectIndex * 4) + 1),
        texelFetch(transformBuffer, int(objectIndex * 4) + 2),
        texelFetch(transformBuffer, int(objectIndex * 4) + 3)
    ));
    
    float parentIndex = texelFetch(settingsBuffer, int(objectIndex * 3) + 2).r;
    
    while (parentIndex >= 0.0) {
        mat4 parentTransform = transpose(mat4(
            texelFetch(transformBuffer, int(parentIndex * 4) + 0),
            texelFetch(transformBuffer, int(parentIndex * 4) + 1),
            texelFetch(transformBuffer, int(parentIndex * 4) + 2),
            texelFetch(transformBuffer, int(parentIndex * 4) + 3)
        ));
        transform = parentTransform * transform;
        parentIndex = texelFetch(settingsBuffer, int(parentIndex * 3) + 2).r;
    }
    
    return transform;
}

void main() {
    // Initialize transform matrix and handle grid case
    mat4 transform = is_grid ? mat4(1.0) : getEffectiveTransform(object_index);

    float pointSize = 1.0;
    float line_width = 1.0;

    // Set visibility and display settings
    if (is_grid) {
        show = show_points = show_lines = show_faces = 1.0;
        is_selected = 0.0;
        object_opacity = 1.0;
    } else {
        vec4 settings_row1 = texelFetch(settingsBuffer, int(object_index * 3));
        vec4 settings_row2 = texelFetch(settingsBuffer, int(object_index * 3) + 1);
        vec4 settings_row3 = texelFetch(settingsBuffer, int(object_index * 3) + 2);
        show = getEffectiveShow(object_index);
        show_points = settings_row1.g;
        show_lines = settings_row1.b;
        show_faces = settings_row1.a;
        instance_color = vec4(settings_row2.rgb, 1.0);
        is_selected = getEffectiveSelection(object_index);
        object_opacity = settings_row3.g;
        pointSize = settings_row3.b;
        line_width = settings_row3.a;
    }

    // Calculate final position
    vertex_color = color;
    vec4 worldPos = transform * vec4(position, 1.0);
    
    // Bypass matrix transformations 2D elements
    if (element_type == 4) {
        gl_Position = vec4(position, 1.0);
        ec_pos = position;
    } else {
        vec4 viewPos = viewworld * worldPos;
        gl_Position = projection * viewPos;
        ec_pos = vec3(viewPos);
    }
    
    gl_PointSize = pointSize;
    linewidth = line_width;
} 