from compas_robots import RobotModel
from compas_robots.resources import GithubPackageMeshLoader

from compas_viewer import Viewer
from compas_viewer.layout import Slider
from compas_viewer.layout import Treeform
from compas_viewer.scene.robotobject import RobotModelObject

viewer = Viewer(rendermode="lighted")


github = GithubPackageMeshLoader("ros-industrial/abb", "abb_irb6600_support", "kinetic-devel")
model = RobotModel.from_urdf_file(github.load_urdf("irb6640.urdf"))
model.load_geometry(github)


robot_object: RobotModelObject = viewer.add(model, show_lines=False, configuration=model.random_configuration())  # type: ignore


def rotate(value, robot_object: RobotModelObject, index: int):
    config = robot_object.configuration
    config.joint_values[index] = value / 360 * 2 * 3.14159
    robot_object.update(config)


for i, joint in enumerate(robot_object.configuration.joint_names):
    slider = Slider(
        rotate,
        0,
        -180,
        180,
        1,
        joint,
        kwargs={"robot_object": robot_object, "index": i},
    )
    slider = viewer.layout.sidedock.add_element(slider)


treeform = Treeform(viewer.tree, {"Name": ".name", "Object": ""})

viewer.layout.sidedock.add_element(treeform)

robot_object.update()

viewer.show()
