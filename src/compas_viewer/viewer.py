import sys
from pathlib import Path
from typing import Callable
from typing import Literal
from typing import Optional
from typing import Union

from compas.datastructures import Datastructure
from compas.geometry import Geometry
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMainWindow

from compas_viewer.actions import Action
from compas_viewer.actions import register
from compas_viewer.components import Renderer
from compas_viewer.configurations import ActionConfig
from compas_viewer.configurations import ControllerConfig
from compas_viewer.configurations import LayoutConfig
from compas_viewer.configurations import RendererConfig
from compas_viewer.configurations import ViewerConfig
from compas_viewer.controller import Controller
from compas_viewer.layout import Layout
from compas_viewer.qt import Timer
from compas_viewer.scene.scene import ViewerScene
from compas_viewer.scene.sceneobject import ViewerSceneObject


class Viewer:
    """
    The Viewer class is the main entry of the viewer. It contains the scene and create the GUI application.

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
    rendermode : Literal['shaded', 'ghosted', 'wireframe', 'lighted'], optional
        The display mode of the OpenGL view. It will override the value in the config file.
    viewmode : Literal['front', 'right', 'top', 'perspective'], optional
        The view mode of the OpenGL view. It will override the value in the config file.
        In 'ghosted' mode, all objects have a default opacity of 0.7.
    show_grid : bool, optional
        Show the XY plane. It will override the value in the config file.
    configpath : str, optional
        The path to the config folder.

    Attributes
    ----------
    scene : :class:`compas_viewer.scene.ViewerScene`
        The scene of the viewer.
    render : :class:`compas_viewer.components.render.Render`
        The render component of the viewer.
    controller : :class:`compas_viewer.controller.Controller`
        The controller component of the viewer.
    layout : :class:`compas_viewer.layout.Layout`
        The layout component of the viewer.

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
    .. code-block:: python

        from compas_viewer import Viewer
        viewer = Viewer()
        viewer.show()
    """

    def __init__(
        self,
        title: Optional[str] = None,
        fullscreen: Optional[bool] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        rendermode: Optional[Literal["wireframe", "shaded", "ghosted", "lighted", "instance"]] = None,
        viewmode: Optional[Literal["front", "right", "top", "perspective"]] = None,
        show_grid: Optional[bool] = None,
        configpath: Optional[str] = None,
    ):
        # Custom or default config
        if configpath is None:
            self.renderer_config = RendererConfig.from_default()
            self.viewer_config = ViewerConfig.from_default()
            self.controller_config = ControllerConfig.from_default()
            self.layout_config = LayoutConfig.from_default()
        else:
            self.renderer_config = RendererConfig.from_json(Path(configpath, "renderer.json"))
            self.viewer_config = ViewerConfig.from_json(Path(configpath, "scene.json"))
            self.controller_config = ControllerConfig.from_json(Path(configpath, "controller.json"))
            self.layout_config = LayoutConfig.from_json(Path(configpath, "layout.json"))

        #  In-code config
        if title is not None:
            self.layout_config.window.title = title
        if fullscreen is not None:
            self.layout_config.window.fullscreen = fullscreen
        if width is not None:
            self.layout_config.window.width = width
        if height is not None:
            self.layout_config.window.height = height
        if rendermode is not None:
            self.renderer_config.rendermode = rendermode
        if viewmode is not None:
            self.renderer_config.viewmode = viewmode
        if show_grid is not None:
            self.renderer_config.show_grid = show_grid

        # Viewer
        self.config = self.viewer_config

        #  Application
        self.started = False
        self.app = QCoreApplication.instance() or QApplication(sys.argv)
        self.window = QMainWindow()

        # Scene
        self.scene = ViewerScene(self, name=self.layout_config.window.title, context="Viewer")

        # Controller
        self.controller = Controller(self, self.controller_config)

        # Render
        self.renderer = Renderer(self, self.renderer_config)

        # Layout
        self.layout = Layout(self, self.layout_config)
        self.layout.init()

        # `on` function
        self.timer: Timer
        self.frame_count: int = 0

        #  Primitive
        self.objects: list[ViewerSceneObject]

    # ==========================================================================
    # Scene
    # ==========================================================================

    def add(self, item: Union[Geometry, Datastructure, ViewerSceneObject], *args, **kwargs):
        """
        Add an item to the scene.
        This is a compatibility function for the old version of the viewer.
        While :func:`compas.scene.Scene.add` is the recommended way to add an item to the scene.

        Parameters
        ----------
        item : :class:`compas.geometry.Geometry`, :class:`compas.datastructures.Datastructure`,
            :class:`compas_viewer.scene.ViewerSceneObject`
            The item to be added to the scene.
        *args : list
            Additional arguments for the :class:`compas_viewer.scene.ViewerSceneObject`.
        **kwargs : dict
            Additional options for the :class:`compas_viewer.scene.ViewerSceneObject`.

        Returns
        -------
        :class:`compas_viewer.scene.sceneobject.ViewerSceneObject`
            The scene object.
        """

        return self.scene.add(*args, **kwargs)

    # ==========================================================================
    # Runtime
    # ==========================================================================

    def show(self):
        """Show the viewer window."""
        # opengel being initialized:
        self.window.show()
        self.started = True
        # stop point of the main thread:
        self.app.exec_()

    def on(self, interval: int, timeout: Optional[int] = None, frames: Optional[int] = None) -> Callable:
        """Decorator for callbacks of a dynamic drawing process.

        Parameters
        ----------
        interval : int
            Interval between subsequent calls to this function, in milliseconds.
        timeout : int, optional
            Timeout between subsequent calls to this function, in milliseconds.
        frames : int, optional
            The number of frames of the process.
            If no frame number is provided, the process continues until the viewer is closed.

        Returns
        -------
        Callable

        Notes
        -----
        The difference between `interval` and `timeout` is that the former indicates
        the time between subsequent calls to the callback,
        without taking into account the duration of the execution of the call,
        whereas the latter indicates a pause after the completed execution of the previous call,
        before starting the next one.

        Examples
        --------
        .. code-block:: python

            angle = math.radians(5)

            @viewer.on(interval=1000)
            def rotate(frame):
                obj.rotation = [0, 0, frame * angle]
                obj.update()

        """
        if (not interval and not timeout) or (interval and timeout):
            raise ValueError("Must specify either interval or timeout.")

        def outer(func: Callable):
            def renderer():
                func(self.frame_count)
                self.renderer.update()
                self.frame_count += 1
                if frames is not None and self.frame_count >= frames:
                    self.timer.stop()

            if interval:
                self.timer = Timer(interval=interval, callback=renderer)
            if timeout:
                self.timer = Timer(interval=timeout, callback=renderer, singleshot=True)

            self.frame_count = 0

        return outer

    # ==========================================================================
    # Action
    # ==========================================================================

    def add_action(
        self,
        pressed_action: Callable,
        key: str,
        released_action: Optional[Callable] = None,
        modifier: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """Add a custom action to the viewer.

        Parameters
        ----------
        pressed_action : Callable
            The function to be called when the key is pressed.
        key : str
            The key to be pressed.
        released_action : Callable, optional
            The function to be called when the key is released.
            Default to None.
        modifier : str, optional
            The modifier of the key.
            Default to None.
        name : str, optional
            The name of the action.
            Default to the name of the pressed_action function.

        Returns
        -------
        :class:`compas_viewer.actions.Action`
            The action object.

        Examples
        --------
        .. code-block:: python

            from compas.geometry import Scale
            from compas.geometry import Transformation
            from compas_viewer import Viewer
            viewer = Viewer()
            faces = viewer.scene.add(Mesh.from_obj(compas.get("faces.obj")))
            faces.transformation = Transformation()
            def pressed_action():
                faces.transformation *= Scale.from_factors([1.1, 1.1, 1.1], Frame.worldXY())
                faces.update()
            action = viewer.add_action(pressed_action, "p")
            viewer.show()

        """

        if name is None:
            name = pressed_action.__name__
        if modifier is None:
            modifier = "no"

        class CustomAction(Action):
            def pressed_action(self):
                pressed_action()

            def released_action(self):
                if released_action:
                    released_action()

        register(name, CustomAction)

        action = CustomAction(name, self, ActionConfig(key, modifier))

        self.controller.actions[name] = action

        return action
