from pathlib import Path
from typing import Literal
from typing import TypedDict

from compas.colors import Color

from compas_viewer import DATA
from .config import Config


class SelectorConfigType(TypedDict):
    enable_selector: bool
    selectioncolor: Color


class SelectorConfig(Config):
    """
    The class representation of a selector class Selector.
    It contains all the settings about the selector: enable_selector, selectioncolor, ...

    Parameters
    ----------
    config : SelectorConfigType
        A TypedDict with defined keys and types.

    See Also
    --------
    :class:`compas_viewer.components.renderer.selector.Selector`

    """

    def __init__(self, config: SelectorConfigType):
        super().__init__(config)
        self.enable_selector = config["enable_selector"]
        self.selectioncolor = config["selectioncolor"]

    @classmethod
    def from_json(cls, filepath) -> "SelectorConfig":
        selector_config = super().from_json(filepath)
        if not isinstance(selector_config, SelectorConfig):
            raise TypeError(f"The {filepath} is not a valid selector configuration file.")
        return selector_config


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


class CameraConfig(Config):
    """
    The class representation of a camera class Camera.
    It contains all the settings about the camera: fov, near, far, position, target, ...

    Parameters
    ----------
    config : CameraConfigType
        A TypedDict with defined keys and types.

    See Also
    --------
    :class:`compas_viewer.components.renderer.camera.Camera`

    """

    def __init__(self, config: CameraConfigType):
        super().__init__(config)
        self.fov = config["fov"]
        self.near = config["near"]
        self.far = config["far"]
        self.position = config["position"]
        self.target = config["target"]
        self.scale = config["scale"]
        self.zoomdelta = config["zoomdelta"]
        self.rotationdelta = config["rotationdelta"]
        self.pan_delta = config["pan_delta"]

    @classmethod
    def from_json(cls, filepath) -> "CameraConfig":
        camera_config = super().from_json(filepath)
        if not isinstance(camera_config, CameraConfig):
            raise TypeError(f"The {filepath} is not a valid camera configuration file.")
        return camera_config


class RenderConfigType(TypedDict):
    show_grid: bool
    gridsize: tuple[float, int, float, int]
    show_gridz: bool
    viewmode: Literal["front", "right", "top", "perspective"]
    rendermode: Literal["wireframe", "shaded", "ghosted", "lighted", "instance"]
    backgroundcolor: Color
    ghostopacity: float
    camera: CameraConfig
    selector: SelectorConfig


class RenderConfig(Config):
    """
    The class representation for the `renderer.json` of the class Renderer.
    The renderer.json contains all the settings about the renderer: background color, selection color, ...

    Parameters
    ----------
    config : :class:`RenderConfigType`
        A TypedDict with defined keys and types.

    See Also
    --------
    :class:`compas_viewer.components.renderer.Renderer`

    """

    def __init__(self, config: RenderConfigType):
        super().__init__(config)
        self.show_grid = config["show_grid"]
        self.gridsize = config["gridsize"]
        self.show_gridz = config["show_gridz"]
        self.viewmode = config["viewmode"]
        self.rendermode = config["rendermode"]
        self.backgroundcolor = config["backgroundcolor"]
        self.ghostopacity = config["ghostopacity"]
        self.camera = config["camera"]
        self.selector = config["selector"]

    @classmethod
    def from_default(cls) -> "RenderConfig":
        """
        Load the default configuration.
        """
        render_config = RenderConfig.from_json(Path(DATA, "default_config", "renderer.json"))
        if not isinstance(render_config, RenderConfig):
            raise TypeError(f"The {render_config} is not a valid renderer configuration file.")
        return render_config

    @classmethod
    def from_json(cls, filepath) -> "RenderConfig":
        render_config = super().from_json(filepath)
        if not isinstance(render_config, RenderConfig):
            raise TypeError(f"The {filepath} is not a valid renderer configuration file.")
        return render_config
