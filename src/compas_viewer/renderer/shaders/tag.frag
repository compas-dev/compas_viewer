#version 120


uniform sampler2D tex;
uniform int text_num;
uniform vec3 text_color;

varying vec2 texcoord;

void main()
{
    vec2 xy = texcoord;
    xy.y = 1.0 - xy.y;
    float a = texture2D(tex, xy).r;
    gl_FragColor = vec4(text_color, a);
    if (a <= 0){
        discard;
    }
}
