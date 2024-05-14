from compas.geometry import Polyhedron
from compas_viewer.viewer import Viewer
from compas.geometry import Translation

viewer = Viewer()

p1 = Polyhedron.from_platonicsolid(4)
viewer.scene.add(p1)

p2 = Polyhedron.from_platonicsolid(6)
p2.transform(Translation.from_vector([5, 0, 0]))
viewer.scene.add(p2)

p3 = Polyhedron.from_platonicsolid(8)
p3.transform(Translation.from_vector([10, 0, 0]))
viewer.scene.add(p3)

p4 = Polyhedron.from_platonicsolid(12)
p4.transform(Translation.from_vector([15, 0, 0]))
viewer.scene.add(p4)

p5 = Polyhedron.from_platonicsolid(20)
p5.transform(Translation.from_vector([20, 0, 0]))
viewer.scene.add(p5)

viewer.show()
