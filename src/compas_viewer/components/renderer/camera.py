from math import atan2
from math import radians
from math import tan
from typing import TYPE_CHECKING
from typing import Callable
from typing import Optional

from numpy import array
from numpy import asfortranarray
from numpy import dot
from numpy import float32
from numpy import pi
from numpy.linalg import det
from numpy.linalg import norm

from compas.geometry import Rotation
from compas.geometry import Transformation
from compas.geometry import Translation
from compas.geometry import Vector

if TYPE_CHECKING:
    # https://peps.python.org/pep-0484/#runtime-or-type-checking
    pass


class Position(Vector):
    """
    The position of the camera.

    Parameters
    ----------
    vector : tuple[float, float, float]
        The position of the camera.
    on_update : Callable
        A callback function that is called when the position changes.

    """

    def __init__(self, vector: tuple[float, float, float], on_update: Optional[Callable] = None):
        self.on_update = on_update
        self.pause_update = True
        super().__init__(*vector)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        if self.on_update is not None and not self.pause_update:
            self.on_update([x, self.y, self.z])
        self._x = float(x)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        if self.on_update is not None and not self.pause_update:
            self.on_update([self.x, y, self.z])
        self._y = float(y)

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, z):
        if self.on_update is not None and not self.pause_update:
            self.on_update([self.x, self.y, z])
        self._z = float(z)

    def set(self, x: float, y: float, z: float, pause_update: bool = False):
        """Set the position of the camera."""
        pause_update = pause_update or self.pause_update
        if self.on_update is not None and not pause_update:
            self.on_update([x, y, z])
        self._x = x
        self._y = y
        self._z = z


class RotationEuler(Position):
    pass


