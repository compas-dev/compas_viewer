from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock

import numpy as np
import pytest

from compas.datastructures import Mesh
from compas.geometry import Point
from compas.geometry import Sphere
from compas.scene import SceneObject
from compas_viewer.renderer import renderer as renderer_module
from compas_viewer.renderer.renderer import Renderer
from compas_viewer.scene.buffermanager import BufferManager
from compas_viewer.snapping import ProjectedPoint
from compas_viewer.snapping import SnapKind
from compas_viewer.snapping import SnapQuery
from compas_viewer.snapping import SnapResult


class Camera:
    def __init__(self, projection=None, viewworld=None):
        self._projection = np.identity(4) if projection is None else projection
        self._viewworld = np.identity(4) if viewworld is None else viewworld

    def projection(self, width, height):
        return self._projection

    def viewworld(self):
        return self._viewworld


def projection_renderer(width=200, height=100, camera=None) -> Any:
    renderer: Any = SimpleNamespace(
        width=lambda: width,
        height=lambda: height,
        camera=camera or Camera(),
        SNAP_DEPTH_EPSILON=Renderer.SNAP_DEPTH_EPSILON,
    )
    renderer._view_projection = lambda: Renderer._view_projection(renderer)
    renderer._project_point = Renderer._project_point
    renderer._unproject_point_with_matrix = lambda x, y, depth, matrix: Renderer._unproject_point_with_matrix(renderer, x, y, depth, matrix)
    return renderer


