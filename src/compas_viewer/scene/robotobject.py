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

        @property
        def show_visual(self):
            return self._show_visual

        @show_visual.setter
        def show_visual(self, value: bool):
            if value == self._show_visual:
                return
            self._show_visual = value
            for mesh_obj in self.draw_visual():
                if value:
                    self.viewer.tree.add_object(mesh_obj, self)
                    self.viewer.instance_colors[mesh_obj] = mesh_obj.instance_color
                else:
                    self.viewer.tree.remove_object(mesh_obj)

        @property
        def show_collision(self):
            return self._show_collision

        @show_collision.setter
        def show_collision(self, value: bool):
            if value == self._show_collision:
                return
            self._show_collision = value
            for mesh_obj in self.draw_collision():
                if value:
                    self.viewer.tree.add_object(mesh_obj, self)
                    self.viewer.instance_colors[mesh_obj] = mesh_obj.instance_color
                else:
                    self.viewer.tree.remove_object(mesh_obj)

        def init(self):
            """Initialize the viewer object."""

            for mesh_obj in self.draw_visual():
                mesh_obj.init()
                if self.show_visual:
                    print("RobotModelObject.init()")
                    self.viewer.tree.add_object(mesh_obj, self)
                    self.viewer.instance_colors[mesh_obj] = mesh_obj.instance_color

            for mesh_obj in self.draw_collision():
                mesh_obj.init()
                if self.show_collision:
                    self.viewer.tree.add_object(mesh_obj, self)
                    self.viewer.instance_colors[mesh_obj] = mesh_obj.instance_color

        def transform(self, geometry, transformation: Transformation):
            geometry.transformation = transformation

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
            )

            return mesh_object

        def update(self, joint_state: Optional[Configuration] = None):
            """Update the viewer."""

            if joint_state:

                self.configuration = joint_state

                if self.show_visual:
                    for obj, transformation in zip(
                        self.draw_visual(), self.model.compute_transformations(joint_state).values()
                    ):
                        if obj.transformation != transformation:
                            obj.transformation = transformation
                            obj._update_matrix()

                if self.show_collision:
                    for obj, transformation in zip(
                        self.draw_collision(), self.model.compute_transformations(joint_state).values()
                    ):
                        if obj.transformation != transformation:
                            obj.transformation = transformation
                            obj._update_matrix()

            self.viewer.renderer.update()

except ImportError:
    pass
