from compas_viewer.configurations import ControllerConfig
from compas_viewer.configurations import ViewerConfig


def test_viewer_config() -> None:
    config = ViewerConfig.from_default()
    assert type(config) == ViewerConfig
    assert type(config.about) == str
    assert type(config.title) == str
    assert type(config.width) == int
    assert type(config.height) == int
    assert type(config.full_screen) == bool
    config.validate_data(config.data)


def test_controller_config() -> None:
    config = ControllerConfig.from_default()
    assert type(config) == ControllerConfig
    assert type(config.pan) == dict
    assert type(config.zoom) == dict
    assert type(config.rotate) == dict
    assert type(config.box_selection) == dict
    assert type(config.selection) == str
    assert type(config.multi_selection) == str
    assert type(config.deletion) == str
    config.validate_data(config.data)