def install_gl_state(monkeypatch, *, enabled):
    gl = renderer_module.GL
    capabilities = {
        gl.GL_SCISSOR_TEST,
        gl.GL_DEPTH_TEST,
        gl.GL_BLEND,
        gl.GL_POLYGON_OFFSET_FILL,
        gl.GL_CULL_FACE,
    }
    state = {
        "enabled": {capability: enabled for capability in capabilities},
        "scissor_box": (3, 4, 5, 6),
        "pack_alignment": 8,
        "pixel_pack_buffer": 71,
        "depth_func": gl.GL_GREATER,
        "depth_write_mask": False,
        "clear_color": (0.1, 0.2, 0.3, 0.4),
        "polygon_offset": (3.0, 4.0),
        "line_width": 2.0,
        "point_size": 3.0,
        "program": 11,
        "vertex_array": 12,
        "array_buffer": 13,
        "element_array_buffer": 14,
        "texture_buffer": 15,
        "active_texture": int(gl.GL_TEXTURE0) + 3,
        "texture_buffer_bindings": {int(gl.GL_TEXTURE0): 21, int(gl.GL_TEXTURE0) + 1: 22},
        "texture_2d": 23,
        "renderbuffer": 24,
        "viewport": (0, 0, 100, 50),
        "clear_colors": [],
    }

    def get_integer(name):
        values = {
            gl.GL_SCISSOR_BOX: state["scissor_box"],
            gl.GL_PACK_ALIGNMENT: state["pack_alignment"],
            gl.GL_PIXEL_PACK_BUFFER_BINDING: state["pixel_pack_buffer"],
            gl.GL_DEPTH_FUNC: state["depth_func"],
            gl.GL_CURRENT_PROGRAM: state["program"],
            gl.GL_VERTEX_ARRAY_BINDING: state["vertex_array"],
            gl.GL_ARRAY_BUFFER_BINDING: state["array_buffer"],
            gl.GL_ELEMENT_ARRAY_BUFFER_BINDING: state["element_array_buffer"],
            gl.GL_TEXTURE_BUFFER_BINDING: state["texture_buffer"],
            gl.GL_ACTIVE_TEXTURE: state["active_texture"],
            gl.GL_TEXTURE_BINDING_BUFFER: state["texture_buffer_bindings"].get(state["active_texture"], 0),
            gl.GL_TEXTURE_BINDING_2D: state["texture_2d"],
            gl.GL_RENDERBUFFER_BINDING: state["renderbuffer"],
        }
        return values[name]

    def get_float(name):
        values = {
            gl.GL_COLOR_CLEAR_VALUE: state["clear_color"],
            gl.GL_POLYGON_OFFSET_FACTOR: state["polygon_offset"][0],
            gl.GL_POLYGON_OFFSET_UNITS: state["polygon_offset"][1],
            gl.GL_LINE_WIDTH: state["line_width"],
            gl.GL_POINT_SIZE: state["point_size"],
        }
        return values[name]

    monkeypatch.setattr(gl, "glIsEnabled", lambda capability: state["enabled"][capability])
    monkeypatch.setattr(gl, "glEnable", lambda capability: state["enabled"].__setitem__(capability, True))
    monkeypatch.setattr(gl, "glDisable", lambda capability: state["enabled"].__setitem__(capability, False))
    monkeypatch.setattr(gl, "glGetIntegerv", get_integer)
    monkeypatch.setattr(gl, "glGetBooleanv", lambda name: state["depth_write_mask"])
    monkeypatch.setattr(gl, "glGetFloatv", get_float)
    monkeypatch.setattr(gl, "glScissor", lambda *value: state.__setitem__("scissor_box", value))
    monkeypatch.setattr(gl, "glPixelStorei", lambda _name, value: state.__setitem__("pack_alignment", value))
    monkeypatch.setattr(gl, "glDepthFunc", lambda value: state.__setitem__("depth_func", value))
    monkeypatch.setattr(gl, "glDepthMask", lambda value: state.__setitem__("depth_write_mask", bool(value)))

    def clear_color(*value):
        state["clear_color"] = value
        state["clear_colors"].append(value)

    monkeypatch.setattr(gl, "glClearColor", clear_color)
    monkeypatch.setattr(gl, "glPolygonOffset", lambda factor, units: state.__setitem__("polygon_offset", (factor, units)))
    monkeypatch.setattr(gl, "glLineWidth", lambda value: state.__setitem__("line_width", value))
    monkeypatch.setattr(gl, "glPointSize", lambda value: state.__setitem__("point_size", value))
    monkeypatch.setattr(gl, "glUseProgram", lambda value: state.__setitem__("program", value))
    monkeypatch.setattr(gl, "glBindVertexArray", lambda value: state.__setitem__("vertex_array", value))

    def bind_buffer(target, value):
        key = {
            gl.GL_ARRAY_BUFFER: "array_buffer",
            gl.GL_ELEMENT_ARRAY_BUFFER: "element_array_buffer",
            gl.GL_TEXTURE_BUFFER: "texture_buffer",
            gl.GL_PIXEL_PACK_BUFFER: "pixel_pack_buffer",
        }[target]
        state[key] = value

    monkeypatch.setattr(gl, "glBindBuffer", bind_buffer)
    monkeypatch.setattr(gl, "glActiveTexture", lambda value: state.__setitem__("active_texture", int(value)))

    def bind_texture(target, value):
        if target == gl.GL_TEXTURE_BUFFER:
            state["texture_buffer_bindings"][state["active_texture"]] = value
        else:
            state["texture_2d"] = value

    monkeypatch.setattr(gl, "glBindTexture", bind_texture)
    monkeypatch.setattr(gl, "glBindRenderbuffer", lambda _target, value: state.__setitem__("renderbuffer", value))
    monkeypatch.setattr(gl, "glViewport", lambda *value: state.__setitem__("viewport", value))
    monkeypatch.setattr(gl, "glClear", Mock())
    monkeypatch.setattr(gl, "glFlush", Mock())
    monkeypatch.setattr(gl, "glFinish", Mock())
    return state


def state_snapshot(state):
    return {key: value.copy() if isinstance(value, dict) else value for key, value in state.items() if key != "clear_colors"}


def test_project_point_uses_logical_top_left_pixels_and_clip_w():
    renderer = projection_renderer()

    projected = Renderer.project_point(renderer, Point(0, 0, 0))

    assert projected == ProjectedPoint(100, 50, 0.5, 1.0)

    perspective = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, -1.0, 0.0],
        ]
    )
    renderer.camera = Camera(projection=perspective)

    projected = Renderer.project_point(renderer, Point(1, 0, -2))

    assert projected == ProjectedPoint(150, 50, 0.5, 2.0)
    assert Renderer.project_point(renderer, Point(1, 0, 2)) is None


def test_projection_and_unprojection_roundtrip_in_orthographic_view():
    renderer = projection_renderer(width=100, height=100)
    point = Point(-0.5, 0.5, 0.2)

    projected = Renderer.project_point(renderer, point)
    assert projected is not None
    restored = Renderer._unproject_point(renderer, projected.x, projected.y, projected.depth)

    assert restored == point
    top_left = Renderer._unproject_point(renderer, 0, 0, 0.5)
    assert top_left == Point(-1, 1, 0)


