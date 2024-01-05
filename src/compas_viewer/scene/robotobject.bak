from compas_view2.collections import Collection

from .collectionobject import CollectionObject

import itertools
from compas.geometry import Line
from compas.geometry import Plane
from compas.geometry import Circle
from compas.geometry import Transformation
from compas.geometry import Rotation
from compas.robots import Geometry
from math import radians


class RobotObject(CollectionObject):
    """Object for displaying COMPAS RobotModel.

    Attributes
    ----------
    robot : :class:`compas.robots.RobotModel`
        The compas robot model.
    joints : dict
        Dictionary of joints and their corresponding objects.
    link_objs : list
        Dictionary of links and their corresponding objects.
    """

    def __init__(self, robot, **kwargs):
        kwargs.update({"name": robot.name})
        super().__init__(Collection(), **kwargs)
        self.robot = robot
        self.joints = {}
        self.link_objs = {}
        self.create(robot.root, self)

    def create(self, link, parent, parent_joint=None):
        """Recursively create the robot joints and links in hierrachy.

        Parameters
        ----------
        link: :class:`compas.robots.Joint`
            The robot link to create.
        parent: :class:`compas_view2.objects.collectionobject.CollectionObject`
            The parent compas_view2 collection object.
        parent_joint: :class:`compas.robots.Joint`
            The parent joint of the link.

        Returns
        -------
        None

        """
        meshes = []

        for item in itertools.chain(link.visual):
            meshes.extend(Geometry._get_item_meshes(item))
            if item.origin:
                for mesh in meshes:
                    mesh.transform(Transformation.from_frame(item.origin))

        if meshes:
            obj = parent.add(Collection(meshes), name=link.name, show_lines=False)
        else:
            lines = []
            for joint in link.joints:
                line = Line([0, 0, 0], joint.origin.point)
                lines.append(line)
                if parent_joint:
                    lines.append(Circle(Plane([0, 0, 0], parent_joint.axis.vector), line.length / 3))
            obj = parent.add(Collection(lines), name=link.name)

        if parent_joint:
            obj.matrix = Transformation.from_frame(parent_joint.origin).matrix
            self.joints[parent_joint.name] = {
                "link_obj": obj,
                "joint": parent_joint,
                "axis": parent_joint.axis.vector,
                "origin": parent_joint.origin,
            }

        self.link_objs[link.name] = obj

        for joint in link.joints:
            self.create(joint.child_link, parent=obj, parent_joint=joint)

    def rotate_joint(self, joint_name, angle):
        """Rotate the joint by the given angle.

        Parameters
        ----------
        joint_name: str
            The name of the joint to rotate.
        angle: float
            The angle to rotate the joint by.

        Returns
        -------
        None

        """
        joint = self.joints[joint_name]
        T = Transformation.from_frame(joint["origin"])
        R = Rotation.from_axis_and_angle(joint["axis"], radians(angle))
        joint["link_obj"].matrix = (T * R).matrix
