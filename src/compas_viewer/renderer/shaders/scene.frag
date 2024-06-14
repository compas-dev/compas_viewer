#version 430

in vec4 vertex_color;
in vec3 ec_pos;
out vec4 frag_color;
void main() {

    float alpha = vertex_color.a;
    vec3 color;
    color = vertex_color.rgb;
    
    // if(is_lighted) {
    if(true) {
        vec3 ec_normal = normalize(cross(dFdx(ec_pos), dFdy(ec_pos)));
        vec3 L = normalize(-ec_pos);
        frag_color  = vec4(color * dot(ec_normal, L), alpha);
    } else {
        frag_color  = vec4(color, alpha);
    }
}