def test_snap_region_clips_viewport_edges_without_device_pixel_scaling():
    renderer = projection_renderer(width=100, height=50)
    renderer.devicePixelRatio = Mock(side_effect=AssertionError("logical instance pixels should not be scaled"))

    top_left = Renderer._snap_region(renderer, (-2, -3), 5)
    bottom_right = Renderer._snap_region(renderer, (99, 49), 5)

    assert top_left == (0, 0, 47, 4, 3)
    assert bottom_right == (94, 44, 0, 6, 6)
    renderer.devicePixelRatio.assert_not_called()


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("fails", [False, True])
def test_acquisition_uses_one_scissored_pass_and_restores_state(monkeypatch, enabled, fails):
    renderer = projection_renderer(width=100, height=50)
    renderer._capture_instance_gl_state = Renderer._capture_instance_gl_state
    renderer._restore_instance_gl_state = Renderer._restore_instance_gl_state
    renderer._render_instance_map = Mock(side_effect=RuntimeError("render failed") if fails else None)
    renderer._read_pixels = Mock(return_value=np.array([[[1, 2, 3]], [[4, 5, 6]]], dtype=np.uint8))
    renderer._read_depths = Mock(return_value=np.array([[0.25], [0.75]], dtype=np.float32))
    state = install_gl_state(monkeypatch, enabled=enabled)
    initial = state_snapshot(state)

    class Offscreen:
        def __init__(self, width, height):
            assert (width, height) == (100, 50)

        def __enter__(self):
            state["texture_2d"] = 123
            state["renderbuffer"] = 124
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return None

    monkeypatch.setattr(renderer_module, "OffscreenBufferContext", Offscreen)

    if fails:
        with pytest.raises(RuntimeError, match="render failed"):
            Renderer._acquire_snap_buffers(renderer, (10, 20, 28, 1, 2))
        assert state_snapshot(state) == initial
        return

    colors, depths = Renderer._acquire_snap_buffers(renderer, (10, 20, 28, 1, 2))

    renderer._render_instance_map.assert_called_once_with()
    renderer._read_pixels.assert_called_once_with(10, 28, 1, 2)
    renderer._read_depths.assert_called_once_with(10, 28, 1, 2)
    assert colors.tolist() == [[[4, 5, 6]], [[1, 2, 3]]]
    assert np.allclose(depths, [[0.75], [0.25]])
    assert state_snapshot(state) == initial


def test_instance_render_uses_sentinel_background_and_coplanar_component_priority(monkeypatch):
    renderer = projection_renderer(width=100, height=50)
    renderer.INSTANCE_BACKGROUND = Renderer.INSTANCE_BACKGROUND
    renderer._capture_instance_gl_state = Renderer._capture_instance_gl_state
    renderer._restore_instance_gl_state = Renderer._restore_instance_gl_state
    renderer.paintGL = Mock()
    renderer.clear = Mock()
    collision_color = (0.2, 0.4, 0.6, 1.0)
    renderer.viewer = SimpleNamespace(config=SimpleNamespace(renderer=SimpleNamespace(backgroundcolor=SimpleNamespace(rgba=collision_color))))
    state = install_gl_state(monkeypatch, enabled=False)
    initial = state_snapshot(state)
    depth_during_paint = []
    renderer.paint = Mock(side_effect=lambda **_kwargs: depth_during_paint.append(state["depth_func"]))

    Renderer._render_instance_map(renderer)

    renderer.paint.assert_called_once_with(is_instance=True)
    renderer.paintGL.assert_not_called()
    renderer.clear.assert_not_called()
    assert Renderer.INSTANCE_BACKGROUND in state["clear_colors"]
    assert collision_color not in state["clear_colors"]
    assert depth_during_paint == [renderer_module.GL.GL_LEQUAL]
    assert state_snapshot(state) == initial

    manager = BufferManager()
    for name in manager.buffer_ids:
        manager.buffer_ids[name] = {"positions": 1}
    order = []
    manager._draw_faces = Mock(side_effect=lambda *_args: order.append("faces"))
    manager._draw_points = Mock(side_effect=lambda *_args: order.append("points"))
    manager._draw_lines = Mock(side_effect=lambda *_args: order.append("lines"))
    manager.draw(Mock(), Mock(), "shaded", is_instance=True)

    assert order == ["faces", "points", "lines"]


