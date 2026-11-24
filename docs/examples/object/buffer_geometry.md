# Buffer Geometry

Use `BufferGeometry` when shared vertices and indexed primitives already exist
as Python or NumPy arrays and should be sent directly to the renderer. This is
the efficient path for a large collection of connected lines or triangles:
edges and triangles keep their indices, and the Viewer does not create one
scene object per primitive or expand the shared vertex table.

The script uses `BufferGeometry.from_vertices_and_edges` and
`BufferGeometry.from_vertices_and_triangles`. Use
`BufferGeometry.from_points` for an indexed point collection, or the general
constructor when one buffer geometry intentionally combines primitive types.
Inputs are copied to contiguous `float32` vertex/color arrays and `int32` index
arrays. Colors are vertex-indexed rather than per-edge or per-triangle.

```python
--8<-- "docs/examples/object/buffer_geometry.py"
```
