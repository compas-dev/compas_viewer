# Side-dock Controls

Configure the side dock before constructing the Viewer. Controls update durable
scene-object state and call the matching public refresh operation. Transform
refresh updates transformation buffers without rebuilding geometry; appearance
refresh synchronizes display settings such as visibility and opacity.

```python
--8<-- "docs/examples/ui/sidedock.py"
```
