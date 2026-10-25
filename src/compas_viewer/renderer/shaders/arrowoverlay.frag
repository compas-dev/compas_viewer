#version 330 core

uniform vec3 arrow_color;
uniform vec3 selection_color;
uniform float arrow_opacity;
uniform bool is_selected;

out vec4 fragColor;

void main()
{
    vec3 color = is_selected ? selection_color : arrow_color;
    fragColor = vec4(color, arrow_opacity);
}
