from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from compas.geometry import Box
from compas.geometry import Capsule
from compas.geometry import Circle
from compas.geometry import Cone
from compas.geometry import Cylinder
from compas.geometry import Ellipse
from compas.geometry import Frame
from compas.geometry import Line
from compas.geometry import Plane
from compas.geometry import Point
from compas.geometry import Polygon
from compas.geometry import PolygonalSurface
from compas.geometry import Polyline
from compas.geometry import Sphere
from compas.geometry import Torus
from compas_viewer.commands import add_geometry
from compas_viewer.commands import create_geometry
from compas_viewer.uidefinitions import default_menu_items


@pytest.mark.parametrize(
    ("kind", "geometry_type"),
    [
        ("point", Point),
        ("line", Line),
        ("frame", Frame),
        ("plane", Plane),
        ("polyline", Polyline),
        ("polygon", Polygon),
        ("circle", Circle),
        ("ellipse", Ellipse),
        ("quad_surface", PolygonalSurface),
        ("saddle_surface", PolygonalSurface),
        ("box", Box),
        ("sphere", Sphere),
        ("cylinder", Cylinder),
        ("cone", Cone),
        ("capsule", Capsule),
        ("torus", Torus),
    ],
)
def test_create_geometry_presets(kind, geometry_type):
    assert isinstance(create_geometry(kind), geometry_type)


def test_create_geometry_rejects_unknown_preset():
    with pytest.raises(ValueError, match="Unknown geometry preset"):
        create_geometry("teapot")


def test_add_geometry_selects_only_the_new_object():
    existing = object()
    created = object()

    class Scene:
        objects = [existing]

        def add(self, geometry, **kwargs):
            self.geometry = geometry
            self.kwargs = kwargs
            return created

    scene = Scene()
    selection = Mock()
    viewer = SimpleNamespace(scene=scene, state=SimpleNamespace(selection=selection), running=False)

    result = add_geometry(viewer, "sphere")

    assert result is created
    selection.replace.assert_called_once_with((created,))
    assert scene.kwargs == {"name": "Sphere"}


def test_scene_menu_owns_the_existing_geometry_categories():
    menus = default_menu_items()
    scene_menu = next(item for item in menus if item["title"] == "Scene")
    add_menu = next(item for item in scene_menu["items"] if item.get("title") == "Add")

    assert all(item["title"] != "Add" for item in menus)
    assert [item["title"] for item in add_menu["items"]] == ["Primitives", "Curves", "Surfaces", "Shapes"]
    commands = [entry for category in add_menu["items"] for entry in category["items"]]
    assert all(entry["command"] == "viewer.add_geometry" for entry in commands)
    assert [entry["kwargs"]["kind"] for entry in commands] == [
        "point",
        "line",
        "frame",
        "plane",
        "polyline",
        "polygon",
        "circle",
        "ellipse",
        "quad_surface",
        "saddle_surface",
        "box",
        "sphere",
        "cylinder",
        "cone",
        "capsule",
        "torus",
    ]
