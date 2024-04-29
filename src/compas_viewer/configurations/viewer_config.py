from pathlib import Path

from compas.colors import Color
from compas_viewer import HERE

from .config import Config


class ViewerConfig(Config):
    """
    The class representation for the `viewer.json` of the viewer.
    The viewer.json contains all the settings about the general (default) appearance of the scene objects.

    Parameters
    ----------
    pointcolor : :class:`compas.colors.Color`
        The default color of the points.
    linecolor : :class:`compas.colors.Color`
        The default color of the lines.
    surfacecolor : :class:`compas.colors.Color`
        The default color of the surfaces.
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
        pointcolor: Color,
        linecolor: Color,
        surfacecolor: Color,
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

        self.pointcolor = pointcolor
        self.linecolor = linecolor
        self.surfacecolor = surfacecolor
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
    def from_default(cls) -> "ViewerConfig":
        """
        Load the default configuration.
        """
        viewer_config = ViewerConfig.from_json(Path(HERE, "configurations", "default_config", "viewer.json"))
        if not isinstance(viewer_config, ViewerConfig):
            raise TypeError(f"The {viewer_config} is not a valid scene configuration file.")
        return viewer_config

    @classmethod
    def from_json(cls, filepath) -> "ViewerConfig":
        viewer_config = super().from_json(filepath)
        if not isinstance(viewer_config, ViewerConfig):
            raise TypeError(f"The {filepath} is not a valid scene configuration file.")
        return viewer_config
