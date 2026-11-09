# Distance Measurements

Configure the informational unit and display precision, add geometry with
visible vertices and edges, and start a one-shot fixed-distance interaction.
The completed dimension becomes a selected root-level scene object.

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
   root-level distance dimension, then stops.

Moving to the background hides the available-point palette. The palette is
guidance: its individual points are projected without separate occlusion
tests. The highlighted winner is the only click-eligible result and must pass
the configured screen-radius and depth checks. The depth check searches the
hovered object's rendered point footprint rather than relying on one pixel, so
visible receding vertices remain reliable on steeply tilted meshes without
making occluded vertices eligible.

Mesh edges do not participate in measurement acquisition. Standalone Line
objects and Graph edges remain selectable, but continuous locations are not
enumerated as hover markers in this version.

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
`compas.scene.DistanceDimension`; its unit and precision are snapshots taken
when the second anchor is accepted.

Snap priority is point, vertex, or node; then standalone Line or Graph edge;
then face or surface. Fixed mode accepts every available category and copies
the snapped world points. Associative mode links to points, vertices and nodes
with stable serializable keys, and normalized positions on Lines and Graph
edges. Face and surface associations are not supported yet. They remain
available in fixed mode, while associative mode shows a rejection instead of
falling back to a fixed point. Supported Point, Mesh-vertex, or Graph-node
guidance remains visible during that rejection.

There is no construction-plane or background fallback. A background click does
not create an anchor. While a measurement is active, left-click input is
reserved for the tool; right-drag rotation, Shift + right-drag panning, and
wheel zoom continue to work. Press `Escape` or use **Measure → Cancel
Measurement** to cancel.

The unit is a label only: it never rescales coordinates. Precision controls
display formatting only and is not a geometric tolerance. Transient inspection
labels use the current values from the **Units and Measurement** tab.

Completed dimensions are depth-tested world annotations. They remain visible
when they coincide with the measured geometry, but closer geometry can occlude
them.
