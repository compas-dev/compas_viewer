# Side-dock Controls

Configure the side dock before constructing the Viewer. Controls update durable
scene-object state and explicitly refresh the transient Viewer render object
when its transformation changes. Display-only changes such as opacity require
only a repaint.

```python
--8<-- "docs/examples/ui/sidedock.py"
```
