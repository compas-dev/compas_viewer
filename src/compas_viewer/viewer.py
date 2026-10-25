import sys
from collections.abc import Callable
from io import BytesIO
from pathlib import Path
from typing import Any
from typing import Literal
from typing import cast

from PySide6.QtCore import QBuffer
from PySide6.QtCore import QByteArray
from PySide6.QtCore import QIODevice
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor
from PySide6.QtGui import QIcon
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

from compas.colors import Color
from compas.scene import Scene
from compas_viewer import HERE
from compas_viewer.animation import ANIMATION_PRESETS
from compas_viewer.animation import AnimationPreset
from compas_viewer.commandregistry import CommandRegistry
from compas_viewer.commands import Command
from compas_viewer.commands import builtin_commands
from compas_viewer.config import Appearance
from compas_viewer.config import Config
from compas_viewer.config import Unit
from compas_viewer.events import EventManager
from compas_viewer.mouse import Mouse
from compas_viewer.plugins import ensure_scene_objects_registered
from compas_viewer.renderer import Renderer
from compas_viewer.scene import ViewerScene
from compas_viewer.scene import ViewerSceneObject
from compas_viewer.singleton import Singleton
from compas_viewer.state import ViewerState
from compas_viewer.ui import UI
from compas_viewer.uidefinitions import UIItem
from compas_viewer.uidefinitions import default_menu_items
from compas_viewer.uidefinitions import default_sidebar_items


