from types import SimpleNamespace
from uuid import uuid4

import numpy as np
from PySide6.QtCore import QEvent
from PySide6.QtCore import QPoint

from compas.colors import Color
from compas.geometry import Point

from compas_viewer.commands import isolate_selected
from compas_viewer.commands import invert_selection
from compas_viewer.commands import deselect_object
from compas_viewer.commands import deselect_all_cmd
from compas_viewer.commands import select_multiple
from compas_viewer.commands import select_object
from compas_viewer.commands import select_window
from compas_viewer.commands import select_by_color
from compas_viewer.commands import select_by_name
from compas_viewer.commands import select_by_type
from compas_viewer.commands import select_multiple_cmd
from compas_viewer.commands import show_all
from compas_viewer.commands import toggle_grid
from compas_viewer.commands import zoom_extents
from compas_viewer.commands import zoom_selected
from compas_viewer.commands import _object_from_instance_colors
from compas_viewer.commands import _window_instance_colors
from compas_viewer.config import Config
from compas_viewer.state import ViewerState


class MeshItem:
    pass


def test_deselect_all_uses_escape_key():
    assert deselect_all_cmd.keybinding == "Escape"


class PointItem:
    pass


class SceneObject:
    def __init__(self, name, item, color, bounding_box, *, parent=None):
        self.guid = uuid4()
        self.name = name
        self.item = item
        self.facecolor = color
        self.bounding_box = bounding_box
        self.show = True
        self.parent = parent

    def _update_bounding_box(self):
        pass


class Camera:
    def __init__(self):
        self._target = Point(0, 0, 0)
        self._position = Point(0, -10, 0)
        self.scale = 1.0

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        self._target = Point(value[0], value[1], value[2])

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = Point(value[0], value[1], value[2])


class Viewer:
    def __init__(self, objects):
        class Scene:
            def __init__(self, objects):
                self.objects = objects
                self.instance_colors = {}

            def object(self, guid):
                return next(obj for obj in self.objects if obj.guid == guid)

            def render_object(self, sceneobject):
                return sceneobject

        self.scene = Scene(objects)
        self.renderer = SimpleNamespace(camera=Camera(), update=lambda: None)
        self.ui = SimpleNamespace(sidebar=SimpleNamespace(update=lambda: None))
        self.config = Config()
        self.state = ViewerState(self.config, self.scene.object)
        self.mouse = SimpleNamespace(last_pos=SimpleNamespace(x=lambda: 0, y=lambda: 0))


def make_viewer():
    root = SimpleNamespace(is_root=True, parent=None)
    group = SceneObject("Group", object(), Color.grey(), None, parent=root)
    red_mesh = SceneObject("Red Mesh", MeshItem(), Color.red(), [[0, 0, 0], [2, 2, 2]], parent=group)
    blue_point = SceneObject("Blue Point", PointItem(), Color.blue(), [[10, 0, 0], [10, 0, 0]], parent=root)
    viewer = Viewer([group, red_mesh, blue_point])
    viewer.state.selection.add(red_mesh)
    return viewer, group, red_mesh, blue_point


def test_selection_filters_replace_selection():
    viewer, _, red_mesh, blue_point = make_viewer()

    select_by_type(viewer, "PointItem")
    assert blue_point in viewer.state.selection
    assert red_mesh not in viewer.state.selection

    select_by_name(viewer, "red")
    assert red_mesh in viewer.state.selection
    assert blue_point not in viewer.state.selection

    select_by_color(viewer, "#0000ff")
    assert blue_point in viewer.state.selection
    assert red_mesh not in viewer.state.selection


def test_invert_selection_only_toggles_visible_objects():
    viewer, group, red_mesh, blue_point = make_viewer()
    blue_point.show = False
    viewer.state.selection.add(blue_point)

    invert_selection(viewer)

    assert group in viewer.state.selection
    assert red_mesh not in viewer.state.selection
    assert blue_point in viewer.state.selection


def test_instance_color_resolution_ignores_background_pixels():
    selected = object()
    viewer = SimpleNamespace(scene=SimpleNamespace(instance_colors={(10, 20, 30): selected}))
    pixels = np.array([[0, 0, 0], [10, 20, 30], [0, 0, 0], [10, 20, 30]], dtype=np.uint8)

    assert _object_from_instance_colors(viewer, pixels) is selected


