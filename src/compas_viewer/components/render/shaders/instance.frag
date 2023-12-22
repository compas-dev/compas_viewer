#version 120

uniform vec3 instance_color;

void main()
{
    gl_FragColor = vec4(instance_color, 1);
}
