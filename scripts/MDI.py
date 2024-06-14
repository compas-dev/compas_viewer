import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
import numpy as np

# Vertex Shader
vertex_shader = """
#version 330 core
layout(location = 0) in vec3 position;
void main() {
    gl_Position = vec4(position, 1.0);
}
"""

# Fragment Shader
fragment_shader = """
#version 330 core
out vec4 FragColor;
void main() {
    FragColor = vec4(1.0, 0.5, 0.2, 1.0);
}
"""

# Initialize GLFW
if not glfw.init():
    raise Exception("Failed to initialize GLFW")

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

window = glfw.create_window(800, 600, "Multi-Draw Indirect Example", None, None)
if not window:
    glfw.terminate()
    raise Exception("Failed to create GLFW window")

glfw.make_context_current(window)

# Compile and link shaders
shader_program = compileProgram(
    compileShader(vertex_shader, GL_VERTEX_SHADER),
    compileShader(fragment_shader, GL_FRAGMENT_SHADER)
)

# Define vertices and indices
vertices = np.array([
    -0.5, -0.1, 0.0,
     0.5, -0.5, 0.0,
     0.0,  0.5, 0.0,
], dtype=np.float32)

indices = np.array([0, 1, 2], dtype=np.uint32)

# Create and bind VAO, VBO, and EBO
VAO = glGenVertexArrays(1)
VBO = glGenBuffers(1)
EBO = glGenBuffers(1)
glBindVertexArray(VAO)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, None)
glEnableVertexAttribArray(0)

# Setup indirect drawing commands
draw_commands = np.array([(3, 1, 0, 0, 0)], dtype=[('count', np.uint32), ('primCount', np.uint32), ('firstIndex', np.uint32), ('baseVertex', np.uint32), ('baseInstance', np.uint32)])
indirect_buffer = glGenBuffers(1)
glBindBuffer(GL_DRAW_INDIRECT_BUFFER, indirect_buffer)
glBufferData(GL_DRAW_INDIRECT_BUFFER, draw_commands.nbytes, draw_commands, GL_STATIC_DRAW)

# Main rendering loop
while not glfw.window_should_close(window):
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(shader_program)
    glBindVertexArray(VAO)
    glBindBuffer(GL_DRAW_INDIRECT_BUFFER, indirect_buffer)
    glMultiDrawElementsIndirect(GL_TRIANGLES, GL_UNSIGNED_INT, None, 1, 0)
    glfw.swap_buffers(window)

# Cleanup
glDeleteVertexArrays(1, [VAO])
glDeleteBuffers(1, [VBO, EBO, indirect_buffer])
glDeleteProgram(shader_program)
glfw.terminate()
