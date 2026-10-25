from collections.abc import Sequence
from pathlib import Path
from typing import cast

from numpy import array
from numpy.typing import ArrayLike
from OpenGL import GL


class Shader:
    """The shader used by the OpenGL view."""

    def __init__(self, name: str = "mesh") -> None:
        """Compile and link a named shader program.

        Parameters
        ----------
        name
            Stem of the shader source filenames.

        """
        self.program = make_shader_program(name)
        self.locations: dict[str, int] = {}

    def uniform4x4(self, name: str, value: ArrayLike) -> None:
        """Store a uniform 4x4 transformation matrix in the shader program at a named location.

        Parameters
        ----------
        name
            The name of the location in the shader program.
        value
            A 4x4 transformation matrix.

        """
        _value = array(value)
        location = GL.glGetUniformLocation(self.program, name)
        GL.glUniformMatrix4fv(location, 1, True, _value)

    def uniform1i(self, name: str, value: int) -> None:
        """Store a uniform integer in the shader program at a named location.

        Parameters
        ----------
        name
            The name of the location in the shader program.
        value
            An integer value.

        """
        location = GL.glGetUniformLocation(self.program, name)
        GL.glUniform1i(location, value)

    def uniform1f(self, name: str, value: float) -> None:
        """Store a uniform float in the shader program at a named location.

        Parameters
        ----------
        name
            The name of the location in the shader program.
        value
            A float value.

        """
        location = GL.glGetUniformLocation(self.program, name)
        GL.glUniform1f(location, value)

    def uniform3f(self, name: str, value: Sequence[float]) -> None:
        """Store a uniform list of 3 floats in the shader program at a named location.

        Parameters
        ----------
        name
            The name of the location in the shader program.
        value
            An iterable of 3 floats.

        """
        location = GL.glGetUniformLocation(self.program, name)
        GL.glUniform3f(location, *value)

    def uniform2f(self, name: str, value: Sequence[float]) -> None:
        """Store a uniform list of 2 floats in the shader program at a named location.

        Parameters
        ----------
        name
            The name of the location in the shader program.
        value
            An iterable of 2 floats.

        """
        location = GL.glGetUniformLocation(self.program, name)
        GL.glUniform2f(location, *value)

    def uniformText(self, name: str, texture: int) -> None:
        """Store a uniform texture in the shader program at a named location.

        Parameters
        ----------
        name
            The name of the location in the shader program.
        texture
            The texture to store.

        """
        # location = GL.glGetUniformLocation(self.program, name)
        # print(location)
        GL.glActiveTexture(cast(int, GL.GL_TEXTURE0))
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture)

    def uniformBuffer(self, name: str, buffer: int, unit: int = 0) -> None:
        """Store a uniform buffer in the shader program at a named location.

        Parameters
        ----------
        name
            The name of the location in the shader program.
        buffer
            The buffer to store.
        unit
            The texture unit to use (0-15 typically available)

        """
        location = GL.glGetUniformLocation(self.program, name)
        GL.glUniform1i(location, unit)  # Use specified texture unit
        GL.glActiveTexture(cast(int, GL.GL_TEXTURE0) + unit)
        GL.glBindTexture(GL.GL_TEXTURE_BUFFER, buffer)

    def bind(self) -> None:
        """Bind the shader program."""
        GL.glUseProgram(self.program)

    def release(self) -> None:
        """Release (unbind) the shader program."""
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glUseProgram(0)

    def enable_attribute(self, name: str) -> None:
        """Enable a named attribute in the shader program.

        Parameters
        ----------
        name
            The name of the attribute.

        """
        location = GL.glGetAttribLocation(self.program, name)
        GL.glEnableVertexAttribArray(location)
        self.locations[name] = location

    def bind_attribute(self, name: str, value: int, step: int = 3) -> None:
        """Bind a named attribute to a buffer.

        Parameters
        ----------
        name
            The name of the attribute.
        value
            The buffer to bind to the attribute.
        step
            The step size of the attribute.

        """
        location = self.locations[name]
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, value)
        GL.glVertexAttribPointer(location, step, GL.GL_FLOAT, False, 0, None)

    def disable_attribute(self, name: str) -> None:
        """Disable and forget a named vertex attribute.

        Parameters
        ----------
        name
            Attribute name previously enabled on this shader.

        """
        GL.glDisableVertexAttribArray(self.locations[name])
        del self.locations[name]

    def draw_triangles(self, elements: int | None = None, n: int = 0, background: bool = False) -> None:
        """Draw triangles.

        Parameters
        ----------
        elements
            The buffer elements.
        n
            The number of elements.
        background
            Draw in background.

        """
        if elements:
            if background:
                GL.glDisable(GL.GL_DEPTH_TEST)
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, elements)
            GL.glDrawElements(GL.GL_TRIANGLES, n, GL.GL_UNSIGNED_INT, None)
        else:
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, GL.GL_BUFFER_SIZE)

    def draw_lines(self, elements: int | None = None, n: int = 0, width: float = 1, background: bool = False) -> None:
        """Draw lines.

        Parameters
        ----------
        elements
            The buffer elements.
        n
            The number of elements.
        width
            The width of the lines.
        background
            Draw in background.

        """
        if elements:
            if background:
                GL.glDisable(GL.GL_DEPTH_TEST)
            GL.glLineWidth(width)
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, elements)
            GL.glDrawElements(GL.GL_LINES, n, GL.GL_UNSIGNED_INT, None)
            GL.glEnable(GL.GL_DEPTH_TEST)
        else:
            GL.glDrawArrays(GL.GL_LINES, 0, GL.GL_BUFFER_SIZE)

    def draw_points(self, size: float = 1, elements: int | None = None, n: int = 0, background: bool = False) -> None:
        """Draw points.

        Parameters
        ----------
        size
            The size of the points.
        elements
            The buffer elements.
        n
            The number of elements.
        background
            Draw in background.

        """
        GL.glPointSize(size)
        if elements:
            if background:
                GL.glDisable(GL.GL_DEPTH_TEST)
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, elements)
            GL.glDrawElements(GL.GL_POINTS, n, GL.GL_UNSIGNED_INT, None)
        else:
            GL.glDrawArrays(GL.GL_POINTS, 0, GL.GL_BUFFER_SIZE)

    def draw_texts(self, elements: int | None = None, n: int = 0) -> None:
        """Draw text quads.

        Parameters
        ----------
        elements
            The buffer elements.
        n
            The number of elements.

        """
        if elements:
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, elements)
            GL.glDrawElements(GL.GL_TRIANGLE_STRIP, n, GL.GL_UNSIGNED_INT, None)
        else:
            GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, GL.GL_BUFFER_SIZE)

    def draw_arrows(self, elements: int | None, n: int, width: float, background: bool = False) -> None:
        """Draw arrows.

        Parameters
        ----------
        elements
            The buffer elements.
        n
            The number of elements.
        width
            The width of the arrows.
        background
            Draw in background.

        """
        GL.glDisable(GL.GL_POINT_SMOOTH)

        if elements:
            if background:
                GL.glDisable(GL.GL_DEPTH_TEST)
            GL.glLineWidth(width)
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, elements)
            GL.glDrawElements(GL.GL_LINES, n, GL.GL_UNSIGNED_INT, None)
            GL.glEnable(GL.GL_DEPTH_TEST)
        else:
            GL.glDrawArrays(GL.GL_LINES, 0, GL.GL_BUFFER_SIZE)
        GL.glEnable(GL.GL_POINT_SMOOTH)

    def draw_2d_box(self, box_coords: tuple[float, float, float, float], width: int, height: int) -> None:
        """Draw a 2D box. Mostly used for box selection.

        Parameters
        ----------
        box_coords
            The coordinates of the box. The coordinates are in the format of (x1, y1, x2, y2).
        width
            The width of the viewport.
        height
            The height of the viewport.

        """
        # Save current OpenGL state
        depth_test_enabled = GL.glIsEnabled(GL.GL_DEPTH_TEST)
        blend_enabled = GL.glIsEnabled(GL.GL_BLEND)
        previous_line_width = GL.glGetFloat(GL.GL_LINE_WIDTH)

        # Set element_type to 4 to bypass matrix transformations
        self.uniform1i("element_type", 4)

        # Disable depth testing to ensure the box appears on top
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        x1, y1, x2, y2 = box_coords
        x1 = (x1 / width - 0.5) * 2
        x2 = (x2 / width - 0.5) * 2
        y1 = -(y1 / height - 0.5) * 2
        y2 = -(y2 / height - 0.5) * 2
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        # Create vertices for the box
        vertices = array(
            [
                x1,
                y1,
                0.0,  # Bottom-left
                x2,
                y1,
                0.0,  # Bottom-right
                x2,
                y2,
                0.0,  # Top-right
                x1,
                y2,
                0.0,  # Top-left
            ],
            dtype="float32",
        )

        # Create vertex buffer
        vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)

        # Enable position attribute
        self.enable_attribute("position")
        self.bind_attribute("position", vbo, 3)

        # Draw filled rectangle with transparency
        self.uniform1f("opacity", 0.2)  # Set low opacity for filled rectangle
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, 4)

        # Draw the box outline with thicker line width
        self.uniform1f("opacity", 1.0)  # Set full opacity for outline

        # Get supported line width range
        line_width_range = GL.glGetFloatv(GL.GL_LINE_WIDTH_RANGE)
        max_line_width = min(line_width_range[1], 2.0)  # Use 2.0 or the max supported width, whichever is smaller

        GL.glLineWidth(max_line_width)
        # Use LINE_LOOP instead of TRIANGLE_FAN in polygon line mode to avoid diagonal lines
        GL.glDrawArrays(GL.GL_LINE_LOOP, 0, 4)

        # Clean up
        self.disable_attribute("position")
        GL.glDeleteBuffers(1, [vbo])

        # Restore previous OpenGL state
        if not blend_enabled:
            GL.glDisable(GL.GL_BLEND)
        if depth_test_enabled:
            GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glLineWidth(previous_line_width)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)  # Reset polygon mode


