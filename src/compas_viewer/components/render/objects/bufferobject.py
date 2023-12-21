import numpy as np

from compas.utilities import flatten
from compas.geometry import transform_points_numpy

from compas_viewer.components.render.gl import make_index_buffer
from compas_viewer.components.render.gl import make_vertex_buffer
from compas_viewer.components.render.gl import update_vertex_buffer
from compas_viewer.components.render.gl import update_index_buffer

from .object import Object


class BufferObject(Object):
    """A shared object to handle GL buffer creation and drawings

    Attributes
    ----------
    visualisation : list[str], read-only
        List of visualisation properties which can be edited in the GUI.
    """

    @property
    def visualisation(self):
        options = ["opacity"]
        if hasattr(self, "_points_data"):
            options += ["pointcolor", "show_points", "pointsize"]
        if hasattr(self, "_lines_data"):
            options += ["linecolor", "show_lines", "linewidth"]
        if hasattr(self, "_frontfaces_data"):
            options += ["facecolor", "show_faces"]
        return options

    def make_buffer_from_data(self, data):
        """Create buffers from point/line/face data.

        Parameters
        ----------
        data: tuple
            Contains positions, colors, elements for the buffer

        Returns
        -------
        buffer_dict
           A dict with created buffer indexes
        """
        positions, colors, elements = data
        return {
            "positions": make_vertex_buffer(list(flatten(positions))),
            "colors": make_vertex_buffer(list(flatten(colors))),
            "elements": make_index_buffer(list(flatten(elements))),
            "n": len(list(flatten(elements))),
        }

    def update_buffer_from_data(self, data, buffer, update_positions=True, update_colors=True, update_elements=True):
        """Update existing buffers from point/line/face data.

        Parameters
        ----------
        data: tuple
            Contains positions, colors, elements for the buffer
        buffer: dict
            The dict with created buffer indexes
        update_positions : bool
            Whether to update positions in the buffer dict
        update_colors : bool
            Whether to update colors in the buffer dict
        update_elements : bool
            Whether to update elements in the buffer dict
        """
        positions, colors, elements = data
        if update_positions:
            update_vertex_buffer(list(flatten(positions)), buffer["positions"])
        if update_colors:
            update_vertex_buffer(list(flatten(colors)), buffer["colors"])
        if update_elements:
            update_index_buffer(list(flatten(elements)), buffer["elements"])
        buffer["n"] = len(list(flatten(elements)))

    def make_buffers(self):
        """Create all buffers from object's data"""
        if hasattr(self, "_points_data"):
            data = self._points_data()
            self._points_buffer = self.make_buffer_from_data(data)
            if data[0]:
                self._update_bounding_box(data[0])
        if hasattr(self, "_lines_data"):
            data = self._lines_data()
            self._lines_buffer = self.make_buffer_from_data(data)
            if data[0] and self._bounding_box_center is None:
                self._update_bounding_box(data[0])
        if hasattr(self, "_frontfaces_data"):
            data = self._frontfaces_data()
            self._frontfaces_buffer = self.make_buffer_from_data(data)
            if data[0] and self._bounding_box_center is None:
                self._update_bounding_box(data[0])
        if hasattr(self, "_backfaces_data"):
            data = self._backfaces_data()
            self._backfaces_buffer = self.make_buffer_from_data(data)
            if data[0] and self._bounding_box_center is None:
                self._update_bounding_box(data[0])

    def update_buffers(self):
        """Update all buffers from object's data"""
        if hasattr(self, "_points_data"):
            self.update_buffer_from_data(self._points_data(), self._points_buffer)
        if hasattr(self, "_lines_data"):
            self.update_buffer_from_data(self._lines_data(), self._lines_buffer)
        if hasattr(self, "_frontfaces_data"):
            self.update_buffer_from_data(self._frontfaces_data(), self._frontfaces_buffer)
        if hasattr(self, "_backfaces_data"):
            self.update_buffer_from_data(self._backfaces_data(), self._backfaces_buffer)

    def init(self):
        """Initialize the object"""
        self.make_buffers()
        self._update_matrix()

    def update(self):
        """Update the object"""
        self._update_matrix()
        self.update_buffers()

    def _update_bounding_box(self, positions=None):
        """Update the bounding box of the object"""
        if positions is None:
            positions = []
            if hasattr(self, "_points_data"):
                positions += self._points_data()[0]
            if hasattr(self, "_lines_data"):
                positions += self._lines_data()[0]
            if hasattr(self, "_frontfaces_data"):
                positions += self._frontfaces_data()[0]
            if not positions:
                return

        positions = np.array(positions)
        self._bounding_box = transform_points_numpy(
            np.array([positions.min(axis=0), positions.max(axis=0)]), self._transformation
        )
        self._bounding_box_center = np.average(self.bounding_box, axis=0)

    def draw(self, shader, wireframe=False, is_lighted=False):
        """Draw the object from its buffers"""
        shader.enable_attribute("position")
        shader.enable_attribute("color")
        shader.uniform1i("is_selected", self.is_selected)
        if self._matrix_buffer is not None:
            shader.uniform4x4("transform", self._matrix_buffer)
        shader.uniform1i("is_lighted", is_lighted)
        shader.uniform1f("object_opacity", self.opacity)
        shader.uniform1i("element_type", 2)
        if hasattr(self, "_frontfaces_buffer") and self.show_faces and not wireframe:
            shader.uniform3f("single_color", self.facecolor)
            shader.uniform1i(
                "use_single_color",
                not self.facecolors and not self._is_collection and not getattr(self, "use_vertex_color", False),
            )
            shader.bind_attribute("position", self._frontfaces_buffer["positions"])
            shader.bind_attribute("color", self._frontfaces_buffer["colors"])
            shader.draw_triangles(
                elements=self._frontfaces_buffer["elements"], n=self._frontfaces_buffer["n"], background=self.background
            )
        if hasattr(self, "_backfaces_buffer") and self.show_faces and not wireframe:
            shader.uniform3f("single_color", self.facecolor)
            shader.uniform1i(
                "use_single_color",
                not self.facecolors and not self._is_collection and not getattr(self, "use_vertex_color", False),
            )
            shader.bind_attribute("position", self._backfaces_buffer["positions"])
            shader.bind_attribute("color", self._backfaces_buffer["colors"])
            shader.draw_triangles(
                elements=self._backfaces_buffer["elements"], n=self._backfaces_buffer["n"], background=self.background
            )
        shader.uniform1i("is_lighted", False)
        shader.uniform1i("element_type", 1)
        if hasattr(self, "_lines_buffer") and (self.show_lines or wireframe):
            shader.uniform3f("single_color", self.linecolor)
            shader.uniform1i("use_single_color", not self.linecolors and not self._is_collection)
            shader.bind_attribute("position", self._lines_buffer["positions"])
            shader.bind_attribute("color", self._lines_buffer["colors"])
            shader.draw_lines(
                width=self.linewidth,
                elements=self._lines_buffer["elements"],
                n=self._lines_buffer["n"],
                background=self.background,
            )
        shader.uniform1i("element_type", 0)
        if hasattr(self, "_points_buffer") and self.show_points:
            shader.uniform3f("single_color", self.pointcolor)
            shader.uniform1i("use_single_color", not self.pointcolors and not self._is_collection)
            shader.bind_attribute("position", self._points_buffer["positions"])
            shader.bind_attribute("color", self._points_buffer["colors"])
            shader.draw_points(
                size=self.pointsize,
                elements=self._points_buffer["elements"],
                n=self._points_buffer["n"],
                background=self.background,
            )

        shader.uniform1i("is_selected", 0)
        shader.uniform1f("object_opacity", 1)
        if self._matrix_buffer is not None:
            shader.uniform4x4("transform", np.identity(4).flatten())
        shader.disable_attribute("position")
        shader.disable_attribute("color")

    def draw_instance(self, shader, wireframe=False):
        """Draw the object instance for picking"""
        shader.enable_attribute("position")
        shader.uniform3f("instance_color", self._instance_color)
        if self._matrix_buffer is not None:
            shader.uniform4x4("transform", self._matrix_buffer)
        if hasattr(self, "_points_buffer") and self.show_points:
            shader.bind_attribute("position", self._points_buffer["positions"])
            shader.draw_points(
                size=self.pointsize, elements=self._points_buffer["elements"], n=self._points_buffer["n"]
            )
        if hasattr(self, "_lines_buffer") and (self.show_lines or wireframe):
            shader.bind_attribute("position", self._lines_buffer["positions"])
            shader.draw_lines(width=self.linewidth, elements=self._lines_buffer["elements"], n=self._lines_buffer["n"])
        if hasattr(self, "_frontfaces_buffer") and self.show_faces and not wireframe:
            shader.bind_attribute("position", self._frontfaces_buffer["positions"])
            shader.draw_triangles(elements=self._frontfaces_buffer["elements"], n=self._frontfaces_buffer["n"])
            shader.bind_attribute("position", self._backfaces_buffer["positions"])
            shader.draw_triangles(elements=self._backfaces_buffer["elements"], n=self._backfaces_buffer["n"])
        if self._matrix_buffer is not None:
            shader.uniform4x4("transform", np.identity(4).flatten())
        shader.uniform3f("instance_color", [0, 0, 0])
        shader.disable_attribute("position")
