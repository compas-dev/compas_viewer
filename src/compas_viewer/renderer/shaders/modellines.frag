#version 330 core

// Inputs
in vec4 g_vertex_color;
in vec3 g_ec_pos;
in float g_is_selected;
in float g_show;
in float g_show_points;
in float g_show_lines;
in float g_show_faces;
in vec4 g_instance_color;
in float g_object_opacity;

// Uniforms
uniform float opacity;
uniform bool is_lighted;
uniform vec3 selection_color;
uniform int element_type;
uniform bool is_instance;
uniform bool is_grid;

out vec4 fragColor;

void main() {
    // Early visibility checks
    if (g_show == 0.0 || 
        (element_type == 0 && g_show_points == 0.0) ||
        (element_type == 1 && g_show_lines == 0.0) ||
        (element_type == 2 && g_show_faces == 0.0) ||
        (is_instance && is_grid)) {
        discard;
    }

    // Handle instanced objects
    if (is_instance) {
        fragColor = g_instance_color;
        return;
    }

    // Calculate color and alpha
    float alpha = opacity * g_object_opacity * g_vertex_color.a;
    vec3 color = g_vertex_color.rgb;

    // Handle selection highlighting
    if (g_is_selected > 0.5) {
        color = selection_color * (element_type == 0 ? 0.9 : 
                                 element_type == 1 ? 0.8 : 
                                 1.0);
        alpha = max(alpha, 0.5);
    }

    // Draw circular points
    if (element_type == 0) {
        vec2 center = gl_PointCoord - vec2(0.5);
        if (length(center) > 0.5) {
            discard;
        }
    }

    // Apply lighting if needed
    if (is_lighted && !is_grid) {
        vec3 ec_normal = normalize(cross(dFdx(g_ec_pos), dFdy(g_ec_pos)));
        vec3 L = normalize(-g_ec_pos);
        fragColor = vec4(color * dot(ec_normal, L), alpha);
    } else {
        fragColor = vec4(color, alpha);
    }
} 