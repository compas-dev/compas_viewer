#version 330 core

in vec4 vertex_color;
in vec3 ec_pos;
in float is_selected;

uniform float opacity;
uniform float object_opacity;
uniform bool is_lighted;
uniform vec3 selection_color;
uniform int element_type;

out vec4 fragColor;

void main() {
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
        // gl_PointCoord is in [0,1], with (0,0) at the lower-left of the point
        vec2 center = gl_PointCoord - vec2(0.5);
        float dist = length(center);

        // If the fragment is outside the radius, discard it
        if (dist > 0.5) {
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
