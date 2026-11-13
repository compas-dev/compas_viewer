# Distance Measurements

Configure the informational unit and display precision, add geometry with
an otherwise visible Mesh, and start a one-shot fixed-distance interaction.
The completed dimension becomes a selected entry in the flat annotation
collection.

```python
--8<-- "docs/examples/ui/measurements.py"
```

Use the example in these steps:

1. Move the pointer over the rectangular Mesh. All four vertices appear as
   bright hollow square point snaps.
2. Move near one vertex. That vertex becomes the distinct highlighted winner;
   only this filled square winner can be selected.
3. Left-click the highlighted winner. The first anchor remains visible.
4. Move toward another vertex. The available-point palette follows the hovered
   object, and the live line and formatted distance appear when a second winner
   is available.
5. Left-click the second highlighted winner. The tool creates and selects one
   distance-dimension annotation, then stops.

Moving to the background hides the available-point palette. The palette is
guidance: its individual points are projected without separate occlusion
tests. The highlighted winner is the only click-eligible result and must pass
the 18-logical-pixel screen radius and depth checks. The depth check searches the
hovered object's rendered point footprint rather than relying on one pixel, so
visible receding vertices remain reliable on steeply tilted meshes without
making occluded vertices eligible.

Mesh acquisition does not require ordinary vertex glyphs. While measurement is
active, an otherwise visible face-only or edge-only Mesh receives an invisible
measurement footprint for every vertex in the acquisition pass. This example
sets `show_vertices=False` to exercise that path; the hollow guides still
communicate eligibility, while the footprints never appear in ordinary
rendering. A hidden Mesh or one with no visible face, edge, or vertex
representation remains excluded.

Only displayed discrete guidance participates in measurement acquisition:
Point objects, Mesh vertices, and Graph nodes. Lines, edges, faces, and surfaces
are not themselves candidates. Missing a point therefore creates no anchor
instead of silently accepting nearby unmarked geometry.

The same scene also supports the other modes:

```python
viewer.start_distance_inspection()
viewer.start_distance_dimension(mode="associative")
viewer.cancel_measurement()
```

Starting a mode replaces any active measurement or retained transient
inspection. Each interaction completes after two valid anchors and then stops.
An inspection remains transient and does not change scene data, selection,
serialization, or transform history. Fixed and associative modes create a
`compas.scene.DistanceDimension` in `viewer.scene.annotations`; its unit and
precision are snapshots taken when the second anchor is accepted. The entry is
selected through `viewer.state.annotation_selection`, independently from
spatial object selection.

With that single distance entry selected, use **Annotations → Measurement
Format** to edit its durable **Coordinate Unit** or **Display Precision**.
Coordinate Unit is trimmed and blank input stores no unit. Precision is a
fixed-point decimal-place count from 0 through 15 inclusive. Values outside the
range are rejected rather than clamped or truncated. These controls edit only
the selected dimension: they do not convert its value, change its anchors, or
alter the **Grid and Units** defaults. Conversely, changing Grid and Units
affects transient labels and dimensions created afterward, not this existing
entry. If a dimension has an explicit label, that text remains verbatim and
hides any generated formatting change until the override is removed, but it
does not relax precision validation.

Fixed mode copies the selected point, vertex, or node coordinates. Associative
mode links to those same displayed components using their stable serializable
keys. The acquisition targets are identical; only persistence differs.

There is no construction-plane or background fallback. A background click does
not create an anchor. While a measurement is active, left-click input is
reserved for the tool; right-drag rotation, Shift + right-drag panning, and
wheel zoom continue to work. Press `Escape` or use **Measure → Cancel
Measurement** to cancel.

The unit is a label only: it never rescales coordinates. Precision controls
display formatting only and is not a geometric tolerance. Transient inspection
labels use the current values from the **Grid and Units** section of the
**System** tab.

Completed dimensions render in a final persistent-annotation pass without
depth testing or depth writes, so scene geometry cannot hide them.

Use the **Annotations** tab to hide, select, or remove a dimension. When exactly
one distance dimension is selected, the detail area provides an explicit Name
field, its read-only Type, Measurement Format controls, and controls for color,
line width, text size, arrow size, and label offset. These style sizes and
offsets use logical screen pixels and do not alter anchors, unit, precision, or
label text. Measurement Format is hidden for unsupported selection states,
including no selection, multiple selection, non-distance annotations, and
unresolved annotation data bindings.
