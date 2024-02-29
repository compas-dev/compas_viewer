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
            Robot model.
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
            configuration: Optional[Configuration],
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
            self.configuration = configuration or model.zero_configuration()
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
            """Initialize the viewer object."""

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
            geometry.transformation = geometry.transformation * transformation

        def create_geometry(
            self, geometry: Mesh, name: Optional[str] = None, color: Optional[Color] = None
        ) -> MeshObject:
            """Draw geometry."""

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

        def update(self, joint_state: Optional[Configuration] = None):
            """Update the viewer."""

            super().update(joint_state, self.show_visual, self.show_collision)

            if self.show_visual:
                for obj in self.draw_visual():
                    obj._update_matrix()

            if self.show_collision:
                for obj in self.draw_collision():
                    obj._update_matrix()

            self.viewer.renderer.update()

except ImportError:
    pass