class Camera:
    """Camera object for the default view.

    Parameters
    ----------
    renderer : :class:`compas_viewer.components.renderer.Renderer`,
        The parent renderer of the camera.

    Attributes
    ----------
    config : :class:`compas_viewer.configurations.render_config.CameraConfig`

    Notes
    -----
    The camera is defined by the following parameters which can be found in:
    :class:`compas_viewer.configurations.render_config.CameraConfig`:

    fov : float
        The field of view as an angler in degrees.
    near : float
        The location of the "near" clipping plane.
    far : float
        The location of the "far" clipping plane.
    position : :class:`compas_viewer.components.renderer.camera.Position`
        The location the camera.
    rotation : :class:`compas_viewer.components.renderer.camera.RotationEuler`
        The euler rotation of camera.
    target : :class:`compas_viewer.components.renderer.camera.Position`
        The viewing target.
        Default is the origin of the world coordinate system.
    distance : float
        The distance from the camera standpoint to the target.
    zoomdelta : float
        Size of one zoom increment.
    rotationdelta : float
        Size of one rotation increment.
    pan_delta : float
        Size of one pan increment.
    scale : float
        The scale factor for camera's near, far and pan_delta.
    """

    def __init__(
        self,
        fov: Optional[float] = 45.0,
        near: Optional[float] = 0.1,
        far: Optional[float] = 1000.0,
        init_position: Optional[tuple] = [10.0, 10.0, 10.0],
        init_target: Optional[tuple] = [0.0, 0.0, 0.0],
        scale: Optional[float] = 1.0,
        zoomdelta: Optional[float] = 0.05,
        rotationdelta: Optional[float] = 0.01,
        pan_delta: Optional[float] = 0.05,
    ) -> None:
        self.fov = fov
        self.near = near
        self.far = far
        self.scale = scale
        self.zoomdelta = zoomdelta
        self.rotationdelta = rotationdelta
        self.pan_delta = pan_delta

        self._position = Position(init_position, on_update=self._on_position_update)
        self._rotation = RotationEuler((0, 0, 0), on_update=self._on_rotation_update)
        self._target = Position(init_target, on_update=self._on_target_update)
        self._position.pause_update = False
        self._rotation.pause_update = False
        self._target.pause_update = False
        self.target = Position(init_target)

    def lazy_init(self) -> None:
        # Camera position only modifiable in perspective view mode.
        self.reset_position()
        # if self.renderer.config.viewmode == "perspective":
        #     self.position = Position(self.config.position)

    @property
    def viewer(self):
        from compas_viewer.viewer import Viewer

        return Viewer()

    @property
    def position(self) -> Position:
        """The position of the camera."""
        return self._position

    @position.setter
    def position(self, position: Position):
        self._position.set(*position, pause_update=False)

    @property
    def rotation(self) -> RotationEuler:
        """The rotation of the camera."""
        return self._rotation

    @rotation.setter
    def rotation(self, rotation: RotationEuler):
        self._rotation.set(rotation.x, rotation.y, rotation.z)

    @property
    def target(self) -> Position:
        """The target of the camera."""
        return self._target

    @target.setter
    def target(self, target: Position):
        self._target.set(*target, pause_update=False)

    @property
    def distance(self) -> float:
        """The distance from the camera to the target."""
        return (self.position - self.target).length

    @distance.setter
    def distance(self, distance: float):
        """Update the position based on the distance."""
        direction = self.position - self.target
        direction.unitize()
        new_position = self.target + direction * distance
        self.position.set(*new_position, pause_update=True)

    def ortho(self, left: float, right: float, bottom: float, top: float, near: float, far: float) -> Transformation:
        """Construct an orthogonal projection matrix.

        Parameters
        ----------
        left : float
            Location of the left clipping plane.
        right : float
            Location of the right clipping plane.
        bottom : float
            Location of the bottom clipping plane.
        top : float
            Location of the top clipping plane.
        near : float
            Location of the near clipping plane.
        far : float
            Location of the far clipping plane.

        Returns
        -------
        :class:`compas.geometry.Transformation`

        """
        dx = right - left
        dy = top - bottom
        dz = far - near
        rx = -(right + left) / dx
        ry = -(top + bottom) / dy
        rz = -(far + near) / dz
        assert dx != 0 and dy != 0 and dz != 0
        matrix = [
            [2.0 / dx, 0, 0, rx],
            [0, 2.0 / dy, 0, ry],
            [0, 0, -2.0 / dz, rz],
            [0, 0, 0, 1],
        ]
        return Transformation.from_matrix(matrix)

    def perspective(self, fov: float, aspect: float, near: float, far: float) -> Transformation:
        """Construct a perspective projection matrix.

        Parameters
        ----------
        fov : float
            The field of view in degrees.
        aspect : float
            The aspect ratio of the view.
        near : float
            Location of the near clipping plane.
        far : float
            Location of the far clipping plane.

        Returns
        -------
        :class:`compas.geometry.Transformation`

        """
        assert near != far
        assert aspect != 0
        assert fov != 0

        sy = 1.0 / tan(radians(fov) / 2.0)
        sx = sy / aspect
        zz = (far + near) / (near - far)
        zw = 2 * far * near / (near - far)
        matrix = [[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, zz, zw], [0, 0, -1, 0]]
        return Transformation.from_matrix(matrix)

    def _on_position_update(self, new_position: Position):
        """Update camera rotation to keep pointing the target."""
        old_direction = array(self.position - self.target)
        new_direction = array(Vector(*new_position) - self.target)
        old_distance = norm(old_direction)
        new_distance = norm(new_direction)
        self.distance *= float(new_distance) / float(old_distance)

        old_direction_xy = old_direction[:2]
        new_direction_xy = new_direction[:2]
        old_direction_xy_distance = norm(old_direction_xy)
        new_direction_xy_distance = norm(new_direction_xy)

        old_direction_pitch = array([old_direction_xy_distance, old_direction[2]])
        new_direction_pitch = array([new_direction_xy_distance, new_direction[2]])
        old_direction_pitch_distance = norm(old_direction_pitch)
        new_direction_pitch_distance = norm(new_direction_pitch)

        if new_direction_xy[0] == 0 and new_direction_xy[1] == 0:
            new_direction_xy[0] = 0.0001

        old_direction_xy /= old_direction_xy_distance or 1
        new_direction_xy /= new_direction_xy_distance or 1
        old_direction_pitch /= old_direction_pitch_distance
        new_direction_pitch /= new_direction_pitch_distance

        angle_z = atan2(det([old_direction_xy, new_direction_xy]), dot(old_direction_xy, new_direction_xy))
        angle_x = -atan2(det([old_direction_pitch, new_direction_pitch]), dot(old_direction_pitch, new_direction_pitch))

        new_rotation = self.rotation + [angle_x or 0, 0, angle_z or 0]
        self.rotation.set(*new_rotation, pause_update=True)

    def _on_rotation_update(self, rotation):
        """Update camera position when rotation around target."""
        R = Rotation.from_euler_angles(rotation)
        T = Translation.from_vector([0, 0, self.distance])
        M = (R * T).matrix
        vector = [M[i][3] for i in range(3)]
        position = self.target + vector

        self.position.set(*position, pause_update=True)

    def _on_target_update(self, target: Position):
        """Update camera position when target changes."""
        R = Rotation.from_euler_angles(self.rotation)
        T = Translation.from_vector([0, 0, self.distance])
        M = (R * T).matrix
        vector = [M[i][3] for i in range(3)]
        position = Vector(*target) + Vector(*vector)

        self.target.set(*target, pause_update=True)
        self.position.set(*position, pause_update=True)

    def reset_position(self):
        """Reset the position of the camera based current view type."""
        self.target.set(0, 0, 0, False)
        if self.viewer.renderer.viewmode == "perspective":
            self.rotation.set(pi / 4, 0, -pi / 4, False)
        if self.viewer.renderer.viewmode == "top":
            self.rotation.set(0, 0, 0, False)
        if self.viewer.renderer.viewmode == "front":
            self.rotation.set(pi / 2, 0, 0, False)
        if self.viewer.renderer.viewmode == "right":
            self.rotation.set(pi / 2, 0, pi / 2, False)

    def rotate(self, dx: float, dy: float):
        """Rotate the camera based on current mouse movement.

        Parameters
        ----------
        dx : float
            Number of rotation increments around the Z axis, with each increment the size
            of :attr:`Camera.rotationdelta`.
        dy : float
            Number of rotation increments around the X axis, with each increment the size
            of :attr:`Camera.rotationdelta`.

        Notes
        -----
        Camera rotations are only available if the current view mode
        is a perspective view (``camera.renderer.config.viewmode == "perspective"``).

        """
        if self.viewer.renderer.config.viewmode == "perspective":
            self.rotation += [-self.rotationdelta * dy, 0, -self.rotationdelta * dx]

    def pan(self, dx: float, dy: float):
        """Pan the camera based on current mouse movement.

        Parameters
        ----------
        dx : float
            Number of "pan" increments in the "X" direction of the current view,
            with each increment the size of :attr:`Camera.pan_delta`.
        dy : float
            Number of "pan" increments in the "Y" direction of the current view,
            with each increment the size of :attr:`Camera.pan_delta`.
        """
        R = Rotation.from_euler_angles(self.rotation)
        T = Translation.from_vector([-dx * self.pan_delta * self.scale, dy * self.pan_delta * self.scale, 0])
        M = (R * T).matrix
        vector = [M[i][3] for i in range(3)]
        self.target += vector

    def zoom(self, steps: float = 1):
        """Zoom in or out.

        Parameters
        ----------
        steps : float
            The number of zoom increments, with each increment the size
            of :attr:`compas_viewer.components.renderer.Camera.config.zoomdelta`.

        """
        self.distance -= steps * self.zoomdelta * self.distance

    def projection(self, width: int, height: int) -> list[list[float]]:
        """Compute the projection matrix corresponding to the current camera settings.

        Parameters
        ----------
        width : int
            Width of the viewer.
        height : int
            Height of the viewer.

        Returns
        -------
        list[list[float]]
            The transformation matrix as a `numpy` array in column-major order.

        Notes
        -----
        The projection matrix transforms the scene from camera coordinates to screen coordinates.

        """
        aspect = width / height
        if self.viewer.renderer.viewmode == "perspective":
            P = self.perspective(self.fov, aspect, self.near * self.scale, self.far * self.scale)
        else:
            left = -self.distance
            right = self.distance
            bottom = -self.distance / aspect
            top = self.distance / aspect
            P = self.ortho(left, right, bottom, top, self.near * self.scale, self.far * self.scale)
        return list(asfortranarray(P, dtype=float32))

    def viewworld(self) -> list[list[float]]:
        """Compute the view-world matrix corresponding to the current camera settings.

        Returns
        -------
        list[list[float]]
            The transformation matrix in column-major order.

        Notes
        -----
        The view-world matrix transforms the scene from world coordinates to camera coordinates.

        """
        T = Translation.from_vector(self.position)
        R = Rotation.from_euler_angles(self.rotation)
        W = T * R
        return list(asfortranarray(W.inverted(), dtype=float32))
