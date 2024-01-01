import select
from gc import enable
from pathlib import Path
from typing import Literal
from typing import Tuple
from typing import TypedDict

from compas.colors import Color

from compas_viewer import DATA
from compas_viewer.configurations import Config


class SelectorConfigType(TypedDict):
    enable_selector: bool
    selectioncolor: Color


class SelectorConfig(Config):
    """
    The class representation of a selector class :class:`compas_viewer.components.render.selector.Selector`
    It contains all the settings about the selector: enable_selector, selectioncolor, ...

    Parameters
    ----------
    config : SelectorConfigType
        A TypedDict with defined keys and types.

    """

    def __init__(self, config: SelectorConfigType):
        super().__init__(config)
        self.enable_selector = config["enable_selector"]
        self.selectioncolor = config["selectioncolor"]

    @classmethod
    def from_json(cls, filepath) -> "SelectorConfig":
        selector_config = super().from_json(filepath)
        assert isinstance(selector_config, SelectorConfig)
        return selector_config


class CameraConfigType(TypedDict):
    fov: float
    near: float
    far: float
    position: Tuple[float, float, float]
    target: Tuple[float, float, float]
    scale: float
    zoomdelta: float
    rotationdelta: float
    pan_delta: float


class CameraConfig(Config):
    """
    The class representation of a camera class :class:`compas_viewer.components.render.camera.Camera`
    It contains all the settings about the camera: fov, near, far, position, target, ...

    Parameters
    ----------
    config : CameraConfigType
        A TypedDict with defined keys and types.

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
        assert isinstance(camera_config, CameraConfig)
        return camera_config


class RenderConfigType(TypedDict):
    show_grid: bool
    gridsize: Tuple[float, int, float, int]
    show_gridz: bool
    viewmode: Literal["front", "right", "top", "perspective"]
    rendermode: Literal["wireframe", "shaded", "ghosted", "lighted", "instance"]
    backgroundcolor: Color
    ghostopacity: float
    camera: CameraConfig
    selector: SelectorConfig


class RenderConfig(Config):
    """
    The class representation for the `render.json` of the class :class:`compas_viewer.components.render.Render`
    The render.json contains all the settings about the render: background color, selection color, ...

    Parameters
    ----------
    config : :class:`RenderConfigType`
        A TypedDict with defined keys and types.

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
        render_config = RenderConfig.from_json(Path(DATA, "default_config", "render.json"))
        assert isinstance(render_config, RenderConfig)
        return render_config

    @classmethod
    def from_json(cls, filepath) -> "RenderConfig":
        render_config = super().from_json(filepath)
        assert isinstance(render_config, RenderConfig)
        return render_config