def test_window_instance_colors_distinguish_contained_and_crossing_selection():
    contained = (10, 20, 30)
    crossing = (40, 50, 60)
    viewer = SimpleNamespace(scene=SimpleNamespace(instance_colors={contained: object(), crossing: object()}))
    inside = np.array([contained, contained, crossing, (0, 0, 0)], dtype=np.uint8)
    complete_map = np.array([contained, contained, crossing, crossing, crossing, (0, 0, 0)], dtype=np.uint8)

    assert _window_instance_colors(viewer, inside) == {contained, crossing}
    assert _window_instance_colors(viewer, inside, complete_map) == {contained}


def test_isolate_selected_keeps_ancestors_visible():
    viewer, group, red_mesh, blue_point = make_viewer()

    isolate_selected(viewer)

    assert group.show
    assert red_mesh.show
    assert not blue_point.show


def test_show_all_restores_visibility_after_isolation():
    viewer, group, red_mesh, blue_point = make_viewer()

    isolate_selected(viewer)
    show_all(viewer)

    assert group.show
    assert red_mesh.show
    assert blue_point.show


def test_zoom_commands_frame_selected_and_visible_extents():
    viewer, _, red_mesh, blue_point = make_viewer()

    zoom_selected(viewer)
    assert viewer.renderer.camera.target == Point(1, 1, 1)

    zoom_extents(viewer)
    assert viewer.renderer.camera.target == Point(5, 1, 1)

    blue_point.show = False
    zoom_extents(viewer)
    assert viewer.renderer.camera.target == Point(1, 1, 1)


def test_zoom_selected_preserves_camera_scale_for_a_point():
    viewer, _, red_mesh, blue_point = make_viewer()
    viewer.state.selection.replace((blue_point,))
    viewer.renderer.camera.scale = 2.0

    zoom_selected(viewer)

    assert viewer.renderer.camera.target == Point(10, 0, 0)
    assert viewer.renderer.camera.scale == 2.0


def test_grid_toggle_and_multiple_selection_binding():
    viewer, *_ = make_viewer()

    toggle_grid(viewer)

    assert not viewer.config.renderer.show_grid
    assert select_multiple_cmd.mousebinding == "LEFT + CTRL"


def test_pointer_commands_replace_add_and_remove_selection():
    viewer, group, red_mesh, blue_point = make_viewer()
    viewer.scene.instance_colors = {
        (10, 20, 30): group,
        (40, 50, 60): blue_point,
    }
    pixels = iter(
        [
            np.array([[10, 20, 30]], dtype=np.uint8),
            np.array([[40, 50, 60]], dtype=np.uint8),
            np.array([[10, 20, 30]], dtype=np.uint8),
        ]
    )
    viewer.renderer.read_instance_color = lambda _box: next(pixels)
    event = SimpleNamespace(type=lambda: QEvent.Type.MouseButtonPress)

    select_object(viewer, event)
    assert viewer.state.selection.objects == (group,)

    select_multiple(viewer, event)
    assert viewer.state.selection.objects == (group, blue_point)

    deselect_object(viewer, event)
    assert viewer.state.selection.objects == (blue_point,)


def test_window_command_preserves_directional_selection_semantics():
    viewer, group, red_mesh, blue_point = make_viewer()
    group_color = (10, 20, 30)
    red_color = (40, 50, 60)
    blue_color = (70, 80, 90)
    viewer.scene.instance_colors = {
        group_color: group,
        red_color: red_mesh,
        blue_color: blue_point,
    }
    viewer.renderer.width = lambda: 100
    viewer.renderer.height = lambda: 100
    viewer.renderer.read_instance_colors = lambda _boxes: (
        np.array([red_color, red_color, blue_color], dtype=np.uint8),
        np.array([red_color, red_color, blue_color, blue_color], dtype=np.uint8),
    )
    viewer.renderer.read_instance_color = lambda _box: np.array([red_color, blue_color], dtype=np.uint8)
    viewer.mouse.window_start_point = None
    viewer.mouse.window_end_point = None
    viewer.mouse.is_tracing_a_window = False

    select_window(viewer, SimpleNamespace(type=lambda: QEvent.Type.MouseButtonPress, pos=lambda: QPoint(0, 0)))
    select_window(viewer, SimpleNamespace(type=lambda: QEvent.Type.MouseButtonRelease, pos=lambda: QPoint(10, 10)))

    assert viewer.state.selection.objects == (red_mesh,)

    select_window(viewer, SimpleNamespace(type=lambda: QEvent.Type.MouseButtonPress, pos=lambda: QPoint(10, 10)))
    select_window(viewer, SimpleNamespace(type=lambda: QEvent.Type.MouseButtonRelease, pos=lambda: QPoint(0, 0)))

    assert viewer.state.selection.objects == (red_mesh, blue_point)
