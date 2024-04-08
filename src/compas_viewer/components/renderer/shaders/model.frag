#version 120

varying vec3 vertex_color;
varying float vertex_alpha;
varying vec3 ec_pos;

uniform float opacity;
uniform float object_opacity;
uniform bool is_lighted;
uniform bool is_selected;
uniform vec3 selection_color;
uniform int element_type;
// uniform bool use_rgba;

void main()
{
    float alpha=opacity*object_opacity;
    vec3 color;
    color=vertex_color;
    if (is_selected) {
        if (element_type == 0) {color = selection_color*0.9;}
        else if (element_type == 1) {color = selection_color*0.8;}
        else {color = selection_color;}
        if (alpha < 0.5) alpha = 0.5;
    }
    // if (use_rgba){
    //     alpha *= vertex_alpha;
    // }

    vec3 light_pos=vec3(0,0,0);
    if(is_lighted){
        vec3 ec_normal=normalize(cross(dFdx(ec_pos),dFdy(ec_pos)));
        vec3 L=normalize(-ec_pos);
        gl_FragColor=vec4(color*dot(ec_normal,L),alpha);
    }else{
        gl_FragColor=vec4(color,alpha);
    }
}
