import ctypes as ct
from collections.abc import Sequence
from types import TracebackType
from typing import Any

from numpy import floating
from numpy import integer
from numpy.typing import NDArray
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
    ```python
    from compas_viewer import Viewer
    from compas_viewer.gl import gl_info

    viewer = Viewer()
    gl_info()
    ```

    """
    info: str = f"""
        Vendor: {GL.glGetString(GL.GL_VENDOR)}
        Renderer: {GL.glGetString(GL.GL_RENDERER)}
        OpenGL Version: {GL.glGetString(GL.GL_VERSION)}
        Shader Version: {GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION)}
        """

    return info


type FloatBufferData = Sequence[float] | NDArray[floating[Any]]
type IndexBufferData = Sequence[int] | NDArray[integer[Any]]


def make_vertex_buffer(data: FloatBufferData, dynamic: bool = False) -> int:
    """Make a vertex buffer from the given data.

    Parameters
    ----------
    data
        A flat list of floats.
    dynamic
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
    c_data = (ct.c_float * n)(*data)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, size, c_data, access)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
    return vbo


def make_index_buffer(data: IndexBufferData, dynamic: bool = False) -> int:
    """Make an element buffer from the given data.

    Parameters
    ----------
    data
        A flat list of ints.
    dynamic
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
    c_data = (ct.c_int * n)(*data)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, vbo)
    GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, size, c_data, access)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
    return vbo


def update_vertex_buffer(data: FloatBufferData, buffer: int, offset: int = 0) -> None:
    """Update a vertex buffer with new data.

    Parameters
    ----------
    data
        A flat list of floats.
    buffer
        The ID of the buffer.
    offset
        Byte offset into the buffer where the update should start.

    """
    n = len(data)
    size = n * ct.sizeof(ct.c_float)
    c_data = (ct.c_float * n)(*data)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, buffer)
    GL.glBufferSubData(GL.GL_ARRAY_BUFFER, offset, size, c_data)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)


def update_index_buffer(data: IndexBufferData, buffer: int) -> None:
    """Update an index buffer with new data.

    Parameters
    ----------
    data
        A flat list of ints.
    buffer
        The ID of the buffer.

    """
    n = len(data)
    size = n * ct.sizeof(ct.c_uint)
    c_data = (ct.c_int * n)(*data)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, buffer)
    GL.glBufferSubData(GL.GL_ELEMENT_ARRAY_BUFFER, 0, size, c_data)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)


def make_texture_buffer(data: NDArray[floating], internal_format: int = GL.GL_RGBA32F) -> int:
    """Make a texture buffer from the given data.

    Parameters
    ----------
    data
        A numpy array of floats.
    internal_format
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


def update_texture_buffer(data: NDArray[floating], texture: int, offset: int = 0) -> None:
    """Update a texture buffer with new data.

    Parameters
    ----------
    data
        A numpy array of floats.
    texture
        The texture ID.
    offset
        Byte offset into the buffer where the update should start.

    """
    GL.glBindTexture(GL.GL_TEXTURE_BUFFER, texture)
    buffer = GL.glGetTexLevelParameteriv(GL.GL_TEXTURE_BUFFER, 0, GL.GL_TEXTURE_BUFFER_DATA_STORE_BINDING)
    GL.glBindBuffer(GL.GL_TEXTURE_BUFFER, buffer)
    GL.glBufferSubData(GL.GL_TEXTURE_BUFFER, offset, data.nbytes, data)
    GL.glBindBuffer(GL.GL_TEXTURE_BUFFER, 0)


class OffscreenBufferContext:
    """Context manager for offscreen rendering with automatic cleanup.

    This class provides a safe way to render to an offscreen framebuffer object (FBO)
    with automatic setup and cleanup of OpenGL resources.

    Parameters
    ----------
    width
        Width of the offscreen buffer in pixels.
    height
        Height of the offscreen buffer in pixels.

    Examples
    --------
    >>> with OffscreenBufferContext(800, 600) as fbo:
    ...     # Render to offscreen buffer
    ...     GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    ...     # ... render scene ...
    ...     # Read pixels if needed
    ...     pixels = GL.glReadPixels(0, 0, 800, 600, GL.GL_RGB, GL.GL_UNSIGNED_BYTE)

    """

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.fbo = None
        self.texture = None
        self.depth_buffer = None
        self.previous_fbo = None
        self.viewport = None

    def __enter__(self) -> "OffscreenBufferContext":
        """Set up offscreen rendering context."""
        # Store current state
        self.viewport = GL.glGetIntegerv(GL.GL_VIEWPORT)
        self.previous_fbo = GL.glGetIntegerv(GL.GL_FRAMEBUFFER_BINDING)

        # Create framebuffer
        self.fbo = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo)

        # Create and configure color texture
        self.texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA8, self.width, self.height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None)

        # Set texture parameters for nearest neighbor sampling
        for param in [GL.GL_TEXTURE_MIN_FILTER, GL.GL_TEXTURE_MAG_FILTER]:
            GL.glTexParameteri(GL.GL_TEXTURE_2D, param, GL.GL_NEAREST)
        for param in [GL.GL_TEXTURE_WRAP_S, GL.GL_TEXTURE_WRAP_T]:
            GL.glTexParameteri(GL.GL_TEXTURE_2D, param, GL.GL_CLAMP_TO_EDGE)

        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, self.texture, 0)

        # Create depth buffer
        self.depth_buffer = GL.glGenRenderbuffers(1)
        GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, self.depth_buffer)
        GL.glRenderbufferStorage(GL.GL_RENDERBUFFER, GL.GL_DEPTH_COMPONENT24, self.width, self.height)
        GL.glFramebufferRenderbuffer(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT, GL.GL_RENDERBUFFER, self.depth_buffer)

        # Verify framebuffer completeness
        status = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)
        if status != GL.GL_FRAMEBUFFER_COMPLETE:
            self._cleanup()
            raise RuntimeError(f"Framebuffer is not complete! Status: {status}")

        # Set viewport for offscreen rendering
        GL.glViewport(0, 0, self.width, self.height)

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Clean up offscreen rendering context."""
        self._cleanup()

        # Restore previous state
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.previous_fbo)
        assert self.viewport is not None
        GL.glViewport(*self.viewport)

    def _cleanup(self) -> None:
        """Clean up OpenGL resources."""
        if self.depth_buffer:
            GL.glDeleteRenderbuffers(1, [self.depth_buffer])
        if self.texture:
            GL.glDeleteTextures(1, [self.texture])
        if self.fbo:
            GL.glDeleteFramebuffers(1, [self.fbo])
