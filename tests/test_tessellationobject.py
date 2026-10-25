from compas.colors import Color
from compas.geometry import Tessellation

from compas_viewer.scene import TessellationObject


class ExampleTessellationObject(TessellationObject):
    @property
    def tessellation(self):
        return self._tessellation


def make_sceneobject(tessellation):
    sceneobject = object.__new__(ExampleTessellationObject)
    sceneobject._tessellation = tessellation
    sceneobject.surfacecolor = Color.red()
    return sceneobject


def test_tessellation_object_preserves_indexed_vertex_buffer():
    tessellation = Tessellation(
        vertices=((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, 1.0, 0.0)),
        triangles=((0, 1, 2), (1, 3, 2)),
    )
    sceneobject = make_sceneobject(tessellation)

    positions, colors, elements = sceneobject._read_frontfaces_data()

    assert positions is tessellation.vertices
    assert elements == [list(triangle) for triangle in tessellation.triangles]
    assert len(colors) == tessellation.number_of_vertices


def test_tessellation_object_reverses_backfaces_without_mutating_tessellation():
    triangles = ((0, 1, 2),)
    tessellation = Tessellation(
        vertices=((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
        triangles=triangles,
    )
    sceneobject = make_sceneobject(tessellation)

    _, _, elements = sceneobject._read_backfaces_data()

    assert elements == [[2, 1, 0]]
    assert tessellation.triangles == triangles
