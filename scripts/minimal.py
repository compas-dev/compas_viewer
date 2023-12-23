import sys
import math

from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtOpenGL

from OpenGL import GL
from OpenGL import GLU
from OpenGL import GLUT
from OpenGL.arrays.vbo import VBO

import ctypes as ct
import numpy as np

from compas.geometry import Transformation, Translation, Rotation, Frame
from compas.geometry import normalize_vector, subtract_vectors, scale_vector, cross_vectors

from compas.utilities import i_to_rgb


VSHADER = """
#version 330

layout(location = 0) in vec3 vertex;
layout(location = 1) in vec3 color;

uniform mat4 P;
uniform mat4 V;
uniform mat4 M;

out vec4 vertex_color;

void main()
{
    gl_Position = P * V * M * vec4(vertex, 1.0);
    vertex_color = vec4(color, 1.0);
}
"""

FSHADER = """
#version 330

in vec4 vertex_color;
out vec4 frag_color;

void main()
{
    frag_color = vertex_color;
}
"""


def make_shader_program(vsource, fsource):
    vertex = compile_vertex_shader(vsource)
    fragment = compile_fragment_shader(fsource)
    program = GL.glCreateProgram()
    GL.glAttachShader(program, vertex)
    GL.glAttachShader(program, fragment)
    GL.glLinkProgram(program)
    result = GL.glGetProgramiv(program, GL.GL_LINK_STATUS)
    if not result:
        raise RuntimeError(GL.glGetProgramInfoLog(program))
    return program


def make_vertex_buffer(data):
    n = len(data)
    vbo = GL.glGenBuffers(1)
    cdata = (ct.c_float * n)(* data)
    fsize = ct.sizeof(ct.c_float)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, fsize * n, cdata, GL.GL_DYNAMIC_DRAW)
    return vbo


def make_index_buffer(data):
    n = len(data)
    vbo = GL.glGenBuffers(1)
    cdata = (ct.c_int * n)(* data)
    isize = ct.sizeof(ct.c_int)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, vbo)
    GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, isize * n, cdata, GL.GL_DYNAMIC_DRAW)
    return vbo


def compile_vertex_shader(source):
    shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
    GL.glShaderSource(shader, source)
    GL.glCompileShader(shader)
    result = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
    if not result:
        raise RuntimeError(GL.glGetShaderInfoLog(shader))
    return shader


def compile_fragment_shader(source):
    shader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
    GL.glShaderSource(shader, source)
    GL.glCompileShader(shader)
    result = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
    if not result:
        raise RuntimeError(GL.glGetShaderInfoLog(shader))
    return shader


def link_shader_program(vertex, fragment):
    program = GL.glCreateProgram()
    GL.glAttachShader(program, vertex)
    GL.glAttachShader(program, fragment)
    GL.glLinkProgram(program)
    result = GL.glGetProgramiv(program, GL.GL_LINK_STATUS)
    if not result:
        raise RuntimeError(GL.glGetProgramInfoLog(program))
    return program


def ortho(l, r, b, t, n, f):
    dx = r - l
    dy = t - b
    dz = f - n
    rx = -(r + l) / (r - l)
    ry = -(t + b) / (t - b)
    rz = -(f + n) / (f - n)
    matrix = [
        [2.0 / dx,        0,         0, rx],
        [       0, 2.0 / dy,         0, ry],
        [       0,        0, -2.0 / dz, rz],
        [       0,        0,         0,  1]
    ]
    return Transformation.from_matrix(matrix)


def perspective(fov, aspect, near, far):
    sy = 1.0 / math.tan(math.radians(fov) / 2.0)
    sx = sy / aspect
    zz = (far + near) / (near - far)
    zw = 2 * far * near / (near - far)
    matrix = [
        [sx,  0,  0,  0],
        [ 0, sy,  0,  0],
        [ 0,  0, zz, zw],
        [ 0,  0, -1,  0]
    ]
    return Transformation.from_matrix(matrix)


def frustum(x0, x1, y0, y1, z0, z1):
    a = (x1 + x0) / (x1 - x0)
    b = (y1 + y0) / (y1 - y0)
    c = -(z1 + z0) / (z1 - z0)
    d = -2 * z1 * z0 / (z1 - z0)
    sx = 2 * z0 / (x1 - x0)
    sy = 2 * z0 / (y1 - y0)
    matrix = [
        [sx,  0,  a, 0],
        [ 0, sy,  b, 0],
        [ 0,  0,  c, d],
        [ 0,  0, -1, 0]
    ]
    return Transformation.from_matrix(matrix)


def lookat(eye, target, up):
    d = normalize_vector(subtract_vectors(target, eye))
    r = cross_vectors(d, normalize_vector(up))
    u = cross_vectors(r, d)
    M = Transformation()
    M[0, 0] = r[0]
    M[0, 1] = r[1]
    M[0, 2] = r[2]
    M[1, 0] = u[0]
    M[1, 1] = u[1]
    M[1, 2] = u[2]
    M[2, 0] = -d[0]
    M[2, 1] = -d[1]
    M[2, 2] = -d[2]
    M[0, 3] = -eye[0]
    M[1, 3] = -eye[1]
    M[2, 3] = -eye[2]
    return M