def make_shader_program(name: str) -> int:
    """Make a shader program.

    Parameters
    ----------
    name
        The name of the shader.

    Returns
    -------
    int
        Linked OpenGL program identifier.

    """
    shader_directory = Path(__file__).resolve().parent
    vsource = shader_directory / f"{name}.vert"
    fsource = shader_directory / f"{name}.frag"
    gsource = shader_directory / f"{name}.geom"

    vertex = compile_vertex_shader(vsource.read_text(encoding="utf-8"))

    fragment = compile_fragment_shader(fsource.read_text(encoding="utf-8"))

    geometry = None
    if gsource.exists():
        geometry = compile_geometry_shader(gsource.read_text(encoding="utf-8"))

    program = GL.glCreateProgram()
    GL.glAttachShader(program, vertex)
    GL.glAttachShader(program, fragment)
    if geometry:
        GL.glAttachShader(program, geometry)
    GL.glLinkProgram(program)
    GL.glValidateProgram(program)
    result = GL.glGetProgramiv(program, GL.GL_LINK_STATUS)
    if not result:
        raise RuntimeError(GL.glGetProgramInfoLog(program))
    GL.glDeleteShader(vertex)
    GL.glDeleteShader(fragment)
    if geometry:
        GL.glDeleteShader(geometry)
    return cast(int, program)


