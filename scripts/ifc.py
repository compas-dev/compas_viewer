from compas.geometry import Box
from compas.geometry import Frame
from compas_viewer.viewer import Viewer

from compas_ifc.model import Model
from compas_ifc.entities import Project
from compas_ifc.entities import Site
from compas_ifc.entities import Building
from compas_ifc.entities import BuildingStorey
from compas_ifc.entities import Column
from compas_ifc.entities import Wall
from compas_ifc.entities import Slab


def make_column(thickness=300, height=3000):
    column = Box.from_diagonal([[-thickness / 2, -thickness / 2, 0], [thickness / 2, thickness / 2, height]])
    return column


def make_wall(thickness=150, length=5000, height=3000):
    wall = Box.from_diagonal([[-thickness / 2, 0, 0], [thickness / 2, length, height]])
    return wall


def make_floor(thickness=150, length=5000, width=5000):
    floor = Box.from_diagonal([[0, 0, -thickness], [length, width, 0]])
    return floor

# Create a simple model

model = Model()
project = model.create(Project, {"Name": "My Project"})
site = model.create(Site, {"Name": "My Site"}, parent=project)
building = model.create(Building, {"Name": "My Building"}, parent=site)
storey = model.create(BuildingStorey, {"Name": "My Storey"}, parent=building)


floor = make_floor()
model.insert(floor, name="floor1", parent=storey, cls=Slab)

column = make_column()
model.insert(column, name="column1", parent=storey, cls=Column, frame=Frame([0, 0, 0]))
model.insert(column, name="column2", parent=storey, cls=Column, frame=Frame([5000, 0, 0]))
model.insert(column, name="column3", parent=storey, cls=Column, frame=Frame([5000, 5000, 0]))
model.insert(column, name="column4", parent=storey, cls=Column, frame=Frame([0, 5000, 0]))

wall = make_wall()
model.insert(wall, name="wall1", parent=storey, cls=Wall)
model.insert(wall, name="wall2", parent=storey, cls=Wall, frame=Frame([5000, 0, 0]))
model.insert(wall, name="wall3", parent=storey, cls=Wall, frame=Frame([5000, 0, 0], xaxis=[0, 1, 0], yaxis=[-1, 0, 0]))
model.insert(wall, name="wall4", parent=storey, cls=Wall, frame=Frame([5000, 5000, 0], xaxis=[0, 1, 0], yaxis=[-1, 0, 0]))

model.save("simple.ifc")

# Load the model and display it
model = Model("simple.ifc", use_occ=False)
model.print_spatial_hierarchy()

viewer = Viewer()


def parse_entity(entity, parent=None):
    if getattr(entity, "body_with_opening", None):
        if isinstance(entity, Wall):
            viewer.scene.add(entity.body_with_opening, name=entity.name, parent=parent)
        if isinstance(entity, Column):
            viewer.scene.add(entity.body_with_opening, name=entity.name, parent=parent)
        if isinstance(entity, Slab):
            viewer.scene.add(entity.body_with_opening, name=entity.name, parent=parent)
    else:
        obj = viewer.scene.add([], name=entity.name, parent=parent)
        for child in entity.children:
            parse_entity(child, parent=obj)


parse_entity(model.project)

viewer.show()
