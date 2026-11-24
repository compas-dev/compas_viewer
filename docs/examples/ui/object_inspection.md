# Inspect Objects and Data

Select the sphere in the viewport or the hierarchy in the **Scene** tab. The
detail area below the hierarchy derives controls such as name, opacity, colors,
and display options from the stable scene object's declared editable state.
Editing these controls changes durable scene data; Viewer owns the
corresponding render and UI refresh.

Choose **Details** with one Scene object selected to compare that editing
surface with its read-only snapshot. The snapshot keeps four ordered sections:

1. **Identity** identifies the scene object and represented item.
2. **General Scene State** reports visibility, base color, opacity, and local
   transformation.
3. **Type-Specific Scene State** reports only the fields declared by that
   concrete scene-object type, using stable `namespace.field` labels.
4. **Represented Item Parameters** reports safe public-constructor parameters
   when the item is bound.

The snapshot includes declared fields that have no generic editor. It does not
discover arbitrary Python properties, change values, refresh the renderer, or
resolve an unbound item. With multiple Scene objects selected, Details keeps
the compact count, type, and name summary instead.

Open **Data** and select the Mesh row. Although the same Mesh has two Scene
placements, Data lists it once and reports both referrers. **Data Details** is
read-only and presents these tabs in order:

1. **Parameters** for safe public-constructor attributes.
2. **General Attributes** for the ordered `Mesh.attributes` mapping, including
   `discipline` and `revision` from this example.
3. **Vertices**, **Edges**, and **Faces** for the declared component domains.

The Graph row uses the same first two tabs followed by **Nodes** and **Edges**.
Component columns come only from the declared default mappings. Effective
values show both defaults and local overrides: for example, most Mesh vertices
have the default temperature `20.0`, while vertex `2` has `45.0`; Graph node
`A` overrides `support` and its edge overrides `force`. Sparse undeclared
attributes are intentionally omitted. Other bound data types show the
**Parameters** tab only, while unresolved rows remain metadata-only. Data
Details never loads, resolves, edits, deletes, or takes ownership of an item.

The example explicitly passes a setup-time sidebar composition containing the
opt-in **Attributes** inspector. Select the mesh in the **Scene** domain and
open that inspector. Unlike Data Details, this component is an editing surface.
The Viewer creates separate tables for vertices, edges, and faces. Columns come
from the mesh's `default_vertex_attributes`, `default_edge_attributes`, and
`default_face_attributes`; individual element values may override those
defaults. The reset action removes explicit values from selected cells so they
expose their declared defaults again.

The tables currently edit scalar values. General datastructure attributes,
sparse attribute authoring, undo, and viewport subobject selection are outside
this editing interface; inspect general attributes through Data Details or
change them in Python.

Sidebar definitions are shallow-copied and consumed by the first `Viewer(...)`
construction in a process. Mutating `viewer.sidebar_items` later does not add
or remove live components, and subsequent constructor calls return the existing
singleton and ignore new composition inputs. Use a fresh process and
application lifecycle for a different composition.

```python
--8<-- "docs/examples/ui/object_inspection.py"
```
