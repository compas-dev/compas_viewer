#version 330 core

layout (lines) in;
layout (triangle_strip, max_vertices = 4) out;

// from vertex shader
in vec4 vertex_color[];
in vec3 ec_pos[];
in float is_selected[];
in float show[];
in float show_points[];
in float show_lines[];
in float show_faces[];
in vec4 instance_color[];
in float object_opacity[];
in float linewidth[];

// to fragment shader
out vec4 g_vertex_color;
out vec3 g_ec_pos;
out float g_is_selected;
out float g_show;
out float g_show_points;
out float g_show_lines;
out float g_show_faces;
out vec4 g_instance_color;
out float g_object_opacity;

uniform vec2 viewport; // The (width, height) of the viewport in pixels

void main() {
    vec2 p1 = gl_in[0].gl_Position.xy / gl_in[0].gl_Position.w;
    vec2 p2 = gl_in[1].gl_Position.xy / gl_in[1].gl_Position.w;

    vec2 dir = normalize(p2 - p1);
    vec2 normal = vec2(-dir.y, dir.x);

    float width = linewidth[0];
    vec2 offset = normal * width / viewport;

    // Vertex 1
    gl_Position = vec4((p1 - offset) * gl_in[0].gl_Position.w, gl_in[0].gl_Position.zw);
    g_vertex_color = vertex_color[0];
    g_ec_pos = ec_pos[0];
    g_is_selected = is_selected[0];
    g_show = show[0];
    g_show_points = show_points[0];
    g_show_lines = show_lines[0];
    g_show_faces = show_faces[0];
    g_instance_color = instance_color[0];
    g_object_opacity = object_opacity[0];
    EmitVertex();

    // Vertex 2
    gl_Position = vec4((p1 + offset) * gl_in[0].gl_Position.w, gl_in[0].gl_Position.zw);
    EmitVertex();

    // Vertex 3
    gl_Position = vec4((p2 - offset) * gl_in[1].gl_Position.w, gl_in[1].gl_Position.zw);
    g_vertex_color = vertex_color[1];
    g_ec_pos = ec_pos[1];
    g_is_selected = is_selected[1];
    g_show = show[1];
    g_show_points = show_points[1];
    g_show_lines = show_lines[1];
    g_show_faces = show_faces[1];
    g_instance_color = instance_color[1];
    g_object_opacity = object_opacity[1];
    EmitVertex();

    // Vertex 4
    gl_Position = vec4((p2 + offset) * gl_in[1].gl_Position.w, gl_in[1].gl_Position.zw);
    EmitVertex();

    EndPrimitive();
} 