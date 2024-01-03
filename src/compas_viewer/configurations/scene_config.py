from pathlib import Path
from typing import TypedDict

from compas.colors import Color

from compas_viewer import DATA
from compas_viewer.configurations import Config


class SceneConfigType(TypedDict):
    """
    The type template for the `scene.json`.
    """

    pointscolor: Color
    linescolor: Color
    facescolor: Color
    show_points: bool
    show_lines: bool
    show_faces: bool
    lineswidth: float
    pointssize: float
    opacity: float
    hide_coplanaredges: bool
    use_vertexcolors: bool


class SceneConfig(Config):
    """
    The class representation for the `scene.json` of the class :class:`compas_viewer.scene.ViewerSceneObject`
    The scene.json contains all the settings about the general (default) appearance of the scene objects.

    Parameters
    ----------
    config : :class:`SceneConfigType`
        A TypedDict with defined keys and types.

    """

    def __init__(self, config: SceneConfigType):
        super().__init__(config)

        self.pointscolor = config["pointscolor"]
        self.linescolor = config["linescolor"]
        self.facescolor = config["facescolor"]
        self.show_points = config["show_points"]
        self.show_lines = config["show_lines"]
        self.show_faces = config["show_faces"]
        self.lineswidth = config["lineswidth"]
        self.pointssize = config["pointssize"]
        self.opacity = config["opacity"]
        self.hide_coplanaredges = config["hide_coplanaredges"]
        self.use_vertexcolors = config["use_vertexcolors"]

    @classmethod
    def from_default(cls) -> "SceneConfig":
        """
        Load the default configuration.
        """
        scene_config = SceneConfig.from_json(Path(DATA, "default_config", "scene.json"))
        assert isinstance(scene_config, SceneConfig)
        return scene_config

    @classmethod
    def from_json(cls, filepath) -> "SceneConfig":
        scene_config = super().from_json(filepath)
        assert isinstance(scene_config, SceneConfig)
        return scene_config