def compile_vertex_shader(source: str) -> int:
    """Compile a vertex shader from GLSL source.

    Parameters
    ----------
    source
        GLSL vertex-shader source.

    Returns
    -------
    int
        Compiled OpenGL shader identifier.

    """
    shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
    GL.glShaderSource(shader, source)
    GL.glCompileShader(shader)
    result = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
    if not result:
        raise RuntimeError(GL.glGetShaderInfoLog(shader))
    return cast(int, shader)


def compile_fragment_shader(source: str) -> int:
    """Compile a fragment shader from GLSL source.

    Parameters
    ----------
    source
        GLSL fragment-shader source.

    Returns
    -------
    int
        Compiled OpenGL shader identifier.

    """
    shader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
    GL.glShaderSource(shader, source)
    GL.glCompileShader(shader)
    result = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
    if not result:
        raise RuntimeError(GL.glGetShaderInfoLog(shader))
    return cast(int, shader)


def compile_geometry_shader(source: str) -> int:
    """Compile a geometry shader from GLSL source.

    Parameters
    ----------
    source
        GLSL geometry-shader source.

    Returns
    -------
    int
        Compiled OpenGL shader identifier.

    """
    shader = GL.glCreateShader(GL.GL_GEOMETRY_SHADER)
    GL.glShaderSource(shader, source)
    GL.glCompileShader(shader)
    result = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
    if not result:
        raise RuntimeError(GL.glGetShaderInfoLog(shader))
    return cast(int, shader)
