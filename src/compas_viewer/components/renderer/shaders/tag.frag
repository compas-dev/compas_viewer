#version 120


uniform sampler2D tex;
uniform int text_num;
uniform vec3 text_color;

void main()
{
    vec2 xy = gl_PointCoord;
    float a = texture2D(tex, xy).r;
    gl_FragColor = vec4(text_color, a);
    if (a <= 0){
        discard;
    }
}
