#version 330 core

uniform sampler2D tex;
uniform bool is_selected;
uniform vec3 text_color;

in vec2 texcoord;

out vec4 fragColor;

void main()
{
    vec2 xy = texcoord;
    xy.y = 1.0 - xy.y;
    float a = texture(tex, xy).r;
    if (is_selected) {
        fragColor = vec4(1.0, 1.0, 0.0, a);
    } else {
        fragColor = vec4(text_color, a);
    }
    if (a <= 0){
        discard;
    }
}
