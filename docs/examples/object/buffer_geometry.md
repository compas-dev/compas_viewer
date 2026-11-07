# Buffer Geometry

Use `BufferGeometry` when shared vertices and indexed primitives already exist
as Python or NumPy arrays and should be sent directly to the renderer. Edges
and triangles keep their indices; the Viewer does not expand the shared vertex
table into duplicate positions.

The general constructor can combine points, edges, and triangles. For one
primitive type, use `BufferGeometry.from_points`,
`BufferGeometry.from_vertices_and_edges`, or
`BufferGeometry.from_vertices_and_triangles`.

```python
--8<-- "docs/examples/object/buffer_geometry.py"
```