class View(QtWidgets.QOpenGLWidget):
    width = 800
    height = 500

    def __init__(self, data, parent=None):
        super().__init__(parent=parent)
        self.data = data
        self.keys = {'shift': False}

    def gl_info(self):
        info = """
            Vendor: {0}
            Renderer: {1}
            OpenGL Version: {2}
            Shader Version: {3}
            """.format(
            GL.glGetString(GL.GL_VENDOR),
            GL.glGetString(GL.GL_RENDERER),
            GL.glGetString(GL.GL_VERSION),
            GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION)
        )
        return info

    def aspect(self):
        return self.width / self.height

    def initializeGL(self):
        # print(self.gl_info())
        GL.glClearColor(0.9, 0.9, 0.9, 1)
        GL.glPolygonOffset(1.0, 1.0)
        GL.glEnable(GL.GL_POLYGON_OFFSET_FILL)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        # buffers
        self.vbo = {}
        # faces
        self.vbo['faces'] = {
            'vertices': self.data.faces,
            'colors': self.data.faces_colors
        }
        # edges
        self.vbo['edges'] = {
            'vertices': self.data.edges,
            'colors': self.data.edges_colors
        }
        # vertices
        self.vbo['vertices'] = {
            'vertices': self.data.vertices,
            'colors': self.data.vertices_colors
        }
        self.vao = {}
        # buffer configuration for faces
        self.vao['faces'] = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao['faces'])
        GL.glEnableVertexAttribArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo['faces']['vertices'])
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 0, None)
        GL.glEnableVertexAttribArray(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo['faces']['colors'])
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 0, None)
        GL.glBindVertexArray(0)
        # buffer configuration for edges
        self.vao['edges'] = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao['edges'])
        GL.glEnableVertexAttribArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo['edges']['vertices'])
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 0, None)
        GL.glEnableVertexAttribArray(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo['edges']['colors'])
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 0, None)
        GL.glBindVertexArray(0)
        # buffer configuration for vertices
        self.vao['vertices'] = GL.glGenVertexArrays(1)
        GL.glPointSize(10)
        GL.glBindVertexArray(self.vao['vertices'])
        GL.glEnableVertexAttribArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo['vertices']['vertices'])
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 0, None)
        GL.glEnableVertexAttribArray(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo['vertices']['colors'])
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 0, None)
        GL.glBindVertexArray(0)
        # program
        self.program = make_shader_program(VSHADER, FSHADER)
        # uniforms
        GL.glUseProgram(self.program)
        P = perspective(45, self.aspect(), 0.1, 100)
        V = lookat([0, 0, 5], [0, 0, 0], [0, 1, 0])
        # update
        Rx = Rotation.from_axis_and_angle([1, 0, 0], math.radians(-60))
        Rz = Rotation.from_axis_and_angle([0, 0, 1], math.radians(-30))
        M = Rx * Rz
        GL.glUniformMatrix4fv(GL.glGetUniformLocation(self.program, "P"), 1, True, np.asfortranarray(P, dtype=np.float32))
        GL.glUniformMatrix4fv(GL.glGetUniformLocation(self.program, "V"), 1, True, np.asfortranarray(V, dtype=np.float32))
        GL.glUniformMatrix4fv(GL.glGetUniformLocation(self.program, "M"), 1, True, np.asfortranarray(M, dtype=np.float32))
        GL.glUseProgram(0)

    def resizeGL(self, width: int, height: int):
        self.width = width
        self.height = height
        GL.glViewport(0, 0, width, height)
        # update perspective
        GL.glUseProgram(self.program)
        P = perspective(45, self.aspect(), 0.1, 100)
        GL.glUniformMatrix4fv(GL.glGetUniformLocation(self.program, "P"), 1, True, np.asfortranarray(P, dtype=np.float32))
        GL.glUseProgram(0)

    def paintGL(self):
        # clean up what was previously drawn
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        # activate the program
        GL.glUseProgram(self.program)
        # draw faces
        GL.glBindVertexArray(self.vao['faces'])
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, GL.GL_BUFFER_SIZE)
        # draw edges
        GL.glBindVertexArray(self.vao['edges'])
        GL.glDrawArrays(GL.GL_LINES, 0, GL.GL_BUFFER_SIZE)
        # draw points
        GL.glBindVertexArray(self.vao['vertices'])
        GL.glDrawArrays(GL.GL_POINTS, 0, GL.GL_BUFFER_SIZE)
        # finalize
        GL.glUseProgram(0)
        GL.glBindVertexArray(0)

    def mouseMoveEvent(self, event):
        if self.isActiveWindow() and self.underMouse():
            print(event.pos())
            if event.buttons() & QtCore.Qt.RightButton:
                if self.keys['shift']:
                    print('translate')
                else:
                    print('rotate')
            if event.buttons() & QtCore.Qt.MiddleButton:
                print('translate')

    def mousePressEvent(self, event):
        if self.isActiveWindow() and self.underMouse():
            print(event.pos())
            if event.buttons() & QtCore.Qt.LeftButton:
                print('left')
            elif event.buttons() & QtCore.Qt.RightButton:
                print('right')

    def mouseReleaseEvent(self, event):
        if self.isActiveWindow() and self.underMouse():
            print(None)

    def wheelEvent(self, event):
        if self.isActiveWindow() and self.underMouse():
            print('zoom')

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        key = event.key()
        if key == 16777248:
            self.keys['shift'] = True
            print('shift')

    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event)
        key = event.key()
        if key == 16777248:
            self.keys['shift'] = False
        print(None)