@pytest.mark.parametrize("enabled", [False, True])
def test_instance_render_restores_draw_state_after_exception(monkeypatch, enabled):
    renderer = projection_renderer(width=100, height=50)
    renderer.INSTANCE_BACKGROUND = Renderer.INSTANCE_BACKGROUND
    renderer._capture_instance_gl_state = Renderer._capture_instance_gl_state
    renderer._restore_instance_gl_state = Renderer._restore_instance_gl_state
    state = install_gl_state(monkeypatch, enabled=enabled)
    initial = state_snapshot(state)
    gl = renderer_module.GL

    def fail_during_paint(**_kwargs):
        gl.glDisable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_POLYGON_OFFSET_FILL)
        gl.glLineWidth(9.0)
        gl.glPointSize(10.0)
        gl.glUseProgram(91)
        gl.glBindVertexArray(92)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 93)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 94)
        gl.glBindBuffer(gl.GL_TEXTURE_BUFFER, 95)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_BUFFER, 96)
        raise RuntimeError("paint failed")

    renderer.paint = fail_during_paint

    with pytest.raises(RuntimeError, match="paint failed"):
        Renderer._render_instance_map(renderer)

    assert state_snapshot(state) == initial


@pytest.mark.parametrize("reader", ["color", "depth"])
@pytest.mark.parametrize("fails", [False, True])
def test_pixel_read_restores_pack_state_on_success_and_error(monkeypatch, reader, fails):
    renderer = projection_renderer()
    state = install_gl_state(monkeypatch, enabled=False)
    initial = state_snapshot(state)
    if fails:
        monkeypatch.setattr(renderer_module.GL, "glReadPixels", Mock(side_effect=RuntimeError("read failed")))
        with pytest.raises(RuntimeError, match="read failed"):
            if reader == "color":
                Renderer._read_pixels(renderer, 0, 0, 1, 1)
            else:
                Renderer._read_depths(renderer, 0, 0, 1, 1)
    else:
        payload = bytes([1, 2, 3]) if reader == "color" else np.array([0.25], dtype=np.float32).tobytes()
        monkeypatch.setattr(renderer_module.GL, "glReadPixels", Mock(return_value=payload))
        if reader == "color":
            values = Renderer._read_pixels(renderer, 0, 0, 1, 1)
            assert values.tolist() == [[[1, 2, 3]]]
        else:
            values = Renderer._read_depths(renderer, 0, 0, 1, 1)
            assert np.allclose(values, [[0.25]])

    assert state_snapshot(state) == initial


def test_query_snap_context_uses_one_hovered_object_and_balances_gl_context(monkeypatch):
    first = SceneObject(Point(-0.5, 0, 0))
    second = SceneObject(Point(0.5, 0, 0))
    first_color = (10, 20, 30)
    second_color = (40, 50, 60)
    scene = SimpleNamespace(
        objects=(first, second),
        instance_colors={first_color: first, second_color: second},
    )
    renderer = projection_renderer(width=20, height=20)
    renderer.viewer = SimpleNamespace(scene=scene)
    renderer.makeCurrent = Mock()
    renderer.doneCurrent = Mock()
    renderer._snap_region = Mock(return_value=(9, 9, 9, 3, 3))
    renderer._acquire_snap_buffers = Mock(
        return_value=(
            np.full((3, 3, 3), second_color, dtype=np.uint8),
            np.full((3, 3), 0.5, dtype=np.float32),
        )
    )
    renderer._surface_hits = Mock(return_value=())
    renderer._hovered_snap_object = lambda point, region, colors: Renderer._hovered_snap_object(renderer, point, region, colors)
    renderer.project_point = Mock()
    renderer._is_snap_visible = Mock()
    result = SnapResult(Point(0, 0, 0), second.guid, SnapKind.POINT, 0)
    points = (result,)
    semantic_query = Mock(return_value=SnapQuery(result, points))
    monkeypatch.setattr(renderer_module, "query_snaps", semantic_query)

    query = Renderer.query_snap_context_at(renderer, (10, 10), 1)

    assert query == SnapQuery(result, points)
    renderer.makeCurrent.assert_called_once_with()
    renderer.doneCurrent.assert_called_once_with()
    renderer._acquire_snap_buffers.assert_called_once_with((9, 9, 9, 3, 3))
    assert semantic_query.call_args.args[0] == (second,)
    assert semantic_query.call_args.args[1] == (10, 10)


