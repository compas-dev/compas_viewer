#version 120

attribute vec3 position;
attribute vec4 color;

uniform mat4 projection;
uniform mat4 viewworld;
uniform mat4 transform;
uniform float scale;

varying vec4 vertex_color;
varying vec3 ec_pos;

void main() {
    vertex_color = color;

    // Create the scaling matrix
    mat4 scalingMatrix = mat4(scale, 0.0, 0.0, 0.0, 0.0, scale, 0.0, 0.0, 0.0, 0.0, scale, 0.0, 0.0, 0.0, 0.0, 1.0);

    // Scale the translation component of the transform matrix
    mat4 scaledTransform = transform;
    scaledTransform[3] = transform[3] * vec4(scale, scale, scale, 1.0);

    // Apply the scaling matrix to the transformation matrix
    scaledTransform = scaledTransform * scalingMatrix;

    // Calculate the position in clip space
    gl_Position = projection * viewworld * scaledTransform * vec4(position, 1.0);

    // Calculate the eye coordinates position
    ec_pos = vec3(viewworld * scaledTransform * vec4(position, 1.0));
}
