import ctypes as ct

from OpenGL import GL


def gl_info():
    """Return formatted information about the current GL implementation.

    Returns
    -------
    str

    """
    info = """
        Vendor: {0}
        Renderer: {1}
        OpenGL Version: {2}
        Shader Version: {3}
        """.format(
        GL.glGetString(GL.GL_VENDOR),
        GL.glGetString(GL.GL_RENDERER),
        GL.glGetString(GL.GL_VERSION),
        GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION),
    )
    return info


def make_vertex_buffer(data, dynamic=False):
    """Make a vertex buffer from the given data.

    Parameters
    ----------
    data: list[float]
        A flat list of floats.
    dynamic : bool, optional
        If True, the buffer is optimized for dynamic access.

    Returns
    -------
    int
        Vertex buffer ID.

    Examples
    --------
    >>> from compas.utilities import flatten
    >>> vertices = [[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0]]
    >>> buffer = make_vertex_buffer(list(flatten(vertices)))

    """
    access = GL.GL_DYNAMIC_DRAW if dynamic else GL.GL_STATIC_DRAW
    n = len(data)
    size = n * ct.sizeof(ct.c_float)
    vbo = GL.glGenBuffers(1)
    data = (ct.c_float * n)(*data)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, size, data, access)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
    return vbo
