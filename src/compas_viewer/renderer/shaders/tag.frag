#version 330 core

uniform sampler2D tex;
uniform bool is_selected;
uniform vec3 text_color;
uniform vec3 selection_color;
uniform vec3 background_color;
uniform float background_alpha;
uniform float object_opacity;

in vec2 texcoord;

out vec4 fragColor;

void main()
{
    vec2 xy = texcoord;
    xy.y = 1.0 - xy.y;
    float a = texture(tex, xy).r;
    vec3 foreground = is_selected ? selection_color : text_color;
    float alpha = a + background_alpha * (1.0 - a);
    vec3 color = alpha > 0.0
        ? (foreground * a + background_color * background_alpha * (1.0 - a)) / alpha
        : foreground;
    fragColor = vec4(color, alpha * object_opacity);
    if (fragColor.a <= 0.0) {
        discard;
    }
}
