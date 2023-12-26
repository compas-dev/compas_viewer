import sys
from os import path
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import Union

from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Geometry
from compas.scene import Scene
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon

from compas_viewer.components import Render
from compas_viewer.configurations import RenderConfig
from compas_viewer.configurations import SceneConfig
from compas_viewer.configurations import ViewerConfig
from compas_viewer.scene.sceneobject import ViewerSceneObject

ICONS = Path(Path(__file__).parent, "_static", "icons")


class Viewer(Scene):
    """
    The Viewer class is the main entry of `compas_viewer`. It organizes the scene and create the GUI application.

    Parameters
    ----------
    title : str, optional
        The title of the viewer window.  It will override the value in the config file.
    fullscreen : bool, optional
        The fullscreen mode of the viewer window. It will override the value in the config file.
    width : int, optional
        The width of the viewer window at startup. It will override the value in the config file.
    height : int, optional
        The height of the viewer window at startup. It will override the value in the config file.
    rendermode : literal['shaded', 'ghosted', 'wireframe', 'lighted'}, optional
        The display mode of the OpenGL view. It will override the value in the config file.
    viewmode : literal['front', 'right', 'top', 'perspective'}, optional
        The view mode of the OpenGL view. It will override the value in the config file.
        In `ghosted` mode, all objects have a default opacity of 0.7.
    show_grid : bool, optional
        Show the XY plane. It will override the value in the config file.
    configpath : str, optional
        The path to the config folder.

    Attributes
    ----------
    config : :class:`compas_viewer.configurations.ViewerConfig`
        The configuration for the viewer.

    Notes
    -----
    The viewer has a (main) window with a central OpenGL widget,
    and a menubar, toolbar, and statusbar.
    The menubar provides access to all supported 'actions'.
    The toolbar is meant to be a 'quicknav' to a selected set of actions.
    The viewer supports rotate/pan/zoom, and object selection via picking or box selections.
    Currently the viewer uses OpenGL 2.2 and GLSL 120 with a 'compatibility' profile.

    Examples
    --------
    >>> from compas_viewer import Viewer # doctest: +SKIP
    >>> viewer = Viewer() # doctest: +SKIP
    >>> viewer.show() # doctest: +SKIP

    """

    def __init__(
        self,
        title: Optional[str] = None,
        fullscreen: Optional[bool] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        rendermode: Optional[Literal["wireframe", "shaded", "ghosted", "lighted"]] = None,
        viewmode: Optional[Literal["front", "right", "top", "perspective"]] = None,
        show_grid: Optional[bool] = None,
        configpath: Optional[str] = None,
    ) -> None:
        super(Viewer, self).__init__()
        # custom or default config
        if configpath is None:
            self.config = ViewerConfig.from_default()
            self.render_config = RenderConfig.from_default()
            self.scene_config = SceneConfig.from_default()
        else:
            self.config = ViewerConfig.from_json(Path(configpath, "viewer.json"))
            self.render_config = RenderConfig.from_json(Path(configpath, "render.json"))
            self.scene_config = SceneConfig.from_json(Path(configpath, "scene.json"))

        #  in-code config
        if title is not None:
            self.config.title = title
        if fullscreen is not None:
            self.config.fullscreen = fullscreen
        if width is not None:
            self.config.width = width
        if height is not None:
            self.config.height = height
        if rendermode is not None:
            self.render_config.rendermode = rendermode
        if viewmode is not None:
            self.render_config.viewmode = viewmode
        if show_grid is not None:
            self.render_config.show_grid = show_grid

        self._init()

    def __new__(cls, *args, **kwargs):
        instance = super(Viewer, cls).__new__(cls)
        Scene.viewerinstance = instance  # type: ignore
        return instance

    # ==========================================================================
    # Init functions
    # ==========================================================================

    def _init(self) -> None:
        """Initialize the components of the user interface."""
        self._glFormat = QtGui.QSurfaceFormat()
        self._glFormat.setVersion(2, 1)
        self._glFormat.setProfile(QtGui.QSurfaceFormat.CompatibilityProfile)
        self._glFormat.setDefaultFormat(self._glFormat)
        QtGui.QSurfaceFormat.setDefaultFormat(self._glFormat)
        self._app = QCoreApplication.instance() or QtWidgets.QApplication(sys.argv)
        self._app.references = set()  # type: ignore
        self._window = QtWidgets.QMainWindow()
        self._icon = QIcon(path.join(ICONS, "compas_icon_white.png"))
        self._app.setWindowIcon(self._icon)  # type: ignore
        self._app.setApplicationName(self.config.title)
        self.render = Render(self, self.render_config)
        self._window.setCentralWidget(self.render)
        self._window.setContentsMargins(0, 0, 0, 0)
        self._app.references.add(self._window)  # type: ignore
        self._window.resize(self.config.width, self.config.height)
        if self.config.fullscreen:
            self._window.setWindowState(self._window.windowState() | QtCore.Qt.WindowMaximized)
        self._init_statusbar()

    def _init_statusbar(self) -> None:
        self.statusbar = self._window.statusBar()
        self.statusbar.setContentsMargins(0, 0, 0, 0)
        self.statusText = QtWidgets.QLabel(self.config.statusbar)
        self.statusbar.addWidget(self.statusText, 1)
        if self.config.show_fps:
            self.statusFps = QtWidgets.QLabel("fps: ")
            self.statusbar.addWidget

    def _resize(self, width: int, height: int) -> None:
        """Resize the main window programmatically.

        Parameters
        ----------
        width: int
            Width of the viewer window.
        height: int
            Height of the viewer window.

        Returns
        -------
        None

        """
        self._window.resize(width, height)
        desktop = self._app.desktop()  # type: ignore
        rect = desktop.availableGeometry()
        x = int(0.5 * (rect.width() - width))
        y = int(0.5 * (rect.height() - height))
        self._window.setGeometry(x, y, width, height)
        self.config.width = width
        self.config.height = height

    # ==========================================================================
    # Messages
    # ==========================================================================

    def about(self) -> None:
        """Display the about message as defined in the config file.

        Returns
        -------
        None

        """
        QtWidgets.QMessageBox.about(self._window, "About", self.config.about)

    def info(self, message: str) -> None:
        """Display info.

        Parameters
        ----------
        message : str
            An info message.

        Returns
        -------
        None

        """
        QtWidgets.QMessageBox.information(self._window, "Info", message)

    def warning(self, message: str) -> None:
        """Display a warning.

        Parameters
        ----------
        message : str
            A warning message.

        Returns
        -------
        None

        """
        QtWidgets.QMessageBox.warning(self._window, "Warning", message)

    def critical(self, message: str) -> None:
        """Display a critical warning.

        Parameters
        ----------
        message : str
            A critical warning message.

        Returns
        -------
        None

        """
        QtWidgets.QMessageBox.critical(self._window, "Critical", message)

    def question(self, message: str) -> bool:
        """Ask a question.

        Parameters
        ----------
        message : str
            A question.

        Returns
        -------
        None

        """
        flags = QtWidgets.QMessageBox.StandardButton.Yes
        flags |= QtWidgets.QMessageBox.StandardButton.No
        response = QtWidgets.QMessageBox.question(self._window, "Question", message, flags)  # type: ignore
        if response == QtWidgets.QMessageBox.Yes:
            return True
        return False

    def confirm(self, message: str) -> bool:
        """Confirm the execution of an action.

        Parameters
        ----------
        message : str
            Message to inform the user.

        Returns
        -------
        bool
            True if the user confirms.
            False otherwise.

        Examples
        --------
        .. code-block:: python

            if viewer.confirm("Should i continue?"):
                continue

        """
        flags = QtWidgets.QMessageBox.StandardButton.Ok
        flags |= QtWidgets.QMessageBox.StandardButton.Cancel
        response = QtWidgets.QMessageBox.warning(self._window, "Confirmation", message, flags)
        if response == QtWidgets.QMessageBox.StandardButton.Ok:
            return True
        return False

    def status(self, message: str) -> None:
        """Display a message in the status bar.

        Parameters
        ----------
        message : str
            A status message.

        Returns
        -------
        None

        """
        self.statusText.setText(message)

    def fps(self, fps: int) -> None:
        """Update fps info in the status bar.

        Parameters
        ----------
        fps : int
            The number of frames per second.

        Returns
        -------
        None

        """
        self.statusFps.setText("fps: {}".format(fps))

    # ==========================================================================
    # Runtime
    # ==========================================================================

    def show(self) -> None:
        """Show the viewer window.

        Returns
        -------
        None

        """

        self.started = True
        self._window.show()
        # stop point of the main thread:
        self._app.exec_()

    # ==========================================================================
    # Scene
    # ==========================================================================

    def add(
        self,
        item: Union[Mesh, Geometry],
        name: Optional[str] = None,
        parent: Optional[ViewerSceneObject] = None,
        is_selected: bool = False,
        is_visible: bool = True,
        show_points: Optional[bool] = None,
        show_lines: Optional[bool] = None,
        show_faces: Optional[bool] = None,
        pointscolor: Optional[Union[Color, Dict[Any, List[float]]]] = None,
        linescolor: Optional[Union[Color, Dict[Any, List[float]]]] = None,
        facescolor: Optional[Union[Color, Dict[Any, List[float]]]] = None,
        lineswidth: Optional[float] = None,
        pointssize: Optional[float] = None,
        opacity: Optional[float] = None,
        hide_coplanaredges: Optional[bool] = None,
        use_vertexcolors: Optional[bool] = None,
        **kwargs
    ) -> ViewerSceneObject:
        """
        Add an item to the scene.
        This function is inherent from :class:`compas.scene.Scene` with additional functionalities.

        Parameters
        ----------
        item : :class:`compas.geometry.Geometry`
            The geometry to add to the scene.
        name : str, optional
            The name of the item.
            Default to None.
        parent : :class:`compas_viewer.scene.ViewerSceneObject`, optional
            The parent of the item.
        is_selected : bool, optional
            Whether the object is selected.
            Default to False.
        is_visible : bool, optional
            Whether to show object.
            Default to True.
        show_points : bool, optional
            Whether to show points/vertices of the object.
            It will override the value in the scene config file.
        show_lines : bool, optional
            Whether to show lines/edges of the object.
            It will override the value in the scene config file.
        show_faces : bool, optional
            Whether to show faces of the object.
            It will override the value in the scene config file.
        pointscolor : Union[:class:`compas.colors.Color`, Dict[any, :class:`compas.colors.Color`], optional
            The color or the dict of colors of the points.
            It will override the value in the scene config file.
        linescolor : Union[:class:`compas.colors.Color`, Dict[any, :class:`compas.colors.Color`], optional
            The color or the dict of colors of the lines.
            It will override the value in the scene config file.
        facescolor : Union[:class:`compas.colors.Color`, Dict[any, :class:`compas.colors.Color`], optional
            The color or the dict of colors the faces.
            It will override the value in the scene config file.
        lineswidth : float, optional
            The line width to be drawn on screen
            It will override the value in the scene config file.
        pointssize : float, optional
            The point size to be drawn on screen
            It will override the value in the scene config file.
        opacity : float, optional
            The opacity of the object.
            It will override the value in the scene config file.
        hide_coplanaredges : bool, optional
            Whether to hide the coplanar edges of the mesh.
            It will override the value in the scene config file.
        use_vertexcolors : bool, optional
            Whether to use vertex color.
            It will override the value in the scene config file.
        **kwargs : dict
            The other possible parameters to be passed to the object.

        Returns
        -------
        :class:`compas.scene.SceneObject`
            The scene object.
        """

        sceneobject = super(Viewer, self).add(
            item=item,
            parent=parent,
            name=name,
            viewer=self,
            is_selected=is_selected,
            is_visible=is_visible,
            show_points=show_points,
            show_lines=show_lines,
            show_faces=show_faces,
            pointscolor=pointscolor,
            linescolor=linescolor,
            facescolor=facescolor,
            lineswidth=lineswidth,
            pointssize=pointssize,
            opacity=opacity,
            hide_coplanaredges=hide_coplanaredges,
            use_vertexcolors=use_vertexcolors,
            config=self.scene_config,
            **kwargs
        )
        assert isinstance(sceneobject, ViewerSceneObject)
        self.render.objects[name or str(sceneobject)] = sceneobject
        if parent:
            sceneobject.parent = parent
        return sceneobject
