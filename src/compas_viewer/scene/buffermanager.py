from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from compas.colors import Color
from compas_viewer.gl import make_vertex_buffer, make_index_buffer
from compas_viewer.renderer.shaders import Shader

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
    object_ranges : Dict[str, List[Tuple[int, int]]]
        Start and end indices for each object's data within the combined buffers
    """

    def __init__(self):
        self.positions: Dict[str, np.ndarray] = {}
        self.colors: Dict[str, np.ndarray] = {}
        self.elements: Dict[str, np.ndarray] = {}
        self.buffer_ids: Dict[str, Dict[str, int]] = {}
        self.object_ranges: Dict[str, List[Tuple[int, int]]] = {}
        
        # Initialize empty buffers for each geometry type
        for buffer_type in ['points', 'lines', 'faces', 'backfaces']:
            self.positions[buffer_type] = np.array([], dtype=np.float32)
            self.colors[buffer_type] = np.array([], dtype=np.float32)
            self.elements[buffer_type] = np.array([], dtype=np.int32)
            self.object_ranges[buffer_type] = []
            self.buffer_ids[buffer_type] = {
                'positions': None,
                'colors': None,
                'elements': None
            }

    def add_object(self, obj: Any) -> None:
        """Add an object's buffer data to the combined buffers.

        Parameters
        ----------
        obj : Any
            The scene object containing buffer data to add
        """
        # Process points data
        if hasattr(obj, '_points_data') and obj._points_data:
            self._add_buffer_data('points', obj._points_data)
            
        # Process lines data    
        if hasattr(obj, '_lines_data') and obj._lines_data:
            self._add_buffer_data('lines', obj._lines_data)

        # Process faces data
        if hasattr(obj, '_frontfaces_data') and obj._frontfaces_data:
            self._add_buffer_data('faces', obj._frontfaces_data)
            
        # # Process backfaces data
        if hasattr(obj, '_backfaces_data') and obj._backfaces_data:
            self._add_buffer_data('backfaces', obj._backfaces_data)

    def _add_buffer_data(self, buffer_type: str, data: Tuple[List, List, List]) -> None:
        """Add buffer data for a specific geometry type.

        Parameters
        ----------
        buffer_type : str
            The type of geometry buffer ('points', 'lines', 'faces', 'backfaces')
        data : tuple
            Tuple containing (positions, colors, elements) lists
        """
        positions, colors, elements = data
        
        # Convert to numpy arrays if not already
        pos_array = np.array(positions, dtype=np.float32).reshape(-1)
        col_array = np.array([c.rgba for c in colors], dtype=np.float32).reshape(-1)
        elem_array = np.array(elements, dtype=np.int32).reshape(-1)
        
        # Record range for this object
        start_idx = len(self.positions[buffer_type]) // 3
        self.object_ranges[buffer_type].append((
            start_idx,
            start_idx + len(positions)
        ))
        
        # Update elements to account for offset
        elem_array += start_idx
        
        # Append to existing buffers
        self.positions[buffer_type] = np.append(self.positions[buffer_type], pos_array)
        self.colors[buffer_type] = np.append(self.colors[buffer_type], col_array)
        self.elements[buffer_type] = np.append(self.elements[buffer_type], elem_array)

    

    def create_buffers(self) -> None:
        """Create OpenGL buffers from the combined data."""
        for buffer_type in self.positions:
            if len(self.positions[buffer_type]):
                self.buffer_ids[buffer_type]['positions'] = make_vertex_buffer(self.positions[buffer_type])
                self.buffer_ids[buffer_type]['colors'] = make_vertex_buffer(self.colors[buffer_type])
                self.buffer_ids[buffer_type]['elements'] = make_index_buffer(self.elements[buffer_type])

    def draw(self, shader: Shader, wireframe: bool = False, is_lighted: bool = True) -> None:
        """Draw all objects using the combined buffers.

        Parameters
        ----------
        shader : Shader
            The shader program to use for rendering
        wireframe : bool, optional
            Whether to render in wireframe mode
        is_lighted : bool, optional
            Whether to apply lighting
        """
        shader.enable_attribute("position")
        shader.enable_attribute("color")
        
        # Draw faces
        if not wireframe:
            shader.uniform1i("is_lighted", is_lighted)
            shader.uniform1i("element_type", 2)
            
            for face_type in ['faces', 'backfaces']:
                if self.buffer_ids[face_type]['positions']:
                    shader.bind_attribute("position", self.buffer_ids[face_type]['positions'])
                    shader.bind_attribute("color", self.buffer_ids[face_type]['colors'], step=4)
                    shader.draw_triangles(
                        elements=self.buffer_ids[face_type]['elements'],
                        n=len(self.elements[face_type])
                    )
        
        # Draw lines
        shader.uniform1i("is_lighted", False)
        shader.uniform1i("element_type", 1)
        if self.buffer_ids['lines']['positions']:
            shader.bind_attribute("position", self.buffer_ids['lines']['positions'])
            shader.bind_attribute("color", self.buffer_ids['lines']['colors'], step=4)
            shader.draw_lines(
                elements=self.buffer_ids['lines']['elements'],
                n=len(self.elements['lines']),
                width=1.0
            )
        
        # Draw points
        shader.uniform1i("element_type", 0)
        if self.buffer_ids['points']['positions']:
            shader.bind_attribute("position", self.buffer_ids['points']['positions'])
            shader.bind_attribute("color", self.buffer_ids['points']['colors'], step=4)
            shader.draw_points(
                elements=self.buffer_ids['points']['elements'],
                n=len(self.elements['points']),
                size=10.0
            )
        
        shader.disable_attribute("position")
        shader.disable_attribute("color")

    def clear(self) -> None:
        """Clear all buffer data."""
        for buffer_type in self.positions:
            self.positions[buffer_type] = np.array([], dtype=np.float32)
            self.colors[buffer_type] = np.array([], dtype=np.float32)
            self.elements[buffer_type] = np.array([], dtype=np.int32)
            self.object_ranges[buffer_type] = []
            self.buffer_ids[buffer_type] = {
                'positions': None,
                'colors': None, 
                'elements': None
            } 