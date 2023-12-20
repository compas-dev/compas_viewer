from pathlib import Path
from typing import Literal
from typing import Tuple
from typing import TypedDict

from graphviz import render

from compas_viewer import DATA
from compas_viewer.configurations import Config


class CameraConfigData(TypedDict):
    fov: float
    near: float
    far: float
    position: Tuple[float, float, float]
    target: Tuple[float, float, float]
    scale: float
    zoom_delta: float
    rotation_delta: float
    pan_delta: float


class CameraConfig(Config):
    """
    The class representation of a camera instance : :class:`compas_viewer.components.renders.camera.Camera`
    It contains all the settings about the camera: fov, near, far, position, target, ...

    Parameters
    ----------
    config : CameraConfigData
        A TypedDict with defined keys and types.

    """

    def __init__(self, config: CameraConfigData) -> None:
        super().__init__(config)
        self.fov = config["fov"]
        self.near = config["near"]
        self.far = config["far"]
        self.position = config["position"]
        self.target = config["target"]
        self.scale = config["scale"]
        self.zoom_delta = config["zoom_delta"]
        self.rotation_delta = config["rotation_delta"]
        self.pan_delta = config["pan_delta"]

    @classmethod
    def from_json(cls, filepath) -> "CameraConfig":
        camera_config = super().from_json(filepath)
        assert isinstance(camera_config, CameraConfig)
        return camera_config


class RenderConfigData(TypedDict):
    show_grid: bool
    grid_size: Tuple[float, float, int, int]
    viewmode: Literal["front", "right", "top", "perspective"]
    rendermode: Literal["wireframe", "shaded", "ghosted", "lighted"]
    background_color: Tuple[float, float, float, float]
    selection_color: Tuple[float, float, float, float]
    ghost_opacity: float
    camera: CameraConfig


class RenderConfig(Config):
    """
    The class representation for the `render.json` of the class : :class:`compas_viewer.components.Render`
    The render.json contains all the settings about the render: background color, selection color, ...

    Parameters
    ----------
    config : RenderConfigData
        A TypedDict with defined keys and types.

    """

    def __init__(self, config: RenderConfigData) -> None:
        super().__init__(config)
        self.show_grid = config["show_grid"]
        self.grid_size = config["grid_size"]
        self.viewmode = config["viewmode"]
        self.rendermode = config["rendermode"]
        self.background_color = config["background_color"]
        self.selection_color = config["selection_color"]
        self.ghost_opacity = config["ghost_opacity"]
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

