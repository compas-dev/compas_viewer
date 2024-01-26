from pathlib import Path


from compas.colors import Color

from compas_viewer import DATA

from .config import Config


class SceneConfig(Config):
    """
    The class representation for the `scene.json` of the class ViewerSceneObject.
    The scene.json contains all the settings about the general (default) appearance of the scene objects.

    Parameters
    ----------
    pointscolor : :class:`compas.colors.Color`
        The default color of the points.
    linescolor : :class:`compas.colors.Color`
        The default color of the lines.
    facescolor : :class:`compas.colors.Color`
        The default color of the faces.
    show_points : bool
        The default setting for showing the points.
    show_lines : bool
        The default setting for showing the lines.
    show_faces : bool
        The default setting for showing the faces.
    lineswidth : float
        The default width of the lines.
    pointssize : float
        The default size of the points.
    opacity : float
        The default opacity of the objects.
    hide_coplanaredges : bool
        The default setting for hiding the coplanar edges.
    use_vertexcolors : bool
        The default setting for using the vertex colors.
    framesize : tuple[float, int, float, int]
        The default size of the frame.
    show_framez : bool
        The default setting for showing the z-axis of the frame.
    vectorsize : float
        The default size of the vectors.

    See Also
    --------
    :class:`compas_viewer.scene.ViewerSceneObject`

    """

    def __init__(
        self,
        pointscolor: Color,
        linescolor: Color,
        facescolor: Color,
        show_points: bool,
        show_lines: bool,
        show_faces: bool,
        lineswidth: float,
        pointssize: float,
        opacity: float,
        hide_coplanaredges: bool,
        use_vertexcolors: bool,
        framesize: tuple[float, int, float, int],
        show_framez: bool,
        vectorsize: float,
    ):
        super().__init__()

        self.pointscolor = pointscolor
        self.linescolor = linescolor
        self.facescolor = facescolor
        self.show_points = show_points
        self.show_lines = show_lines
        self.show_faces = show_faces
        self.lineswidth = lineswidth
        self.pointssize = pointssize
        self.opacity = opacity
        self.hide_coplanaredges = hide_coplanaredges
        self.use_vertexcolors = use_vertexcolors
        self.framesize = framesize
        self.show_framez = show_framez
        self.vectorsize = vectorsize
        if self.vectorsize < 0 or self.vectorsize > 1:
            raise ValueError("The vectorsize must be between 0 and 1.")

    @classmethod
    def from_default(cls) -> "SceneConfig":
        """
        Load the default configuration.
        """
        scene_config = SceneConfig.from_json(Path(DATA, "default_config", "scene.json"))
        if not isinstance(scene_config, SceneConfig):
            raise TypeError(f"The {scene_config} is not a valid scene configuration file.")
        return scene_config

    @classmethod
    def from_json(cls, filepath) -> "SceneConfig":
        scene_config = super().from_json(filepath)
        if not isinstance(scene_config, SceneConfig):
            raise TypeError(f"The {filepath} is not a valid scene configuration file.")
        return scene_config
