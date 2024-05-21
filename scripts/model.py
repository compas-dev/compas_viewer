from compas_assembly.geometry import Arch
from compas_model.elements import BlockElement
from compas_model.models import Model

from compas.colors import Color
from compas.plugins import plugin
from compas.scene import register
from compas.scene import register_scene_objects
from compas_viewer import Viewer
from compas_viewer.scene import GroupObject


class ModelObject(GroupObject):
    def __init__(self, model, **kwargs):

        elements = []

        for element in model.elements():
            element: BlockElement

            if element.is_support:
                color: Color = Color.red().lightened(50)
                show_faces = True
            else:
                color = Color(0.8, 0.8, 0.8)
                show_faces = False

            elements.append(
                (
                    element.geometry,
                    {
                        "show_faces": show_faces,
                        "surfacecolor": color,
                        "linecolor": color.contrast,
                        "show_points": False,
                    },
                )
            )

        blocks = (elements, {"name": "blocks"})
        interfaces = ([], {"name": "interfaces"})
        forces = ([], {"name": "forces"})
        super().__init__([blocks, interfaces, forces], name=model.name, **kwargs)


register_scene_objects()  # This has to be called before registering the model object
register(Model, ModelObject, context="Viewer")


template = Arch(rise=3, span=10, thickness=0.3, depth=0.5, n=30)

model = Model()

for block in template.blocks():
    model.add_element(BlockElement(shape=block))

viewer = Viewer()


viewer.scene.add(model)

viewer.show()
