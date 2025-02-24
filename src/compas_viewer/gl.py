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
    .. code-block:: python

        from compas_viewer import Viewer
        from compas_viewer.utilities import gl_info

        viewer = Viewer()
        gl_info()
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
    data : list[float]
        A flat list of floats.
    dynamic : bool, optional
        If True, the buffer is optimized for dynamic access.

    Returns
    -------
    int
        Vertex buffer ID.
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
    data : list[int]
        A flat list of ints.
    dynamic : bool, optional
        If True, the buffer is optimized for dynamic access.

    Returns
    -------
    int
        Element buffer ID.
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


def update_vertex_buffer(data, buffer, offset=0):
    """Update a vertex buffer with new data.

    Parameters
    ----------
    data : list[float]
        A flat list of floats.
    buffer : int
        The ID of the buffer.
    offset : int
        Byte offset into the buffer where the update should start.
    """
    n = len(data)
    size = n * ct.sizeof(ct.c_float)
    data = (ct.c_float * n)(*data)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, buffer)
    GL.glBufferSubData(GL.GL_ARRAY_BUFFER, offset, size, data)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)


def update_index_buffer(data, buffer):
    """Update an index buffer with new data.

    Parameters
    ----------
    data : list[int]
        A flat list of ints.
    buffer : int
        The ID of the buffer.
    """
    n = len(data)
    size = n * ct.sizeof(ct.c_uint)
    data = (ct.c_int * n)(*data)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, buffer)
    GL.glBufferSubData(GL.GL_ELEMENT_ARRAY_BUFFER, 0, size, data)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)


def make_texture_buffer(data, internal_format=GL.GL_RGBA32F):
    """Make a texture buffer from the given data.

    Parameters
    ----------
    data : numpy.ndarray
        A numpy array of floats.
    internal_format : GLenum, optional
        The internal format for the texture buffer. Default is GL.GL_RGBA32F.

    Returns
    -------
    int
        The texture ID.
    """
    # Create buffer
    buffer = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_TEXTURE_BUFFER, buffer)

    GL.glBufferData(GL.GL_TEXTURE_BUFFER, data.nbytes, data, GL.GL_STATIC_DRAW)

    # Create texture
    texture = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_BUFFER, texture)
    GL.glTexBuffer(GL.GL_TEXTURE_BUFFER, internal_format, buffer)

    return texture


def update_texture_buffer(data, texture, offset=0):
    """Update a texture buffer with new data.

    Parameters
    ----------
    data : numpy.ndarray
        A numpy array of floats.
    texture : int
        The texture ID.
    offset : int
        Byte offset into the buffer where the update should start.
    """
    GL.glBindTexture(GL.GL_TEXTURE_BUFFER, texture)
    buffer = GL.glGetTexLevelParameteriv(GL.GL_TEXTURE_BUFFER, 0, GL.GL_TEXTURE_BUFFER_DATA_STORE_BINDING)
    GL.glBindBuffer(GL.GL_TEXTURE_BUFFER, buffer)
    GL.glBufferSubData(GL.GL_TEXTURE_BUFFER, offset, data.nbytes, data)
    GL.glBindBuffer(GL.GL_TEXTURE_BUFFER, 0)
