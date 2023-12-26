from compas.colors import Color

from compas_viewer.configurations import CameraConfig
from compas_viewer.configurations import ControllerConfig
from compas_viewer.configurations import RenderConfig
from compas_viewer.configurations import ViewerConfig, SceneConfig


def test_viewer_config() -> None:
    config = ViewerConfig.from_default()
    assert isinstance(config, ViewerConfig)
    assert isinstance(config.about, str)
    assert isinstance(config.title, str)
    assert isinstance(config.width, int)
    assert isinstance(config.height, int)
    assert isinstance(config.fullscreen, bool)
    assert isinstance(config.statusbar, str)
    assert isinstance(config.show_fps, bool)
    config.validate_data(config.data)


def test_controller_config() -> None:
    config = ControllerConfig.from_default()
    assert isinstance(config, ControllerConfig)
    assert isinstance(config.pan, dict)
    assert isinstance(config.zoom, dict)
    assert isinstance(config.rotate, dict)
    assert isinstance(config.drag_selection, dict)
    assert isinstance(config.select, str)
    assert isinstance(config.multiselect, str)
    assert isinstance(config.deselect, str)
    config.validate_data(config.data)


def test_render_config() -> None:
    config = RenderConfig.from_default()
    assert isinstance(config, RenderConfig)
    assert isinstance(config.show_grid, bool)
    assert isinstance(config.gridsize, list)
    assert isinstance(config.viewmode, str)
    assert isinstance(config.rendermode, str)
    assert isinstance(config.backgroundcolor, Color)
    assert isinstance(config.selectioncolor, Color)
    assert isinstance(config.ghostopacity, float)
    assert isinstance(config.camera, CameraConfig)
    assert isinstance(config.camera.fov, float)
    assert isinstance(config.camera.near, float)
    assert isinstance(config.camera.far, float)
    assert isinstance(config.camera.position, list)
    assert isinstance(config.camera.target, list)
    assert isinstance(config.camera.scale, float)
    assert isinstance(config.camera.zoomdelta, float)
    assert isinstance(config.camera.rotationdelta, float)
    assert isinstance(config.camera.pan_delta, float)
    config.validate_data(config.data)


def test_scene_config() -> None:
    config = SceneConfig.from_default()
    assert isinstance(config, SceneConfig)
    assert isinstance(config.pointscolor, Color)
    assert isinstance(config.linescolor, Color)
    assert isinstance(config.facescolor, Color)
    assert isinstance(config.show_points, bool)
    assert isinstance(config.show_lines, bool)
    assert isinstance(config.show_faces, bool)
    assert isinstance(config.lineswidth, float)
    assert isinstance(config.pointssize, float)
    assert isinstance(config.opacity, float)
    assert isinstance(config.hide_coplanaredges, bool)
    assert isinstance(config.use_vertexcolors, bool)
    config.validate_data(config.data)
