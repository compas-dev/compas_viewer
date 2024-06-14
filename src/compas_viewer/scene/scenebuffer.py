from compas_viewer.renderer.shaders import Shader
from compas.geometry import Translation
from compas_viewer.gl import make_index_buffer
from compas_viewer.gl import make_vertex_buffer
from compas_viewer.gl import make_storage_buffer
import numpy as np

class SceneBuffer():
    def __init__(self):
        self.vertices = []
        self.colors = []
        self.lines = []
        self.faces = []
        self.object_ids = [] # object ids per vertex
        self.matrices = []
        self.shader = None

    def init(self):
        
        self.vertices = [
            0.0, 0.0, 0.0,
            1.0, 0.0, 0.0,
            1.0, 1.0, 0.0,

            0.0, 0.0, 0.0,
            1.0, 0.0, 0.0,
            1.0, 1.0, 0.0,
        ]

        self.vertices_buffer = make_vertex_buffer(self.vertices)

        self.colors = [
            1.0, 0, 0, 1.0,
            1.0, 0, 0, 1.0,
            1.0, 0, 0, 1.0,

            0, 1.0, 0, 1.0,
            0, 1.0, 0, 1.0,
            0, 1.0, 0, 1.0,
        ]

        self.colors_buffer = make_vertex_buffer(self.colors)

        self.faces = [
            0, 1, 2, 0, 1, 2
        ]
        self.faces_buffer = make_index_buffer(self.faces)

        self.object_ids = [
            0, 0, 0, 1, 1, 1
        ]
        self.object_ids_buffer = make_index_buffer(self.object_ids)

        self.n = 6
        self.matrices = np.array([Translation.from_vector([0,0,1]).transposed().matrix, Translation.from_vector([0,0,2]).transposed().matrix], dtype=np.float32)
        self.matrices_buffer = make_storage_buffer(self.matrices)

        self.shader = Shader("scene")



    def draw(self, projection, viewworld):
        """Draw the object from its buffers"""
        
        self.shader.bind()

        self.shader.uniform4x4("projection", projection)
        self.shader.uniform4x4("viewworld", viewworld)
        
        self.shader.enable_attribute("position")
        self.shader.enable_attribute("color")
        self.shader.enable_attribute("object")
        self.shader.uniform4x4xN("matrices", self.matrices)
        self.shader.bind_attribute("position", self.vertices_buffer, step=3)
        self.shader.bind_attribute("color", self.colors_buffer, step=4)
        self.shader.bind_int_attribute("object", self.object_ids_buffer, step=1)
        self.shader.draw_triangles(
            elements=self.faces_buffer,
            n=self.n,
        )

        self.shader.disable_attribute("position")
        self.shader.disable_attribute("color")
        self.shader.disable_attribute("object")

        self.shader.release()