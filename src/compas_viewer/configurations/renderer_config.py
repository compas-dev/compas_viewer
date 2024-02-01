from pathlib import Path
from typing import Literal
from typing import TypedDict

from compas.colors import Color

from compas_viewer import HERE

from .config import Config


class SelectorConfig:
    """
    The class representation of a selector class Selector.
    It contains all the settings about the selector: enable_selector, selectioncolor, ...

    Parameters
    ----------
    enable_selector : bool
        Enable the selector.
    selectioncolor : Color
        The color of the selected object.

    See Also
    --------
    :class:`compas_viewer.components.renderer.selector.Selector`
    :class:`compas_viewer.configurations.render_config.RendererConfig`

    """

    def __init__(self, enable_selector: bool, selectioncolor: Color):
        super().__init__()
        self.enable_selector = enable_selector
        self.selectioncolor = selectioncolor


class CameraConfig:
    """
    The class representation of a camera class Camera.
    It contains all the settings about the camera: fov, near, far, position, target, ...

    Parameters
    ----------
    fov : float
        The field of view of the camera.
    near : float
        The near clipping plane of the camera.
    far : float
        The far clipping plane of the camera.
    position : tuple[float, float, float]
        The position of the camera.
    target : tuple[float, float, float]
        The target of the camera.
    scale : float
        The scale of the camera.
    zoomdelta : float
        The zoom delta of the camera.
    rotationdelta : float
        The rotation delta of the camera.
    pan_delta : float
        The pan delta of the camera.

    See Also
    --------
    :class:`compas_viewer.components.renderer.camera.Camera`
    :class:`compas_viewer.configurations.render_config.RendererConfig`
    """

    def __init__(
        self,
        fov: float,
        near: float,
        far: float,
        position: tuple[float, float, float],
        target: tuple[float, float, float],
        scale: float,
        zoomdelta: float,
        rotationdelta: float,
        pan_delta: float,
    ):
        super().__init__()
        self.fov = fov
        self.near = near
        self.far = far
        self.position = position
        self.target = target
        self.scale = scale
        self.zoomdelta = zoomdelta
        self.rotationdelta = rotationdelta
        self.pan_delta = pan_delta


class RendererConfig(Config):
    """
    The class representation for the `renderer.json` of the class Renderer.
    The renderer.json contains all the settings about the renderer: background color, selection color, ...

    Parameters
    ----------
    show_grid : bool
        Whether to show the grid or not.
    gridsize : tuple[float, int, float, int]
        The size of the grid.
    show_gridz : bool
        Whether to show the z-grid or not.
    viewmode : Literal["front", "right", "top", "perspective"]
        The viewmode of the camera.
    rendermode : Literal["wireframe", "shaded", "ghosted", "lighted", "instance"]
        The rendermode of the renderer.
    backgroundcolor : Color
        The background color of the renderer.
    ghostopacity : float
        The opacity of the ghost mode.
    camera : :class:`compas_viewer.configurations.renderer_config.CameraConfigType`
        The camera configuration of the renderer.
    selector : :class:`compas_viewer.configurations.renderer_config.SelectorConfigType`
        The selector configuration of the renderer.

    Attributes
    ----------
    CameraConfigType : :class:`compas_viewer.configurations.renderer_config.CameraConfigType`
        The type template for the the camera: {fov: float, near: float, far: float, ..., pan_delta: float}
    SelectorConfigType : :class:`compas_viewer.configurations.renderer_config.SelectorConfigType`
        The type template for the the selector: {enable_selector: bool, selectioncolor: Color}

    See Also
    --------
    :class:`compas_viewer.components.renderer.Renderer`
    """

    class CameraConfigType(TypedDict):
        fov: float
        near: float
        far: float
        position: tuple[float, float, float]
        target: tuple[float, float, float]
        scale: float
        zoomdelta: float
        rotationdelta: float
        pan_delta: float

    class SelectorConfigType(TypedDict):
        enable_selector: bool
        selectioncolor: Color

    def __init__(
        self,
        show_grid: bool,
        gridsize: tuple[float, int, float, int],
        show_gridz: bool,
        viewmode: Literal["front", "right", "top", "perspective"],
        rendermode: Literal["wireframe", "shaded", "ghosted", "lighted", "instance"],
        backgroundcolor: Color,
        ghostopacity: float,
        camera: CameraConfigType,
        selector: SelectorConfigType,
    ):
        super().__init__()
        self.show_grid = show_grid
        self.gridsize = gridsize
        self.show_gridz = show_gridz
        self.viewmode = viewmode
        self.rendermode = rendermode
        self.backgroundcolor = backgroundcolor
        self.ghostopacity = ghostopacity
        self.camera = CameraConfig(**camera)
        self.selector = SelectorConfig(**selector)

    @classmethod
    def from_default(cls) -> "RendererConfig":
        """
        Load the default configuration.
        """
        render_config = RendererConfig.from_json(Path(HERE, "configurations", "default_config", "renderer.json"))
        if not isinstance(render_config, RendererConfig):
            raise TypeError(f"The {render_config} is not a valid renderer configuration file.")
        return render_config

    @classmethod
    def from_json(cls, filepath) -> "RendererConfig":
        render_config = super().from_json(filepath)
        if not isinstance(render_config, RendererConfig):
            raise TypeError(f"The {filepath} is not a valid renderer configuration file.")
        return render_config
