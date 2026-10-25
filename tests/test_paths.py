from pathlib import Path

from compas_viewer import DATA
from compas_viewer import DOCS
from compas_viewer import HERE
from compas_viewer import HOME
from compas_viewer import TEMP
from compas_viewer.scene import Tag


def test_package_locations_are_paths():
    assert isinstance(HERE, Path)
    assert isinstance(HOME, Path)
    assert isinstance(DATA, Path)
    assert isinstance(DOCS, Path)
    assert isinstance(TEMP, Path)
    assert HERE.name == "compas_viewer"
    assert DOCS == HOME / "docs"


def test_default_annotation_font_is_a_path():
    annotation = Tag("Path", (0, 0, 0))

    assert isinstance(annotation.font, Path)
    assert annotation.font.is_file()
    assert annotation.__data__["font"] == str(annotation.font)
