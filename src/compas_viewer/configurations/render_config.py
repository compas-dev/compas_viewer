from pathlib import Path
from typing import Literal
from typing import Tuple
from typing import Type
from typing import TypedDict

from compas.colors import Color

from compas_viewer import DATA
from compas_viewer.configurations import Config


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

    def __init__(self, config: CameraConfigType) -> None:
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
    gridsize: Tuple[float, float, int, int]
    viewmode: Literal["front", "right", "top", "perspective"]
    rendermode: Literal["wireframe", "shaded", "ghosted", "lighted"]
    backgroundcolor: Color
    selectioncolor: Color
    ghostopacity: float
    camera: CameraConfig


class RenderConfig(Config):
    """
    The class representation for the `render.json` of the class :class:`compas_viewer.components.Render`
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
        self.viewmode = config["viewmode"]
        self.rendermode = config["rendermode"]
        self.backgroundcolor = config["backgroundcolor"]
        self.selectioncolor = config["selectioncolor"]
        self.ghostopacity = config["ghostopacity"]
        self.camera = config["camera"]

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
