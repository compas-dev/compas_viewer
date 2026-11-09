import sys
from collections.abc import Callable
from collections.abc import Iterable
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import Literal
from typing import cast
from uuid import UUID

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
from compas.geometry import Transformation
from compas.scene import DistanceDimension
from compas.scene import Scene
from compas.scene import SceneObject
from compas_viewer import HERE
from compas_viewer._history import TransformTransaction
from compas_viewer._history import copy_transformation
from compas_viewer.animation import ANIMATION_PRESETS
from compas_viewer.animation import AnimationPreset
from compas_viewer.commandregistry import CommandRegistry
from compas_viewer.commands import Command
from compas_viewer.commands import builtin_commands
from compas_viewer.config import Appearance
from compas_viewer.config import Config
from compas_viewer.events import EventManager
from compas_viewer.measurement import SNAP_RADIUS
from compas_viewer.measurement import DistanceInspection
from compas_viewer.measurement import PersistentMeasurementMode
from compas_viewer.measurement import _draw_measurement_preview
from compas_viewer.mouse import Mouse
from compas_viewer.overlays import Overlay
from compas_viewer.overlays import _OverlayContext
from compas_viewer.overlays import _OverlayLayer
from compas_viewer.plugins import ensure_scene_objects_registered
from compas_viewer.renderer import Renderer
from compas_viewer.scene import ViewerScene
from compas_viewer.singleton import Singleton
from compas_viewer.state import ViewerState
from compas_viewer.ui import UI
from compas_viewer.uidefinitions import UIItem
from compas_viewer.uidefinitions import default_menu_items
from compas_viewer.uidefinitions import default_sidebar_items