class Viewer(QtWidgets.QMainWindow):

    def __init__(self, app, data):
        super().__init__()
        # initialize the GL widget
        self.app = app
        self.view = View(data)
        # put the window in the middle of the screen
        self.setCentralWidget(self.view)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.setContentsMargins(0, 0, 0, 0)
        self.center()

    def center(self):
        self.resize(self.view.width, self.view.height)
        desktop = self.app.desktop()
        rect = desktop.availableGeometry()
        x = 0.5 * (rect.width() - self.view.width)
        y = 0.5 * (rect.height() - self.view.height)
        self.setGeometry(x, y, self.view.width, self.view.height)


class BoxObject:

    def __init__(self, box):
        self._box = None
        self._mesh = None
        self._vertices = None
        self._edges = None
        self._faces = None
        self._vertices_colors = None
        self._edges_colors = None
        self._faces_colors = None
        self.box = box

    @property
    def box(self):
        return self._box

    @box.setter
    def box(self, box):
        self._box = box
        self._mesh = Mesh.from_shape(box)
        self._vertices = None
        self._vertices_colors = None
        self._edges = None
        self._edges_colors = None
        self._faces = None
        self._faces_colors = None

    @property
    def mesh(self):
        return self._mesh

    @property
    def vertices(self):
        if not self._box:
            return
        mesh = self._mesh
        if not self._vertices:
            vertices = []
            for vertex in mesh.vertices():
                xyz = mesh.vertex_attributes(vertex, 'xyz')
                vertices.append(xyz)
            self._vertices = make_vertex_buffer(list(flatten(vertices)))
        return self._vertices

    @property
    def vertices_colors(self):
        if not self._box:
            return
        mesh = self._mesh
        if not self._vertices_colors:
            colors = []
            color = [0.1, 0.1, 0.1]
            for vertex in mesh.vertices():
                colors.append(color)
            self._vertices_colors = make_vertex_buffer(list(flatten(colors)))
        return self._vertices_colors

    @property
    def edges(self):
        if not self._box:
            return
        mesh = self._mesh
        if not self._edges:
            edges = []
            for edge in mesh.edges():
                a, b = mesh.vertices_attributes('xyz', keys=edge)
                edges.append(a)
                edges.append(b)
            self._edges = make_vertex_buffer(list(flatten(edges)))
        return self._edges

    @property
    def edges_colors(self):
        if not self._box:
            return
        mesh = self._mesh
        if not self._edges_colors:
            colors = []
            color = [0.2, 0.2, 0.2]
            for edge in mesh.edges():
                colors.append(color)
                colors.append(color)
            self._edges_colors = make_vertex_buffer(list(flatten(colors)))
        return self._edges_colors

    @property
    def faces(self):
        if not self._box:
            return
        mesh = self._mesh
        if not self._faces:
            faces = []
            vertex_xyz = {vertex: mesh.vertex_attributes(vertex, 'xyz') for vertex in mesh.vertices()}
            for face in mesh.faces():
                a, b, c, d = mesh.face_vertices(face)
                faces.append(vertex_xyz[a])
                faces.append(vertex_xyz[b])
                faces.append(vertex_xyz[c])
                faces.append(vertex_xyz[a])
                faces.append(vertex_xyz[c])
                faces.append(vertex_xyz[d])
            self._faces = make_vertex_buffer(list(flatten(faces)))
        return self._faces

    @property
    def faces_colors(self):
        if not self._box:
            return
        mesh = self._mesh
        if not self._faces_colors:
            colors = []
            color = [0.8, 0.8, 0.8]
            for face in mesh.faces():
                colors.append(color)
                colors.append(color)
                colors.append(color)
                colors.append(color)
                colors.append(color)
                colors.append(color)
            self._faces_colors = make_vertex_buffer(list(flatten(colors)))
        return self._faces_colors


if __name__ == '__main__':

    from dataclasses import dataclass

    from compas.datastructures import Mesh
    from compas.geometry import Box
    from compas.utilities import flatten

    box = Box.from_width_height_depth(1, 1, 1)
    boxobject = BoxObject(box)

    # Visualisation

    glFormat = QtGui.QSurfaceFormat()
    glFormat.setVersion(4, 1)
    glFormat.setProfile(QtGui.QSurfaceFormat.CoreProfile)
    glFormat.setDefaultFormat(glFormat)

    QtGui.QSurfaceFormat.setDefaultFormat(glFormat)

    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    app.references = set()

    viewer = Viewer(app, boxobject)
    app.references.add(viewer)

    viewer.show()
    app.exec_()
