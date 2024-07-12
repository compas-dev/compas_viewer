from compas_robots import RobotModel
from compas_robots.resources import GithubPackageMeshLoader
from compas_robots.viewer.scene.robotmodelobject import RobotModelObject
from compas_viewer.components import Slider
from compas_viewer import Viewer

viewer = Viewer()
viewer.renderer.rendermode="lighted"

github = GithubPackageMeshLoader("ros-industrial/abb", "abb_irb6600_support", "kinetic-devel")
model = RobotModel.from_urdf_file(github.load_urdf("irb6640.urdf"))
model.load_geometry(github)

configuration = model.zero_configuration()
robot_object: RobotModelObject = viewer.scene.add(model, show_lines=False, configuration=configuration)  # type: ignore

viewer.ui.sidedock.show = True

def make_rotate_function(index):
    def rotate(slider: Slider, value: int):
        config = robot_object.configuration
        config.joint_values[index] = value / 360 * 2 * 3.14159
        robot_object.update_joints(config)
    return rotate

for i, joint in enumerate(robot_object.configuration.joint_names):
    rotate_function = make_rotate_function(i)
    viewer.ui.sidedock.add(Slider(title=joint, starting_val=0, min_val=-180, max_val=180, step=1, action=rotate_function))


robot_object.update_joints(robot_object.configuration)

viewer.show()
