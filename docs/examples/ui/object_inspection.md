# Inspect Objects and Attributes

Select the sphere in the viewport or scene tree and open the **Object** tab.
The Viewer derives controls such as name, opacity, colors, and display
options from the stable scene object's declared editable state. Editing these
controls changes durable scene data; Viewer owns the corresponding render and
UI refresh.

The example explicitly adds the opt-in **Attributes** tab to its custom
sidebar. Select the mesh and open that tab. The Viewer creates separate tables
for vertices, edges, and faces. Table columns come from the mesh's
`default_vertex_attributes`, `default_edge_attributes`, and
`default_face_attributes`; individual element values may override those
defaults. The reset action removes explicit values from selected cells so they
expose their declared defaults again.

The tables currently edit scalar values. Sparse attribute authoring, undo, and
viewport subobject selection are outside this interface.

```python
--8<-- "docs/examples/ui/object_inspection.py"
```
