import pytest

from compas_viewer.configurations import ViewerConfig


def test_viewer_config() -> None:
    about = 'None"'
    title = "sef"
    width = 100
    height = 1003
    full_screen = True
    config = ViewerConfig(about, title, width, height, full_screen)

    assert type(config.about) == str
    assert type(config.title) == str
    assert type(config.width) == int
    assert type(config.height) == int
    assert type(config.full_screen) == bool

    config.validate_data(config.data)

