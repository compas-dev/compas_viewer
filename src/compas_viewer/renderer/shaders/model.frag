#version 330 core

in vec4 vertex_color;
in vec3 ec_pos;
in float is_selected;
in float show;
in float show_points;
in float show_lines;
in float show_faces;

uniform float opacity;
uniform float object_opacity;
uniform bool is_lighted;
uniform vec3 selection_color;
uniform int element_type;

out vec4 fragColor;

void main() {
    if(show == 0.0) {
        discard;
    }

    if(element_type == 0 && show_points == 0.0) {
        discard;
    }

    if(element_type == 1 && show_lines == 0.0) {
        discard;
    }

    if(element_type == 2 && show_faces == 0.0) {
        discard;
    }

    float alpha = opacity * object_opacity * vertex_color.a;
    vec3 color;
    color = vertex_color.rgb;
    if(is_selected > 0.5) {
        if(element_type == 0) {
            color = selection_color * 0.9;
        } else if(element_type == 1) {
            color = selection_color * 0.8;
        } else {
            color = selection_color;
        }
        if(alpha < 0.5)
            alpha = 0.5;
    }

    if(element_type == 0) {
        // draw a circle
        vec2 center = gl_PointCoord - vec2(0.5);
        float dist = length(center);
        if(dist > 0.5) {
            discard;
        }
    }
    if(is_lighted) {
        vec3 ec_normal = normalize(cross(dFdx(ec_pos), dFdy(ec_pos)));
        vec3 L = normalize(-ec_pos);
        fragColor = vec4(color * dot(ec_normal, L), alpha);
    } else {
        fragColor = vec4(color, alpha);
    }
}
