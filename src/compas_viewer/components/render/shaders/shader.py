from pathlib import Path

from OpenGL import GL


class Shader:
    """The shader used by the OpenGL view."""

    def __init__(self, name="mesh"):
        self.program = make_shader_program(name)
        self.locations = {}

    def uniform4x4(self, name, value):
        """Store a uniform 4x4 transformation matrix in the shader program at a named location.

        Parameters
        ----------
        name: str
            The name of the location in the shader program.
        value: array-like
            A 4x4 transformation matrix in column-major ordering.
        """
        location = GL.glGetUniformLocation(self.program, name)
        GL.glUniformMatrix4fv(location, 1, True, value)

    def uniform1i(self, name, value):
        """Store a uniform integer in the shader program at a named location.

        Parameters
        ----------
        name: str
            The name of the location in the shader program.
        value: int
            An integer value.
        """
        location = GL.glGetUniformLocation(self.program, name)
        GL.glUniform1i(location, value)

    def uniform1f(self, name, value):
        """Store a uniform float in the shader program at a named location.

        Parameters
        ----------
        name: str
            The name of the location in the shader program.
        value: float
            A float value.
        """
        location = GL.glGetUniformLocation(self.program, name)
        GL.glUniform1f(location, value)

    def uniform3f(self, name, value):
        """Store a uniform list of 3 floats in the shader program at a named location.

        Parameters
        ----------
        name: str
            The name of the location in the shader program.
        value: (float, float, float) | list[float]
            An iterable of 3 floats.
        """
        location = GL.glGetUniformLocation(self.program, name)
        GL.glUniform3f(location, *value)

    def uniformText(self, name, texture):
        # TODO:
        # location = GL.glGetUniformLocation(self.program, name)
        # print(location)
        GL.glActiveTexture(GL.GL_TEXTURE0 + 0)  # type: ignore
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture)

    def bind(self):
        """Bind the shader program."""
        GL.glUseProgram(self.program)

    def release(self):
        """Release (unbind) the shader program."""
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glUseProgram(0)

    def enable_attribute(self, name):
        location = GL.glGetAttribLocation(self.program, name)
        GL.glEnableVertexAttribArray(location)
        self.locations[name] = location

    def bind_attribute(self, name, value, step=3):
        location = self.locations[name]
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, value)
        GL.glVertexAttribPointer(location, step, GL.GL_FLOAT, False, 0, None)

    def disable_attribute(self, name):
        GL.glDisableVertexAttribArray(self.locations[name])
        del self.locations[name]

    def draw_triangles(self, elements=None, n=0, background=False):
        if elements:
            if background:
                GL.glDisable(GL.GL_DEPTH_TEST)
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, elements)
            GL.glDrawElements(GL.GL_TRIANGLES, n, GL.GL_UNSIGNED_INT, None)
        else:
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, GL.GL_BUFFER_SIZE)

    def draw_lines(self, elements=None, n=0, width=1, background=False):
        if elements:
            if background:
                GL.glDisable(GL.GL_DEPTH_TEST)
            GL.glLineWidth(width)
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, elements)
            GL.glDrawElements(GL.GL_LINES, n, GL.GL_UNSIGNED_INT, None)
            GL.glEnable(GL.GL_DEPTH_TEST)
        else:
            GL.glDrawArrays(GL.GL_LINES, 0, GL.GL_BUFFER_SIZE)

    def draw_points(self, size=1, elements=None, n=0, background=False):
        GL.glPointSize(size)
        if elements:
            if background:
                GL.glDisable(GL.GL_DEPTH_TEST)
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, elements)
            GL.glDrawElements(GL.GL_POINTS, n, GL.GL_UNSIGNED_INT, None)
        else:
            GL.glDrawArrays(GL.GL_POINTS, 0, GL.GL_BUFFER_SIZE)

    def draw_texts(self, elements=None, n=0):
        GL.glDisable(GL.GL_POINT_SMOOTH)
        GL.glEnable(GL.GL_POINT_SPRITE)
        GL.glEnable(GL.GL_PROGRAM_POINT_SIZE)
        if elements:
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, elements)
            GL.glDrawElements(GL.GL_POINTS, n, GL.GL_UNSIGNED_INT, None)
        else:
            GL.glDrawArrays(GL.GL_POINTS, 0, GL.GL_BUFFER_SIZE)
        GL.glDisable(GL.GL_POINT_SPRITE)
        GL.glEnable(GL.GL_POINT_SMOOTH)

    def draw_arrows(self, elements=None, n=0):
        GL.glDisable(GL.GL_POINT_SMOOTH)
        GL.glEnable(GL.GL_POINT_SPRITE)
        GL.glEnable(GL.GL_PROGRAM_POINT_SIZE)
        if elements:
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, elements)
            GL.glDrawElements(GL.GL_POINTS, n, GL.GL_UNSIGNED_INT, None)
        else:
            GL.glDrawArrays(GL.GL_POINTS, 0, GL.GL_BUFFER_SIZE)
        GL.glDisable(GL.GL_POINT_SPRITE)
        GL.glEnable(GL.GL_POINT_SMOOTH)

    def draw_2d_box(self, box_coords, width, height):
        x1, y1, x2, y2 = box_coords
        x1 = (x1 / width - 0.5) * 2
        x2 = (x2 / width - 0.5) * 2
        y1 = -(y1 / height - 0.5) * 2
        y2 = -(y2 / height - 0.5) * 2
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        GL.glLineWidth(1)
        GL.glBegin(GL.GL_LINE_LOOP)
        GL.glColor3f(0, 0, 0)
        GL.glVertex2f(x1, y1)
        GL.glVertex2f(x2, y1)
        GL.glVertex2f(x2, y2)
        GL.glVertex2f(x1, y2)
        GL.glEnd()


def make_shader_program(name: str):
    vsource = Path(Path(__file__), f"{name}.vert")
    fsource = Path(Path(__file__), f"{name}.frag")

    with open(vsource, "r") as f:
        vertex = compile_vertex_shader(f.read())

    with open(fsource, "r") as f:
        fragment = compile_fragment_shader(f.read())

    program = GL.glCreateProgram()
    GL.glAttachShader(program, vertex)
    GL.glAttachShader(program, fragment)
    GL.glLinkProgram(program)
    GL.glValidateProgram(program)
    result = GL.glGetProgramiv(program, GL.GL_LINK_STATUS)
    if not result:
        raise RuntimeError(GL.glGetProgramInfoLog(program))
    GL.glDeleteShader(vertex)
    GL.glDeleteShader(fragment)
    return program


def compile_vertex_shader(source):
    shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
    GL.glShaderSource(shader, source)
    GL.glCompileShader(shader)
    result = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
    if not result:
        raise RuntimeError(GL.glGetShaderInfoLog(shader))
    return shader


def compile_fragment_shader(source):
    shader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
    GL.glShaderSource(shader, source)
    GL.glCompileShader(shader)
    result = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
    if not result:
        raise RuntimeError(GL.glGetShaderInfoLog(shader))
    return shader
