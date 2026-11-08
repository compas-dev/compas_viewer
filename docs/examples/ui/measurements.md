# Distance Measurements

Configure the informational unit and display precision, add geometry with
visible vertices and edges, and start a one-shot fixed-distance interaction.
Move the pointer to inspect the live preview and left-click two snap points.
The completed dimension becomes a selected root-level scene object.

```python
--8<-- "docs/examples/ui/measurements.py"
```

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

Snap priority is point, vertex, or node; then line or edge; then face or
surface. Fixed mode accepts every category and copies the snapped world points.
Associative mode links to points, vertices and nodes with stable serializable
keys, and normalized positions on lines and edges. Face and surface
associations are not supported yet. They remain available in fixed mode, while
associative mode shows a rejection instead of falling back to a fixed point.

There is no construction-plane or background fallback. A background click does
not create an anchor. While a measurement is active, left-click input is
reserved for the tool; right-drag rotation, Shift + right-drag panning, and
wheel zoom continue to work. Press `Escape` or use **Measure → Cancel
Measurement** to cancel.

The unit is a label only: it never rescales coordinates. Precision controls
display formatting only and is not a geometric tolerance. Transient inspection
labels use the current values from the **Units and Measurement** tab.
