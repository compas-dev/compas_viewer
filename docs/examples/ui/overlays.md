# Scale and Legend Overlays

Add transient screen information directly to the Viewer. Overlays are drawn in
the order in which they are added. They do not become scene objects and are not
saved with the scene.

The scale bar is exact throughout an orthographic view. In a perspective view,
it reports scale at the camera-target depth and states this limitation in its
label.

```python
--8<-- "docs/examples/ui/overlays.py"
```
