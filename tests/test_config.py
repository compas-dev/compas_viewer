from compas_viewer.configurations import ControllerConfig
from compas_viewer.configurations import ViewerConfig


def test_viewer_config() -> None:
    config = ViewerConfig.from_default()
    assert isinstance(config, ViewerConfig)
    assert isinstance(config.about, str)
    assert isinstance(config.title, str)
    assert isinstance(config.width, int)
    assert isinstance(config.height, int)
    assert isinstance(config.fullscreen, bool)
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
