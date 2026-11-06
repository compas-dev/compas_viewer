from compas.geometry import Brep
from compas.geometry import Box
from compas.geometry import Point
from compas.geometry import Polygon
from compas.geometry import PolygonalSurface
from compas.geometry import Polyhedron
from compas.geometry import Tessellation
from compas_viewer.scene import BRepObject
from compas_viewer.scene import PolygonObject
from compas_viewer.scene import PolygonalSurfaceObject
from compas_viewer.scene import PolyhedronObject


def test_polygon_scene_object_uses_nonmutating_triangulation():
    polygon = Polygon([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
    data = polygon.__data__
    sceneobject = object.__new__(PolygonObject)
    PolygonObject.__init__(sceneobject, item=polygon)

    first = sceneobject.tessellation
    second = sceneobject.tessellation

    assert first.number_of_triangles == 2
    assert first is not second
    assert polygon.__data__ == data


def test_polygonal_surface_scene_object_uses_nonmutating_triangulation():
    surface = PolygonalSurface(
        [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
        [[0, 1, 2, 3]],
    )
    data = surface.__data__
    sceneobject = object.__new__(PolygonalSurfaceObject)
    PolygonalSurfaceObject.__init__(sceneobject, item=surface)

    first = sceneobject.tessellation
    second = sceneobject.tessellation

    assert first.number_of_triangles == 2
    assert first is not second
    assert surface.__data__ == data


def test_polyhedron_scene_object_uses_nonmutating_triangulation():
    polygonal_surface = Box(1.0).to_polygonal_surface()
    polyhedron = Polyhedron(polygonal_surface.vertices, polygonal_surface.faces)
    data = polyhedron.__data__
    sceneobject = object.__new__(PolyhedronObject)
    PolyhedronObject.__init__(sceneobject, item=polyhedron)

    first = sceneobject.tessellation
    second = sceneobject.tessellation

    assert first.number_of_triangles == 12
    assert first is not second
    assert polyhedron.__data__ == data


class StubBrep(Brep):
    def __init__(self, tessellation: Tessellation) -> None:
        super().__init__()
        self.tessellation = tessellation
        self.tessellation_calls = 0

    @property
    def points(self) -> list[Point]:
        return [Point(0, 0, 0), Point(1, 0, 0)]

    def to_tessellation(self, *, linear_deflection=None, angular_deflection=None) -> Tessellation:
        self.tessellation_calls += 1
        return self.tessellation


def test_brep_scene_object_refreshes_one_current_tessellation():
    initial = Tessellation(
        vertices=[[0, 0, 0], [1, 0, 0], [0, 1, 0]],
        triangles=[[0, 1, 2]],
        polylines=[[[0, 0, 0], [1, 0, 0], [1, 1, 0]]],
    )
    before_first_draw = Tessellation(
        vertices=[[0, 0, 0], [2, 0, 0], [0, 2, 0]],
        triangles=[[0, 2, 1]],
        polylines=[[[0, 0, 0], [2, 0, 0], [2, 2, 0]]],
    )
    after_mutation = Tessellation(
        vertices=[[0, 0, 0], [3, 0, 0], [0, 3, 0]],
        triangles=[[0, 1, 2]],
        polylines=[[[0, 0, 0], [3, 0, 0], [3, 3, 0]]],
    )
    brep = StubBrep(initial)
    sceneobject = object.__new__(BRepObject)

    BRepObject.__init__(sceneobject, item=brep)
    brep.tessellation = before_first_draw
    sceneobject.refresh_data()

    assert brep.tessellation_calls == 1
    assert sceneobject.viewmesh == (before_first_draw.vertices, before_first_draw.triangles)
    assert sceneobject.lines == [
        ([0, 0, 0], [2, 0, 0]),
        ([2, 0, 0], [2, 2, 0]),
    ]

    brep.tessellation = after_mutation
    sceneobject.refresh_data()

    assert brep.tessellation_calls == 2
    assert sceneobject.viewmesh == (after_mutation.vertices, after_mutation.triangles)
    assert sceneobject.lines == [
        ([0, 0, 0], [3, 0, 0]),
        ([3, 0, 0], [3, 3, 0]),
    ]
