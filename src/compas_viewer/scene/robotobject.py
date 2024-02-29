try:

    from typing import Optional

    from compas.colors import Color
    from compas.datastructures import Mesh
    from compas.geometry import Transformation
    from compas_robots import Configuration
    from compas_robots import RobotModel
    from compas_robots.scene import BaseRobotModelObject

    from .meshobject import MeshObject
    from .sceneobject import ViewerSceneObject

    class RobotModelObject(BaseRobotModelObject, ViewerSceneObject):
        """Viewer scene object for displaying COMPAS Robot geometry.

        Parameters
        ----------
        model : :class:`compas_robots.RobotModel`
            The robot model.
        configuration : :class:`compas_robots.Configuration`, optional
            The initial configuration of the robot. Defaults to the zero configuration.
        show_visual : bool, optional
            Toggle the visibility of the visual geometry. Defaults to True.
        show_collision : bool, optional
            Toggle the visibility of the collision geometry. Defaults to False.
        hide_coplanaredges : bool, optional
            True to hide the coplanar edges. It will override the value in the config file.
        use_vertexcolors : bool, optional
            True to use vertex color. It will override the value in the config file.
        **kwargs : dict, optional
            Additional keyword arguments.
            For more info, see :class:`compas_viewer.scene.ViewerSceneObject`.

        See Also
        --------
        :class:`compas_robots.scene.BaseRobotModelObject`
        """

        def __init__(
            self,
            model: RobotModel,
            configuration: Optional[Configuration] = None,
            show_visual: Optional[bool] = None,
            show_collision: Optional[bool] = None,
            hide_coplanaredges: Optional[bool] = None,
            use_vertexcolors: Optional[bool] = None,
            **kwargs
        ):
            self.use_vertexcolors = use_vertexcolors
            self.hide_coplanaredges = hide_coplanaredges
            self._show_visual = show_visual or True
            self._show_collision = show_collision or False
            self.configuration: Configuration = configuration or model.zero_configuration()
            super(RobotModelObject, self).__init__(model=model, **kwargs)

            self.visual_objects: list[MeshObject] = self.draw_visual()
            self.collision_objects: list[MeshObject] = self.draw_collision()

        @property
        def show_visual(self):
            return self._show_visual

        @show_visual.setter
        def show_visual(self, value: bool):
            if value == self._show_visual:
                return
            self._show_visual = value
            for i, visual_object in enumerate(self.visual_objects):
                if value:
                    self.viewer.tree.add_object(visual_object, self.visual_objects[i - 1] if i > 0 else self)
                    self.viewer.instance_colors[visual_object.instance_color.rgb255] = visual_object
                else:
                    self.viewer.tree.remove_object(visual_object)

        @property
        def show_collision(self):
            return self._show_collision

        @show_collision.setter
        def show_collision(self, value: bool):
            if value == self._show_collision:
                return
            self._show_collision = value
            for i, collision_object in enumerate(self.collision_objects):
                if value:
                    self.viewer.tree.add_object(collision_object, self.visual_objects[i - 1] if i > 0 else self)
                    self.viewer.instance_colors[collision_object.instance_color.rgb255] = collision_object
                else:
                    self.viewer.tree.remove_object(collision_object)

        def init(self):
            """Initialize the robot object with creating the visual and collision objects."""
            for i, visual_object in enumerate(self.visual_objects):
                visual_object.init()
                if self.show_visual:
                    self.viewer.tree.add_object(visual_object, self.visual_objects[i - 1] if i > 0 else self)
                    self.viewer.instance_colors[visual_object.instance_color.rgb255] = visual_object

            for i, collision_object in enumerate(self.collision_objects):
                collision_object.init()
                if self.show_collision:
                    self.viewer.tree.add_object(collision_object, self.visual_objects[i - 1] if i > 0 else self)
                    self.viewer.instance_colors[collision_object.instance_color.rgb255] = collision_object

        def transform(self, geometry, transformation: Transformation):
            """Transform the geometry by a given transformation.

            See Also
            --------
            :class:`compas_robots.scene.AbstractRobotModelObject`
            """
            geometry.transformation = transformation * geometry.transformation

        def create_geometry(
            self, geometry: Mesh, name: Optional[str] = None, color: Optional[Color] = None
        ) -> MeshObject:
            """Create a mesh object from a given geometry.

            See Also
            --------
            :class:`compas_robots.scene.AbstractRobotModelObject`
            """
            mesh_object = MeshObject(  # type: ignore
                geometry,
                viewer=self.viewer,
                parent=None,
                is_selected=self.is_selected,
                is_locked=self.is_locked,
                is_visible=self.is_visible,
                show_points=self.show_points,
                show_lines=self.show_lines,
                show_faces=self.show_faces,
                pointscolor=self.pointscolor,
                linescolor=self.linescolor,
                facescolor=color or self.facescolor,
                lineswidth=self.lineswidth,
                pointssize=self.pointssize,
                opacity=self.opacity,
                config=self.viewer.scene_config,
                hide_coplanaredges=self.hide_coplanaredges,
                use_vertexcolors=self.use_vertexcolors,
                name=name,
                transformation=Transformation(),
            )

            return mesh_object

        def update(self, joint_state: Optional[Configuration] = None, update_buffers: bool = False):
            """Update the viewer."""
            if not self.viewer.started or joint_state is not None:
                self.configuration = joint_state or self.configuration
                super().update(self.configuration, self.show_visual, self.show_collision)

                if self.show_visual:
                    for obj in self.visual_objects:
                        obj._update_matrix()
                        if update_buffers:
                            obj.update_buffers()

                if self.show_collision:
                    for obj in self.collision_objects:
                        obj._update_matrix()
                        if update_buffers:
                            obj.update_buffers()

            self.viewer.renderer.update()

except ImportError:
    pass
