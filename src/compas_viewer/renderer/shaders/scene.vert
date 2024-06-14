#version 430

in vec3 position;
in vec4 color;
in int object;

uniform mat4 projection;
uniform mat4 viewworld;
out int debugOutput;

layout(std430, binding = 0) buffer Matrices {
    mat4 matrices[];
};

out vec4 vertex_color;
out vec3 ec_pos;
void main() {
    vertex_color = color;
    mat4 transform = matrices[object];
    gl_Position = projection * viewworld * transform * vec4(position.x, position.y, position.z + gl_VertexID, 1.0);


    debugOutput = 1;
}