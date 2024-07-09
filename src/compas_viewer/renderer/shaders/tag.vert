#version 120

attribute vec3 position;

uniform mat4 projection;
uniform mat4 viewworld;
uniform mat4 transform;
uniform float scale;

uniform int text_height;
uniform int text_num;

void main() {
    gl_PointSize = text_height * text_num;

    // Create the scaling matrix
    mat4 scalingMatrix = mat4(scale, 0.0, 0.0, 0.0, 0.0, scale, 0.0, 0.0, 0.0, 0.0, scale, 0.0, 0.0, 0.0, 0.0, 1.0);

    // Scale the translation component of the transform matrix
    mat4 scaledTransform = transform;
    scaledTransform[3] = transform[3] * vec4(scale, scale, scale, 1.0);

    // Apply the scaling matrix to the transformation matrix
    scaledTransform = scaledTransform * scalingMatrix;

    // Calculate the position in clip space
    gl_Position = projection * viewworld * scaledTransform * vec4(position, 1.0);
}
