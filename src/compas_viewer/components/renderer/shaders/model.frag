#version 120

varying vec3 vertex_color;
varying vec3 ec_pos;

uniform float opacity;
uniform float object_opacity;
uniform bool is_lighted;
uniform bool is_selected;
uniform vec3 selection_color;
uniform int element_type;

void main()
{
    float alpha=opacity*object_opacity;
    vec3 color;
    color=vertex_color;
    if(is_selected){
        if(element_type==0){color=selection_color*.9;}
        else if(element_type==1){color=selection_color*.8;}
        else{color=selection_color;}
        if(alpha<.5)alpha=.5;
    }

    vec3 light_pos=vec3(0,0,0);
    if(is_lighted){
        vec3 ec_normal=normalize(cross(dFdx(ec_pos),dFdy(ec_pos)));
        vec3 L=normalize(-ec_pos);
        gl_FragColor=vec4(color*dot(ec_normal,L),alpha);
    }else{
        gl_FragColor=vec4(color,alpha);
    }
}