if TYPE_CHECKING:
    from PySide6.QtGui import QPainter


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
        self._config = config if config is not None else Config()
        self._config.validate()
        self.app = self.create_app()
        self.running = False
        self._scene: ViewerScene | None = None
        self._overlay_layer = _OverlayLayer()
        self._undo_transforms: list[TransformTransaction] = []
        self._redo_transforms: list[TransformTransaction] = []

        self.state = ViewerState(self.config, lambda guid: self.scene.object(guid))
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
    def config(self) -> Config:
        """Config: Startup configuration owned by this viewer.

        The nested configuration values may be adjusted during setup. Replacing
        the complete configuration of an existing viewer is unsupported.
        """
        return self._config

    @property
    def renderer(self) -> Renderer:
        """The renderer displayed by the main viewport."""
        return self.ui.viewport.renderer

    @property
    def scene(self) -> ViewerScene:
        """The active viewer scene, created lazily on first access."""
        if self._scene is None:
            self._scene = ViewerScene()
            self._scene.attach(self)
        return self._scene

    @scene.setter
    def scene(self, scene: Scene) -> None:
        """Replace the active scene from serialized COMPAS scene data."""
        self.cancel_measurement()
        if isinstance(scene, ViewerScene):
            self._scene = scene
        else:
            self._scene = ViewerScene.__from_data__(scene.__data__)
            self._scene.bind_many(scene.item_store.values())
        self._scene.attach(self)
        self._clear_transform_history()
        self.state.selection.clear()
        if self.running:
            self._scene.prepare()
            for obj in self._scene.render_objects.values():
                obj.init()

    @property
    def overlays(self) -> tuple[Overlay, ...]:
        """Transient screen overlays in their drawing order."""
        return tuple(self._overlay_layer)

    def add_overlay(self, overlay: Overlay) -> None:
        """Add a transient screen overlay.

        Overlays belong to the Viewer rather than the scene. They are not
        serialized, picked, or included in scene selection.

        Parameters
        ----------
        overlay
            Scale bar or categorical legend to append to the drawing order.

        Raises
        ------
        TypeError
            If `overlay` is not an approved concrete overlay type.
        ValueError
            If the same overlay instance is already present.

        """
        self._overlay_layer.add(overlay)
        if self.running:
            self.ui.viewport.update_overlays()

    def remove_overlay(self, overlay: Overlay) -> bool:
        """Remove a transient screen overlay by identity.

        Parameters
        ----------
        overlay
            Overlay instance to remove.

        Returns
        -------
        bool
            Whether the overlay was present.

        """
        removed = self._overlay_layer.remove(overlay)
        if removed and self.running:
            self.ui.viewport.update_overlays()
        return removed

    def start_distance_inspection(self) -> None:
        """Start a one-shot transient distance inspection.

        The completed inspection remains Viewer-owned transient state until it
        is canceled, another measurement starts, or the scene is replaced.

        """
        self.state.measurement.start("inspection")

    def start_distance_dimension(self, mode: PersistentMeasurementMode = "fixed") -> None:
        """Start a one-shot persistent distance-dimension interaction.

        Parameters
        ----------
        mode
            Fixed or associative anchor acquisition. Associative acquisition
            never falls back to fixed point anchors.

        """
        self.state.measurement.start(mode)

    def cancel_measurement(self) -> bool:
        """Cancel active or retained transient measurement state.

        Returns
        -------
        bool
            Whether measurement state was cleared.

        """
        return self.state.measurement.cancel()

    def _update_measurement_hover(self, screen_point: tuple[float, float]) -> None:
        """Update the active measurement's winner and point-snap palette."""
        query = self.renderer.query_snap_context_at(screen_point, SNAP_RADIUS)
        self.state.measurement.update_hover(query)

    def _accept_measurement_at(self, screen_point: tuple[float, float]) -> None:
        """Accept the semantic snap at one screen position."""
        query = self.renderer.query_snap_context_at(screen_point, SNAP_RADIUS)
        result = self.state.measurement.accept(
            query,
            unit=self.config.measurement.unit,
            precision=self.config.measurement.precision,
        )
        if result is None or isinstance(result, DistanceInspection):
            return
        if not isinstance(result, DistanceDimension):
            raise RuntimeError("Unexpected distance measurement result.")
        sceneobject = self.scene.add(result)
        self.state.selection.replace((sceneobject,))

    def _has_overlay_content(self) -> bool:
        """Return whether the next display frame needs 2D overlay painting."""
        return bool(self._overlay_layer or self.state.measurement.has_transient_state)

    def _draw_overlays(self, renderer: Renderer, painter: "QPainter") -> None:
        """Draw Viewer-owned overlays with the active display-frame painter."""
        width = renderer.width()
        height = renderer.height()
        measurement = self.state.measurement
        if (not self._overlay_layer and not measurement.has_transient_state) or width <= 0 or height <= 0:
            return
        if self._overlay_layer:
            context = _OverlayContext(
                width=width,
                height=height,
                camera_distance=renderer.camera.distance,
                field_of_view=renderer.camera.fov,
                perspective=renderer.view == "perspective",
                unit=self.config.measurement.unit,
                precision=self.config.measurement.precision,
            )
            self._overlay_layer.draw(painter, context)
        if measurement.has_transient_state:
            _draw_measurement_preview(
                painter,
                measurement,
                renderer.project_point,
                unit=self.config.measurement.unit,
                precision=self.config.measurement.precision,
            )

    def create_app(self) -> QApplication:
        """Return the configured Qt application, creating it if necessary.

        Returns
        -------
        QApplication
            Configured application instance.

        Raises
        ------
        RuntimeError
            If a non-GUI Qt core application already exists in the process.

        """
        instance = QApplication.instance()
        if instance is None:
            app = QApplication(sys.argv)
        elif isinstance(instance, QApplication):
            app = instance
        else:
            raise RuntimeError("COMPAS Viewer cannot start after a non-GUI Qt core application has been created.")
        app.setApplicationName(self.config.window.title)
        app.setApplicationDisplayName(self.config.window.title)
        app.setWindowIcon(QIcon(str(self._window_icon_path())))
        return app

    def _window_icon_path(self) -> Path:
        """Return the configured absolute icon path or the packaged default."""
        icon = self.config.window.icon
        if icon is None:
            return HERE / "assets" / "icons" / "compas_icon_white.png"
        return Path(icon)

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

    def transform_objects(
        self,
        objects: Iterable[SceneObject],
        transformation: Transformation,
        *,
        space: Literal["world"] = "world",
    ) -> None:
        """Transform scene objects atomically and record one undo transaction.

        The transformation is a world-space delta applied to every object's
        world transformation before any object is mutated. New local
        transformations are derived from the corresponding pre-operation
        parent world transformations. An ancestor and its descendant cannot be
        transformed in the same request because their shared group semantics
        are ambiguous.

        Parameters
        ----------
        objects
            Stable objects from the current Viewer scene. Duplicate objects
            are transformed once in their first input position.
        transformation
            World-space transformation delta.
        space
            Transformation space. Only `"world"` is currently supported.

        Raises
        ------
        TypeError
            If `transformation` is not a COMPAS transformation or a target is
            not a scene object.
        ValueError
            If the space is unsupported, a target is not in the current scene,
            or the targets contain an ancestor and its descendant.

        """
        if not isinstance(transformation, Transformation):
            raise TypeError("Expected a COMPAS Transformation.")
        if space != "world":
            raise ValueError(f"Unsupported transformation space: {space!r}.")

        targets = self._sceneobjects(objects)
        if not targets or transformation == Transformation():
            return

        target_guids = {sceneobject.guid for sceneobject in targets}
        for sceneobject in targets:
            if any(ancestor.guid in target_guids for ancestor in sceneobject.ancestors):
                raise ValueError("Cannot transform an ancestor and its descendant in one operation.")

        before = tuple((sceneobject, copy_transformation(sceneobject.transformation)) for sceneobject in targets)
        after_states: list[tuple[SceneObject, Transformation | None]] = []
        for sceneobject in targets:
            world = sceneobject.worldtransformation.copy()
            parent = sceneobject.parent
            parent_world = parent.worldtransformation.copy() if parent is not None else Transformation()
            local = parent_world.inverse() * (transformation * world)
            after_states.append((sceneobject, local))
        transaction = TransformTransaction(before=before, after=tuple(after_states))

        self._apply_transform_transaction(transaction, forward=True)
        self._undo_transforms.append(transaction)
        self._redo_transforms.clear()

    def refresh_geometry(self, objects: Iterable[SceneObject] | None = None) -> None:
        """Rebuild render geometry after topology or geometric data changes.

        Parameters
        ----------
        objects
            Changed objects from the current scene. `None` means all objects.
            Geometry buffers are combined, so the first version rebuilds the
            complete buffer set after validating this scope.

        """
        self._sceneobjects(objects)
        if not self.running:
            return
        self.renderer.rebuild_buffers()
        self._sync_view()

    def refresh_appearance(self, objects: Iterable[SceneObject] | None = None) -> None:
        """Refresh same-topology colors and display settings.

        Parameters
        ----------
        objects
            Changed objects from the current scene. `None` means all objects.

        """
        targets = self._sceneobjects(objects)
        if not self.running:
            return
        manager = self.renderer.buffer_manager
        for sceneobject in targets:
            render_object = self.scene.render_objects.get(sceneobject.guid)
            if render_object is None:
                continue
            manager.update_object_data(render_object)
            manager.update_object_settings(render_object)
        self._sync_view()

    def refresh_transform(self, objects: Iterable[SceneObject] | None = None) -> None:
        """Refresh transforms after direct untracked scene-object mutation.

        Calling this operation invalidates transform undo and redo history.
        Use [`transform_objects`][compas_viewer.Viewer.transform_objects] when
        the change should be reversible.

        Parameters
        ----------
        objects
            Changed objects from the current scene. `None` means all objects.

        """
        targets = self._sceneobjects(objects)
        self._refresh_transform(targets, invalidate_history=True)

    def refresh_hierarchy(self) -> None:
        """Rebuild runtime hierarchy, picking, parent links, and buffers.

        Surviving selected objects retain their order. Hierarchy refreshes
        invalidate transformation history because stored local transforms may
        no longer have the same parent meaning.

        """
        self._clear_transform_history()
        surviving = tuple(self.scene.object(guid) for guid in self.state.selection.guids if guid in self.scene.object_store)
        if self.running:
            self.renderer.rebuild_buffers()
        else:
            self.scene.prepare()
        if not self.state.selection.replace(surviving):
            self._sync_view()

    def undo(self) -> bool:
        """Undo the most recent reversible Viewer transformation.

        Returns
        -------
        bool
            `True` if a transaction was undone, otherwise `False`.

        """
        if not self._undo_transforms:
            return False
        transaction = self._undo_transforms[-1]
        self._apply_transform_transaction(transaction, forward=False)
        self._undo_transforms.pop()
        self._redo_transforms.append(transaction)
        return True

    def redo(self) -> bool:
        """Redo the most recently undone Viewer transformation.

        Returns
        -------
        bool
            `True` if a transaction was redone, otherwise `False`.

        """
        if not self._redo_transforms:
            return False
        transaction = self._redo_transforms[-1]
        self._apply_transform_transaction(transaction, forward=True)
        self._redo_transforms.pop()
        self._undo_transforms.append(transaction)
        return True

    def _sceneobjects(self, objects: Iterable[SceneObject] | None) -> tuple[SceneObject, ...]:
        """Validate and de-duplicate current non-root scene objects."""
        candidates = self.scene.objects if objects is None else objects
        result: list[SceneObject] = []
        seen: set[UUID] = set()
        for sceneobject in candidates:
            if not isinstance(sceneobject, SceneObject):
                raise TypeError("Expected stable COMPAS SceneObject values.")
            if sceneobject.is_root:
                raise ValueError("The Viewer scene root cannot be refreshed or transformed.")
            try:
                current = self.scene.object(sceneobject.guid)
            except KeyError:
                raise ValueError("The scene object does not belong to the current Viewer scene.") from None
            if current is not sceneobject:
                raise ValueError("The scene object does not belong to the current Viewer scene.")
            if sceneobject.guid not in seen:
                result.append(sceneobject)
                seen.add(sceneobject.guid)
        return tuple(result)

    def _apply_transform_transaction(self, transaction: TransformTransaction, *, forward: bool) -> None:
        """Apply one transform snapshot atomically and refresh it once."""
        states = transaction.after if forward else transaction.before
        originals = tuple((sceneobject, copy_transformation(sceneobject.transformation)) for sceneobject, _ in states)
        try:
            for sceneobject, transformation in states:
                sceneobject.transformation = copy_transformation(transformation)
            self._refresh_transform(tuple(sceneobject for sceneobject, _ in states), invalidate_history=False)
        except Exception:
            for sceneobject, transformation in originals:
                sceneobject.transformation = transformation
            try:
                self._refresh_transform(tuple(sceneobject for sceneobject, _ in originals), invalidate_history=False)
            except Exception:
                pass
            raise

    def _refresh_transform(self, targets: tuple[SceneObject, ...], *, invalidate_history: bool) -> None:
        """Refresh local transform buffers and descendant world bounds."""
        if invalidate_history:
            self._clear_transform_history()

        expanded: list[SceneObject] = []
        expanded_guids: set[UUID] = set()
        for sceneobject in targets:
            for affected in (sceneobject, *sceneobject.descendants):
                if affected.guid not in expanded_guids:
                    expanded.append(affected)
                    expanded_guids.add(affected.guid)

        if self.running:
            manager = self.renderer.buffer_manager
            for sceneobject in targets:
                render_object = self.scene.render_objects.get(sceneobject.guid)
                if render_object is not None:
                    manager.update_object_transform(render_object)

        for sceneobject in expanded:
            render_object = self.scene.render_objects.get(sceneobject.guid)
            if render_object is not None and render_object._inited:
                self._update_world_bounds(render_object)

        self._sync_view()

    @staticmethod
    def _update_world_bounds(render_object: Any) -> None:
        """Recompute one render helper's world-space bounds."""
        refresh_annotation_bounds = getattr(render_object, "refresh_annotation_bounds", None)
        if refresh_annotation_bounds is not None:
            refresh_annotation_bounds()
            return
        render_object._update_bounding_box()

    def _sync_view(self) -> None:
        """Synchronize the sidebar and viewport once when the Viewer runs."""
        if not self.running:
            return
        self.ui.sidebar.update()
        self.renderer.update()

    def _clear_transform_history(self) -> None:
        """Discard reversible transform transactions."""
        getattr(self, "_undo_transforms", []).clear()
        getattr(self, "_redo_transforms", []).clear()

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
        elif path == "selection" and hasattr(self, "ui"):
            self.ui.sidebar.update()
            self.renderer.update()
        elif path.startswith("measurement.") and hasattr(self, "ui"):
            self.ui.viewport.update_overlays()

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
    converted = Image.open(BytesIO(data.data()))
    converted.load()
    return converted
