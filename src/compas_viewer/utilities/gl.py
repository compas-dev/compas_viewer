import ctypes as ct

from OpenGL import GL


def gl_info() -> str:
    """Return formatted information about the current GL implementation.

    Returns
    -------
    str
        A formatted string containing information about the current GL
        implementation.

    Notes
    -----
    This function is used for debugging purposes on your machine.
    The GL error could be diverse depending the driver, OS, and GL versions.
    Please report your error to help us improve the compatibility.

    Examples
    --------
    >>> from compas_viewer.utilities import gl_info
    >>> print(gl_info()) # doctest: +SKIP
    """
    info: str = f"""
        Vendor: {GL.glGetString(GL.GL_VENDOR)}
        Renderer: {GL.glGetString(GL.GL_RENDERER)}
        OpenGL Version: {GL.glGetString(GL.GL_VERSION)}
        Shader Version: {GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION)}
        """

    return info


def make_vertex_buffer(data, dynamic=False):
    """Make a vertex buffer from the given data.

    Parameters
    ----------
    data : List[float]
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
    >>> buffer = make_vertex_buffer(list(flatten(vertices))) # doctest: +SKIP

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


def make_index_buffer(data, dynamic=False):
    """Make an element buffer from the given data.

    Parameters
    ----------
    data : List[int]
        A flat list of ints.
    dynamic : bool, optional
        If True, the buffer is optimized for dynamic access.

    Returns
    -------
    int
        Element buffer ID.

    Examples
    --------
    >>> from compas.utilities import flatten
    >>> edges = [(0, 1), (1, 2), (2, 3)]
    >>> buffer = make_index_buffer(list(flatten(edges))) # doctest: +SKIP

    """
    access = GL.GL_DYNAMIC_DRAW if dynamic else GL.GL_STATIC_DRAW
    n = len(data)
    size = n * ct.sizeof(ct.c_uint)
    vbo = GL.glGenBuffers(1)
    data = (ct.c_int * n)(*data)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, vbo)
    GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, size, data, access)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
    return vbo


def update_vertex_buffer(data, buffer):
    """Update a vertex buffer with new data.

    Parameters
    ----------
    data : List[float]
        A flat list of floats.
    buffer : int
        The ID of the buffer.

    Returns
    -------
    None

    """
    n = len(data)
    size = n * ct.sizeof(ct.c_float)
    data = (ct.c_float * n)(*data)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, buffer)
    GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, size, data)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)


def update_index_buffer(data, buffer):
    """Update an index buffer with new data.

    Parameters
    ----------
    data : List[int]
        A flat list of ints.
    buffer : int
        The ID of the buffer.

    Returns
    -------
    None

    """
    n = len(data)
    size = n * ct.sizeof(ct.c_uint)
    data = (ct.c_int * n)(*data)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, buffer)
    GL.glBufferSubData(GL.GL_ELEMENT_ARRAY_BUFFER, 0, size, data)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
