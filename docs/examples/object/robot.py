from compas_robots import RobotModel
from compas_robots.resources import GithubPackageMeshLoader
from compas_robots.viewer.scene.robotmodelobject import RobotModelObject

from compas_viewer import Viewer
from compas_viewer.layout import Slider
from compas_viewer.layout import Treeform

viewer = Viewer(rendermode="lighted")


github = GithubPackageMeshLoader("ros-industrial/abb", "abb_irb6600_support", "kinetic-devel")
model = RobotModel.from_urdf_file(github.load_urdf("irb6640.urdf"))
model.load_geometry(github)

configuration = model.random_configuration()
robot_object: RobotModelObject = viewer.scene.add(model, show_lines=False, show_points=False, configuration=configuration)  # type: ignore


def rotate(value, robot_object: RobotModelObject, index: int):
    config = robot_object.configuration
    config.joint_values[index] = value / 360 * 2 * 3.14159
    robot_object.update_joints(config)


for i, joint in enumerate(robot_object.configuration.joint_names):
    slider = Slider(
        rotate,
        configuration.joint_values[i] / 360 * 2 * 3.14159,
        -180,
        180,
        1,
        joint,
        robot_object=robot_object,
        index=i,
    )
    slider = viewer.layout.sidedock.add_element(slider)


treeform = Treeform(viewer.scene, {"Name": (lambda o: o.name), "Object": (lambda o: o)})

viewer.layout.sidedock.add_element(treeform)

robot_object.update_joints(robot_object.configuration)

viewer.show()
