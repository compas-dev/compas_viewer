from types import SimpleNamespace

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
    existing = SimpleNamespace(is_selected=True)
    created = SimpleNamespace(is_selected=True)

    class Scene:
        objects = [existing]

        def add(self, geometry, **kwargs):
            self.geometry = geometry
            self.kwargs = kwargs
            return created

    scene = Scene()
    viewer = SimpleNamespace(scene=scene, running=False)

    result = add_geometry(viewer, "sphere")

    assert result is created
    assert not existing.is_selected
    assert scene.kwargs == {"name": "Sphere", "is_selected": True}


def test_add_menu_contains_geometry_categories():
    add_menu = default_menu_items()[0]

    assert add_menu["title"] == "Add"
    assert [item["title"] for item in add_menu["items"]] == ["Primitives", "Curves", "Surfaces", "Shapes"]