def test_hovered_snap_object_prefers_the_instance_pixel_nearest_the_pointer():
    first = SceneObject(Point(0, 0, 0))
    second = SceneObject(Point(1, 0, 0))
    first_color = (10, 20, 30)
    second_color = (40, 50, 60)
    renderer = projection_renderer(width=20, height=20)
    renderer.viewer = SimpleNamespace(scene=SimpleNamespace(instance_colors={first_color: first, second_color: second}))
    colors = np.array(
        [
            [second_color, second_color, second_color],
            [second_color, first_color, second_color],
            [second_color, second_color, second_color],
        ],
        dtype=np.uint8,
    )

    hovered = Renderer._hovered_snap_object(renderer, (10.5, 10.5), (9, 9, 8, 3, 3), colors)

    assert hovered is first


def test_query_snap_at_remains_the_winner_only_compatibility_path():
    winner = SnapResult(Point(0, 0, 0), SceneObject(Point(0, 0, 0)).guid, SnapKind.POINT, 0)
    renderer: Any = SimpleNamespace(query_snap_context_at=Mock(return_value=SnapQuery(winner, (winner,))))

    result = Renderer.query_snap_at(renderer, (10, 20), 12)

    assert result is winner
    renderer.query_snap_context_at.assert_called_once_with((10, 20), 12)


def test_depth_visibility_rejects_occluded_and_outside_candidates():
    renderer = projection_renderer(width=20, height=20)
    depths = np.full((3, 3), 0.25, dtype=np.float32)
    region = (9, 9, 8, 3, 3)

    visible = Renderer._is_snap_visible(renderer, ProjectedPoint(10.5, 10.5, 0.25), region, depths)
    occluded = Renderer._is_snap_visible(renderer, ProjectedPoint(10.5, 10.5, 0.5), region, depths)
    outside = Renderer._is_snap_visible(renderer, ProjectedPoint(20, 20, 0.1), region, depths)

    assert visible
    assert not occluded
    assert not outside


def test_surface_hits_unproject_face_buffer_pixels_by_object_kind():
    mesh = SceneObject(Mesh.from_vertices_and_faces([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]]))
    sphere = SceneObject(Sphere(1))
    mesh_color = (10, 20, 30)
    sphere_color = (40, 50, 60)
    face_data = ([0.0, 0.0, 0.0], None, [0])
    scene = SimpleNamespace(
        instance_colors={mesh_color: mesh, sphere_color: sphere},
        render_objects={
            mesh.guid: SimpleNamespace(_frontfaces_data=face_data, _backfaces_data=None),
            sphere.guid: SimpleNamespace(_frontfaces_data=face_data, _backfaces_data=None),
        },
    )
    renderer = projection_renderer(width=20, height=20)
    renderer.viewer = SimpleNamespace(scene=scene)
    renderer._has_face_buffers = lambda guid: Renderer._has_face_buffers(renderer, guid)
    colors = np.array([[mesh_color, sphere_color, (0, 0, 0)]], dtype=np.uint8)
    depths = np.array([[0.2, 0.3, 1.0]], dtype=np.float32)

    hits = Renderer._surface_hits(renderer, (5, 7, 12, 3, 1), colors, depths)

    assert [hit.kind for hit in hits] == [SnapKind.FACE, SnapKind.SURFACE]
    assert [hit.object_guid for hit in hits] == [mesh.guid, sphere.guid]
    assert hits[0].point.x == pytest.approx(-0.45)
    assert hits[0].point.y == pytest.approx(0.25)
    assert hits[0].point.z == pytest.approx(-0.6)
    assert hits[1].point.x == pytest.approx(-0.35)
    assert hits[1].point.y == pytest.approx(0.25)
    assert hits[1].point.z == pytest.approx(-0.4)


def test_query_outside_viewport_does_not_acquire_buffers():
    renderer = projection_renderer(width=20, height=20)
    renderer._snap_region = lambda point, radius: Renderer._snap_region(renderer, point, radius)
    renderer._acquire_snap_buffers = Mock()

    result = Renderer.query_snap_context_at(renderer, (-10, -10), 1)

    assert result == SnapQuery()
    renderer._acquire_snap_buffers.assert_not_called()
