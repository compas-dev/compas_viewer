import tkinter as tk
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from pyopengltk import OpenGLFrame

vertices = ((1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1), (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1))
edges = ((0, 1), (0, 3), (0, 4), (2, 1), (2, 3), (2, 7), (6, 3), (6, 4), (6, 7), (5, 1), (5, 4), (5, 7))
surfaces = ((0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4), (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6))
colors = ((1, 0, 0), (0, 1, 0), (1, 0.5, 0), (1, 1, 0), (1, 1, 1), (0, 0, 1))

rot_cube_map = {"Up": (-1, 0), "Down": (1, 0), "Left": (0, -1), "Right": (0, 1)}
rot_slice_map = {
    "1": (0, 0, 1),
    "2": (0, 1, 1),
    "3": (0, 2, 1),
    "4": (1, 0, 1),
    "5": (1, 1, 1),
    "6": (1, 2, 1),
    "7": (2, 0, 1),
    "8": (2, 1, 1),
    "9": (2, 2, 1),
    "F1": (0, 0, -1),
    "F2": (0, 1, -1),
    "F3": (0, 2, -1),
    "F4": (1, 0, -1),
    "F5": (1, 1, -1),
    "F6": (1, 2, -1),
    "F7": (2, 0, -1),
    "F8": (2, 1, -1),
    "F9": (2, 2, -1),
}


class Cube:
    def __init__(self, id, N, scale):
        self.N = 3
        self.scale = scale
        self.init_i = [*id]
        self.current_i = [*id]  # 表示填充，一个变量值代替多个
        self.rot = [[1 if i == j else 0 for i in range(3)] for j in range(3)]

    def isAffected(self, axis, slice, dir):
        return self.current_i[axis] == slice

    def update(self, axis, slice, dir):
        if not self.isAffected(axis, slice, dir):
            return

        i, j = (axis + 1) % 3, (axis + 2) % 3
        for k in range(3):
            self.rot[k][i], self.rot[k][j] = -self.rot[k][j] * dir, self.rot[k][i] * dir

        self.current_i[i], self.current_i[j] = (
            self.current_i[j] if dir < 0 else self.N - 1 - self.current_i[j],
            self.current_i[i] if dir > 0 else self.N - 1 - self.current_i[i],
        )

    def transformMat(self):
        scaleA = [[s * self.scale for s in a] for a in self.rot]
        scaleT = [(p - (self.N - 1) / 2) * 2.1 * self.scale for p in self.current_i]
        return [*scaleA[0], 0, *scaleA[1], 0, *scaleA[2], 0, *scaleT, 1]

    def draw(self, col, surf, vert, animate, angle, axis, slice, dir):
        glPushMatrix()
        if animate and self.isAffected(axis, slice, dir):
            glRotatef(angle * dir, *[1 if i == axis else 0 for i in range(3)])  # 围着这个坐标点旋转
        glMultMatrixf(self.transformMat())

        glBegin(GL_QUADS)
        for i in range(len(surf)):
            glColor3fv(colors[i])
            for j in surf[i]:
                glVertex3fv(vertices[j])
        glEnd()

        glPopMatrix()


class mycube:
    def __init__(self, N, scale):
        self.N = N
        cr = range(self.N)
        self.cubes = [Cube((x, y, z), self.N, scale) for x in cr for y in cr for z in cr]  # 创建27

    def maindd(self):
        for cube in self.cubes:
            cube.draw(colors, surfaces, vertices, False, 0, 0, 0, 0)


class GLFrame(OpenGLFrame):
    def initgl(self):
        self.animate = True
        self.rota = 0
        self.count = 0

        self.ang_x, self.ang_y, self.rot_cube = 0, 0, (0, 0)
        self.animate1Cube, self.animate_ang, self.animate_speed = False, 0, 2
        self.action = (0, 0, 0)
        glClearColor(0.0, 0.0, 0.0, 0.0)  # 背景黑色
        # glViewport(400, 400, 200, 200)  # 指定了视口的左下角位置

        glEnable(GL_DEPTH_TEST)  # 开启深度测试，实现遮挡关系
        glDepthFunc(GL_LEQUAL)  # 设置深度测试函数（GL_LEQUAL只是选项之一）

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()  # 恢复原始坐标
        gluPerspective(30, self.width / self.height, 0.1, 50.0)

        self.N = 3
        cr = range(self.N)
        self.cubes = [Cube((x, y, z), self.N, 1.5) for x in cr for y in cr for z in cr]

    def keydown(self, event):
        if event.keysym in rot_slice_map:
            self.animate1Cube, self.action = True, rot_slice_map[event.keysym]
        if event.keysym in rot_cube_map:
            self.rot_cube = rot_cube_map[event.keysym]

    def keyup(self, event):
        if event.keysym in rot_cube_map:
            self.rot_cube = (0, 0)

    def redraw(self):
        self.ang_x += self.rot_cube[0] * 2
        self.ang_y += self.rot_cube[1] * 2

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -40)
        glRotatef(self.ang_y, 0, 1, 0)
        glRotatef(self.ang_x, 1, 0, 0)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self.animate1Cube:
            if self.animate_ang >= 90:
                for cube in self.cubes:
                    cube.update(*self.action)
                self.animate1Cube, self.animate_ang = False, 0

        for cube in self.cubes:
            cube.draw(colors, surfaces, vertices, self.animate, self.animate_ang, *self.action)
        if self.animate1Cube:
            self.animate_ang += self.animate_speed


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("rubiks cube")
        self.glframe = GLFrame(self, width=800, height=600)
        # self.bind("<Key>", self.glframe.key)
        self.bind("<KeyPress>", self.glframe.keydown)
        self.bind("<KeyRelease>", self.glframe.keyup)
        self.glframe.pack(expand=True, fill=tk.BOTH)
        # self.glframe.focus_displayof()
        # self.animate = True


App().mainloop()
