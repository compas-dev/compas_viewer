from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from compas.colors import Color
from compas_viewer.gl import make_vertex_buffer, make_index_buffer, make_texture_buffer, update_texture_buffer, update_vertex_buffer
from compas_viewer.renderer.shaders import Shader
import OpenGL.GL as GL


class BufferManager:
    """A class to manage and combine buffers from multiple objects for efficient rendering.

    The BufferManager combines vertex data from multiple objects into consolidated buffers
    to minimize draw calls and state changes during rendering.

    Attributes
    ----------
    positions : Dict[str, np.ndarray]
        Combined position buffers for different geometry types (points, lines, faces)
    colors : Dict[str, np.ndarray]
        Combined color buffers for different geometry types
    elements : Dict[str, np.ndarray]
        Combined element index buffers for different geometry types
    buffer_ids : Dict[str, Dict[str, int]]
        OpenGL buffer IDs for positions, colors and elements
    """

    def __init__(self):
        # Shader buffer data
        self.positions: Dict[str, np.ndarray] = {}
        self.colors: Dict[str, np.ndarray] = {}
        self.elements: Dict[str, np.ndarray] = {}
        self.object_indices: Dict[str, np.ndarray] = {}
        self.objects: Dict[Any, int] = {}

        # OpenGL buffer IDs
        self.buffer_ids: Dict[str, Dict[str, int]] = {}

        # Transform data
        self.transforms: List[float] = []

        # Settings data
        self.settings: List[float] = []

        # Initialize empty buffers for each geometry type
        for buffer_type in ["points", "lines", "faces", "backfaces"]:
            self.positions[buffer_type] = np.array([], dtype=np.float32)
            self.colors[buffer_type] = np.array([], dtype=np.float32)
            self.elements[buffer_type] = np.array([], dtype=np.int32)
            self.object_indices[buffer_type] = np.array([], dtype=np.float32)
            self.buffer_ids[buffer_type] = {}

    def add_object(self, obj: Any) -> None:
        """Add an object's buffer data to the combined buffers."""

        self.objects[obj] = len(self.transforms)

        # Process geometry data
        if hasattr(obj, "_points_data") and obj._points_data:
            self._add_buffer_data("points", obj._points_data)
        if hasattr(obj, "_lines_data") and obj._lines_data:
            self._add_buffer_data("lines", obj._lines_data)
        if hasattr(obj, "_frontfaces_data") and obj._frontfaces_data:
            self._add_buffer_data("faces", obj._frontfaces_data)
        if hasattr(obj, "_backfaces_data") and obj._backfaces_data:
            self._add_buffer_data("backfaces", obj._backfaces_data)

        matrix = obj._matrix_buffer if obj._matrix_buffer is not None else np.identity(4, dtype=np.float32).flatten()
        self.transforms.append(matrix)

        # Add default settings (is_selected = 0.0)
        # self.settings.append(1.0)

    def _add_buffer_data(self, buffer_type: str, data: Tuple[List, List, List]) -> None:
        """Add buffer data for a specific geometry type."""
        positions, colors, elements = data

        # Convert to numpy arrays
        pos_array = np.array(positions, dtype=np.float32).flatten()
        col_array = np.array([c.rgba for c in colors], dtype=np.float32).flatten()
        elem_array = np.array(elements, dtype=np.int32).flatten()

        # Update elements to account for offset
        start_idx = len(self.positions[buffer_type]) // 3
        elem_array += start_idx

        # Create vertex indices
        object_index = len(self.transforms)
        obj_indices = np.full(len(positions), object_index, dtype=np.float32)

        # Append to existing buffers
        self.positions[buffer_type] = np.append(self.positions[buffer_type], pos_array)
        self.colors[buffer_type] = np.append(self.colors[buffer_type], col_array)
        self.elements[buffer_type] = np.append(self.elements[buffer_type], elem_array)
        self.object_indices[buffer_type] = np.append(self.object_indices[buffer_type], obj_indices)

    def create_buffers(self) -> None:
        """Create OpenGL buffers from the collected data."""
        # Create transform buffer and texture
        transforms_array = np.array(self.transforms, dtype=np.float32)
        self.transform_texture = make_texture_buffer(transforms_array)

        # Create settings buffer and texture using GL_R32F for a single float per texel
        settings_array = np.array([0, 0, 1], dtype=np.float32) # TODO: finish this
        self.settings_texture = make_texture_buffer(settings_array, internal_format=GL.GL_R32F)
        print(settings_array)

        for buffer_type in self.positions:
            if len(self.positions[buffer_type]):
                self.buffer_ids[buffer_type]["positions"] = make_vertex_buffer(self.positions[buffer_type])
                self.buffer_ids[buffer_type]["colors"] = make_vertex_buffer(self.colors[buffer_type])
                self.buffer_ids[buffer_type]["elements"] = make_index_buffer(self.elements[buffer_type])
                self.buffer_ids[buffer_type]["object_indices"] = make_vertex_buffer(self.object_indices[buffer_type])

    def draw(self, shader: Shader, wireframe: bool = False, is_lighted: bool = True) -> None:
        """Draw all objects using the combined buffers."""
        shader.uniform1i("is_grid", False)
        shader.enable_attribute("position")
        shader.enable_attribute("color")
        shader.enable_attribute("object_index")

        # Draw faces
        if not wireframe:
            shader.uniform1i("is_lighted", is_lighted)
            shader.uniform1i("element_type", 2)

            for face_type in ["faces", "backfaces"]:
                if self.buffer_ids[face_type]:
                    shader.bind_attribute("position", self.buffer_ids[face_type]["positions"])
                    shader.bind_attribute("color", self.buffer_ids[face_type]["colors"], step=4)
                    shader.bind_attribute("object_index", self.buffer_ids[face_type]["object_indices"], step=1)
                    shader.draw_triangles(elements=self.buffer_ids[face_type]["elements"], n=len(self.elements[face_type]))

        # Draw lines
        shader.uniform1i("is_lighted", False)
        shader.uniform1i("element_type", 1)
        if self.buffer_ids["lines"]:
            shader.bind_attribute("position", self.buffer_ids["lines"]["positions"])
            shader.bind_attribute("color", self.buffer_ids["lines"]["colors"], step=4)
            shader.bind_attribute("object_index", self.buffer_ids["lines"]["object_indices"], step=1)
            shader.draw_lines(elements=self.buffer_ids["lines"]["elements"], n=len(self.elements["lines"]), width=1.0)

        # Draw points
        shader.uniform1i("element_type", 0)
        if self.buffer_ids["points"]:
            shader.bind_attribute("position", self.buffer_ids["points"]["positions"])
            shader.bind_attribute("color", self.buffer_ids["points"]["colors"], step=4)
            shader.bind_attribute("object_index", self.buffer_ids["points"]["object_indices"], step=1)
            shader.draw_points(elements=self.buffer_ids["points"]["elements"], n=len(self.elements["points"]), size=10.0)

        shader.disable_attribute("object_index")
        shader.disable_attribute("position")
        shader.disable_attribute("color")

    def clear(self) -> None:
        """Clear all buffer data."""
        for buffer_type in self.positions:
            self.positions[buffer_type] = np.array([], dtype=np.float32)
            self.colors[buffer_type] = np.array([], dtype=np.float32)
            self.elements[buffer_type] = np.array([], dtype=np.int32)
            self.buffer_ids[buffer_type] = {}

        self.transforms = []
        self.settings = []

    def update_object_transform(self, obj: Any) -> None:
        """Update the transformation matrix for a single object.

        Parameters
        ----------
        obj : Any
            The object whose transform should be updated.
        """
        if obj not in self.objects:
            return

        index = self.objects[obj]
        obj._update_matrix()
        if obj._matrix_buffer is None:
            matrix = np.identity(4, dtype=np.float32).flatten()
        else:
            matrix = np.array(obj._matrix_buffer, dtype=np.float32)
        self.transforms[index] = matrix
        byte_offset = index * (4 * 16)
        update_texture_buffer(matrix, self.transform_texture, offset=byte_offset)

    def update_object_data(self, obj: Any) -> None:
        """Update the position and color buffers for a single object.

        Parameters
        ----------
        obj : Any
            The object whose buffers should be updated.
        """
        if obj not in self.objects:
            return

        index = self.objects[obj]

        # Update each buffer type that the object has
        buffer_types = []
        if hasattr(obj, "_points_data") and obj._points_data:
            buffer_types.append("points")
        if hasattr(obj, "_lines_data") and obj._lines_data:
            buffer_types.append("lines")
        if hasattr(obj, "_frontfaces_data") and obj._frontfaces_data:
            buffer_types.append("faces")
        if hasattr(obj, "_backfaces_data") and obj._backfaces_data:
            buffer_types.append("backfaces")

        for buffer_type in buffer_types:
            # Get the data based on buffer type
            if buffer_type == "points":
                data = obj._points_data
            elif buffer_type == "lines":
                data = obj._lines_data
            elif buffer_type == "faces":
                data = obj._frontfaces_data
            else:  # backfaces
                data = obj._backfaces_data

            positions, colors, _ = data  # We don't update elements as topology stays the same

            # Convert to numpy arrays
            pos_array = np.array(positions, dtype=np.float32).flatten()
            col_array = np.array([c.rgba for c in colors], dtype=np.float32).flatten()

            # Find the start and end indices for this object in the buffer
            start_idx = 0
            for i in range(len(self.object_indices[buffer_type])):
                if self.object_indices[buffer_type][i] == index:
                    start_idx = i
                    break

            vertices_per_object = len(positions)

            # Update the position buffer
            pos_byte_offset = start_idx * 3 * 4  # 3 floats per vertex * 4 bytes per float
            pos_byte_size = vertices_per_object * 3 * 4
            update_vertex_buffer(pos_array, self.buffer_ids[buffer_type]["positions"], offset=pos_byte_offset)

            # Update the color buffer
            col_byte_offset = start_idx * 4 * 4  # 4 floats per color * 4 bytes per float
            col_byte_size = vertices_per_object * 4 * 4
            update_vertex_buffer(col_array, self.buffer_ids[buffer_type]["colors"], offset=col_byte_offset)

    def update_object_settings(self, obj: Any, is_selected: bool) -> None:
        """Update the settings for a single object.

        Parameters
        ----------
        obj : Any
            The object whose settings should be updated.
        is_selected : bool
            Whether the object is selected.
        """
        if obj not in self.objects:
            return

        index = self.objects[obj]
        self.settings[index] = float(is_selected)
        byte_offset = index * 4  # 1 float * 4 bytes
        update_texture_buffer(np.array([float(is_selected)], dtype=np.float32), self.settings_texture, offset=byte_offset)