class Viewer(Singleton):
    """Coordinate the application, scene, renderer, events, and user interface.

    Parameters
    ----------
    config
        Viewer configuration. A default configuration is created when omitted.
    **kwargs
        Reserved keyword arguments for compatibility with viewer subclasses.

    """

    def __init__(self, config: Config | None = None, **kwargs: Any) -> None:
        ensure_scene_objects_registered()
        self.app = self.create_app()
        self.running = False
        self._scene: ViewerScene | None = None

        self.config = config or Config()
        self.state = ViewerState(self.config)
        self.state.changed.connect(self._on_state_changed)
        self.commands = CommandRegistry(builtin_commands())
        self.menu_items: list[UIItem] = default_menu_items()
        self.toolbar_items: list[UIItem] = []
        self.sidebar_items: list[UIItem] = default_sidebar_items()
        self.app.styleHints().colorSchemeChanged.connect(self._on_system_color_scheme_changed)
        self.set_appearance(self.config.ui.appearance)
        self.timer = QTimer()
        self.mouse = Mouse()

        self.eventmanager = EventManager()
        self.ui = UI()

    @property
    def renderer(self) -> Renderer:
        """The renderer displayed by the main viewport."""
        return self.ui.viewport.renderer

    @property
    def scene(self) -> ViewerScene:
        """The active viewer scene, created lazily on first access."""
        if self._scene is None:
            self._scene = ViewerScene()
        return self._scene

    @scene.setter
    def scene(self, scene: Scene) -> None:
        """Replace the active scene from serialized COMPAS scene data."""
        self._scene = ViewerScene.__from_data__(scene.__data__)
        if self.running:
            for obj in self._scene.objects:
                cast(ViewerSceneObject, obj).init()

    def create_app(self) -> QApplication:
        """Create and configure the Qt application.

        Returns
        -------
        QApplication
            Configured application instance.

        """
        app = QApplication(sys.argv)
        app.setApplicationName("COMPAS Viewer")
        app.setApplicationDisplayName("COMPAS Viewer")
        app.setWindowIcon(QIcon(str(HERE / "assets" / "icons" / "compas_icon_white.png")))
        return app

    def register_command(self, identifier: str, command: Command, *, replace: bool = False) -> None:
        """Register a runtime command and activate its input bindings.

        Parameters
        ----------
        identifier
            Stable, namespaced command identifier.
        command
            Command contributed by the application or a plugin.
        replace
            Whether an existing registration may be replaced.

        """
        replacing = identifier in self.commands
        self.commands.register(identifier, command, replace=replace)
        if replacing:
            self.eventmanager.reload_bindings()
        else:
            self.eventmanager.register_command(command)

    def add_menu_item(self, menu: str, item: UIItem) -> None:
        """Contribute an item to a top-level runtime menu.

        Parameters
        ----------
        menu
            Title of the top-level menu. A new menu is created when necessary.
        item
            Menu item definition, normally referring to a registered command
            through its stable identifier.

        """
        for definition in self.menu_items:
            if definition.get("title") == menu:
                definition.setdefault("items", []).append(item)
                break
        else:
            self.menu_items.append({"title": menu, "items": [item]})
        self.ui.menubar.reload()

    def set_appearance(self, appearance: Appearance) -> None:
        """Apply a system, light, or dark application appearance.

        Parameters
        ----------
        appearance
            Appearance to apply. System appearance follows the platform color
            scheme and updates when that scheme changes.

        """
        if appearance not in {"system", "light", "dark"}:
            raise ValueError(f"Unsupported appearance: {appearance!r}.")

        if not self.state.set("ui.appearance", appearance):
            self._apply_appearance(appearance)

    def _apply_appearance(self, appearance: Appearance) -> None:
        """Apply an appearance without changing the selected state value."""
        effective = self._system_appearance() if appearance == "system" else appearance
        self.app.setPalette(self._appearance_palette(effective))
        self.state.set("renderer.backgroundcolor", Color.from_hex("#1e1e1e") if effective == "dark" else Color.white())
        if hasattr(self, "ui"):
            self.renderer.update()

    def _on_state_changed(self, path: str, value: object) -> None:
        """Apply viewer-owned effects for a changed state value."""
        if path == "ui.appearance":
            self._apply_appearance(cast(Appearance, value))

    def _on_system_color_scheme_changed(self, _scheme: Qt.ColorScheme) -> None:
        """Reapply system appearance after a platform theme change."""
        if self.config.ui.appearance == "system":
            self._apply_appearance("system")

    def _system_appearance(self) -> Literal["light", "dark"]:
        """Return the effective appearance reported by the platform."""
        scheme = self.app.styleHints().colorScheme()
        if scheme == Qt.ColorScheme.Dark:
            return "dark"
        if scheme == Qt.ColorScheme.Light:
            return "light"
        return "dark" if self.app.palette().color(QPalette.ColorRole.Window).lightness() < 128 else "light"

    @staticmethod
    def _appearance_palette(appearance: Literal["light", "dark"]) -> QPalette:
        """Create a complete Qt palette for an effective appearance.

        Parameters
        ----------
        appearance
            Effective light or dark appearance.

        Returns
        -------
        QPalette
            Application palette for the requested appearance.

        """
        palette = QPalette()
        if appearance == "dark":
            colors = {
                QPalette.ColorRole.Window: "#2b2b2b",
                QPalette.ColorRole.WindowText: "#f0f0f0",
                QPalette.ColorRole.Base: "#1e1e1e",
                QPalette.ColorRole.AlternateBase: "#353535",
                QPalette.ColorRole.ToolTipBase: "#f0f0f0",
                QPalette.ColorRole.ToolTipText: "#202020",
                QPalette.ColorRole.Text: "#f0f0f0",
                QPalette.ColorRole.Button: "#353535",
                QPalette.ColorRole.ButtonText: "#f0f0f0",
                QPalette.ColorRole.BrightText: "#ff5c5c",
                QPalette.ColorRole.Link: "#6cb6ff",
                QPalette.ColorRole.Highlight: "#3d7eff",
                QPalette.ColorRole.HighlightedText: "#ffffff",
                QPalette.ColorRole.PlaceholderText: "#a0a0a0",
            }
        else:
            colors = {
                QPalette.ColorRole.Window: "#f0f0f0",
                QPalette.ColorRole.WindowText: "#202020",
                QPalette.ColorRole.Base: "#ffffff",
                QPalette.ColorRole.AlternateBase: "#e8e8e8",
                QPalette.ColorRole.ToolTipBase: "#ffffdc",
                QPalette.ColorRole.ToolTipText: "#202020",
                QPalette.ColorRole.Text: "#202020",
                QPalette.ColorRole.Button: "#f0f0f0",
                QPalette.ColorRole.ButtonText: "#202020",
                QPalette.ColorRole.BrightText: "#ffffff",
                QPalette.ColorRole.Link: "#0057ae",
                QPalette.ColorRole.Highlight: "#308cc6",
                QPalette.ColorRole.HighlightedText: "#ffffff",
                QPalette.ColorRole.PlaceholderText: "#707070",
            }
        for role, color in colors.items():
            palette.setColor(role, QColor(color))
        return palette

    @property
    def unit(self) -> Unit:
        """The display unit used by the viewport."""
        return self.ui.viewport.unit

    @unit.setter
    def unit(self, unit: Unit) -> None:
        """Set the display unit before the viewer starts running."""
        self.ui.viewport.unit = unit

    def show(self) -> None:
        """Initialize the interface and enter the Qt event loop."""
        self.running = True
        self.ui.init()
        self.app.exec()

    def save_image(
        self,
        filepath: str | Path,
        width: int | None = None,
        height: int | None = None,
        *,
        zoom_extents: bool = False,
    ) -> Path:
        """Render the current scene to an image without opening the viewer.

        Parameters
        ----------
        filepath
            Destination image path. The suffix determines the image format.
        width
            Image width in pixels. The configured window width is used when
            omitted.
        height
            Image height in pixels. The configured window height is used when
            omitted.
        zoom_extents
            Whether to frame all visible scene objects before rendering.

        Returns
        -------
        Path
            Path of the generated image.

        Raises
        ------
        ValueError
            If the image dimensions are invalid or the path has no suffix.
        RuntimeError
            If Qt cannot save the rendered framebuffer.

        """
        path = Path(filepath)
        if (width is not None and width < 1) or (height is not None and height < 1):
            raise ValueError("Image width and height must be positive integers.")
        if not path.suffix:
            raise ValueError("The image path must include a file extension.")

        renderer = self.renderer
        default_width = renderer.width() if self.running else self.config.window.width
        default_height = renderer.height() if self.running else self.config.window.height
        width = default_width if width is None else width
        height = default_height if height is None else height

        if width < 1 or height < 1:
            raise ValueError("Image width and height must be positive integers.")

        window = self.ui.window.widget

        if self.running:
            if zoom_extents:
                from compas_viewer.commands import zoom_extents as frame_scene

                frame_scene(self)
            image = renderer.grabFramebuffer().scaled(width, height)
        else:
            previous_minimum = renderer.minimumSize()
            previous_maximum = renderer.maximumSize()

            # A QOpenGLWidget needs an exposed native surface to create its GL
            # context. WA_DontShowOnScreen provides that surface without ever
            # presenting the viewer window to the user.
            window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
            renderer.setFixedSize(width, height)
            window.resize(width, height)
            self.running = True

            try:
                window.show()
                self.app.processEvents()
                if zoom_extents:
                    from compas_viewer.commands import zoom_extents as frame_scene

                    frame_scene(self)
                renderer.update()
                self.app.processEvents()
                image = renderer.grabFramebuffer()
            finally:
                window.hide()
                window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, False)
                renderer.setMinimumSize(previous_minimum)
                renderer.setMaximumSize(previous_maximum)
                self.running = False

        if not image.save(str(path)):
            raise RuntimeError(f"Could not save rendered image to {path}.")
        return path

    def record_animation(
        self,
        filepath: str | Path,
        update: Callable[[int], object],
        frames: int,
        *,
        preset: str | AnimationPreset = "documentation",
        width: int | None = None,
        height: int | None = None,
        fps: int | None = None,
        loop: int = 0,
        zoom_extents: bool = False,
    ) -> Path:
        """Record deterministic scene updates as an animated GIF or WebP.

        Parameters
        ----------
        filepath
            Destination ending in ``.gif`` or ``.webp``.
        update
            Callback invoked with the zero-based frame number before each
            frame is rendered.
        frames
            Number of frames to record.
        preset
            ``"preview"``, ``"documentation"``, ``"presentation"``, or a
            custom animation preset.
        width
            Frame width overriding the preset.
        height
            Frame height overriding the preset.
        fps
            Frame rate overriding the preset.
        loop
            Number of animation loops. Zero means forever.
        zoom_extents
            Whether to frame visible objects before recording.

        Returns
        -------
        Path
            Path of the generated animation.

        """
        path = Path(filepath)
        suffix = path.suffix.lower()
        if suffix not in {".gif", ".webp"}:
            raise ValueError("Animation output must use the .gif or .webp extension.")
        if frames < 1:
            raise ValueError("Animation must contain at least one frame.")
        if isinstance(preset, str):
            try:
                settings = ANIMATION_PRESETS[preset]
            except KeyError as error:
                names = ", ".join(ANIMATION_PRESETS)
                raise ValueError(f"Unknown animation preset {preset!r}. Choose from: {names}.") from error
        else:
            settings = preset

        width = settings.width if width is None else width
        height = settings.height if height is None else height
        fps = settings.fps if fps is None else fps
        if width < 1 or height < 1 or fps < 1:
            raise ValueError("Animation width, height, and fps must be positive integers.")
        if loop < 0:
            raise ValueError("Animation loop count cannot be negative.")

        renderer = self.renderer
        window = self.ui.window.widget
        was_running = self.running
        previous_minimum = renderer.minimumSize()
        previous_maximum = renderer.maximumSize()

        if not was_running:
            window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
            renderer.setFixedSize(width, height)
            window.resize(width, height)
            self.running = True

        images = []
        try:
            if not was_running:
                window.show()
                self.app.processEvents()
            if zoom_extents:
                from compas_viewer.commands import zoom_extents as frame_scene

                frame_scene(self)

            for frame in range(frames):
                update(frame)
                renderer.update()
                self.app.processEvents()
                image = renderer.grabFramebuffer()
                if image.width() != width or image.height() != height:
                    image = image.scaled(width, height)
                images.append(_qimage_to_pillow(image))
        finally:
            if not was_running:
                window.hide()
                window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, False)
                renderer.setMinimumSize(previous_minimum)
                renderer.setMaximumSize(previous_maximum)
                self.running = False

        duration = round(1000 / fps)
        first, *remaining = images
        if suffix == ".gif":
            first = first.convert("RGB").quantize(colors=settings.colors)
            remaining = [image.convert("RGB").quantize(colors=settings.colors) for image in remaining]
            first.save(path, save_all=True, append_images=remaining, duration=duration, loop=loop, optimize=settings.optimize, disposal=2)
        else:
            first.save(path, save_all=True, append_images=remaining, duration=duration, loop=loop, quality=settings.quality, method=6)
        return path

    def on(self, interval: int, frames: int | None = None) -> Callable[[Callable[[int], object]], Callable[[int], object]]:
        """Decorator for callbacks of a dynamic drawing process with fixed intervals.

        Parameters
        ----------
        interval
            Interval between subsequent calls to this function, in milliseconds.
        frames
            The number of frames of the process.
            If no frame number is provided, the process continues until the viewer is closed.

        Returns
        -------
        Callable
            The original decorated callback.

        """
        self.frame_count = 0

        def decorator(func: Callable[[int], object]) -> Callable[[int], object]:
            def wrapper() -> None:
                if frames is not None and self.frame_count >= frames:
                    self.timer.stop()
                    return
                func(self.frame_count)
                self.frame_count += 1
                self.renderer.update()

            self.timer.timeout.connect(wrapper)
            self.timer.start(interval)
            return func

        return decorator


def _qimage_to_pillow(image: Any) -> Any:
    """Convert a Qt image to a Pillow image without temporary files."""
    from PIL import Image

    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    if not image.save(buffer, "PNG"):
        raise RuntimeError("Could not encode an animation frame.")
    buffer.close()
    converted = Image.open(BytesIO(bytes(data)))
    converted.load()
    return converted
