from typing import TYPE_CHECKING
from typing import Any
from typing import Optional

from numpy import ndarray
from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLayout
from PySide6.QtWidgets import QSpinBox
from PySide6.QtWidgets import QVBoxLayout

from .collapsiblebox import CollapsibleBox

if TYPE_CHECKING:
    from compas_viewer.scene.sceneobject import ViewerSceneObject


class Propertyform(QVBoxLayout):
    """
    Class for displaying tree-like data.
    Treeform is an abstract class that could be placed in either the viewport or the sidedock.

    Parameters
    ----------
    tree : :class:`compas.datastructures.Tree`
        The tree to be displayed. An typical example is the scene
        object tree: :attr:`compas_viewer.viewer.Viewer._tree`.
    columns : dict
        A dictionary of column names and their corresponding attributes.
        Example: `` {"Name": "object.name", "Object": "object"}``
    column_editable : list, optional
        A list of booleans indicating whether the corresponding column is editable.
        Defaults to ``[False]``.
    show_headers : bool, optional
        Show the header of the tree.
        Defaults to ``True``.
    stretch : int, optional
        Stretch factor of the tree in the grid layout.
        Defaults to ``2``.

    Attributes
    ----------
    tree : :class:`compas.datastructures.Tree`
        The tree to be displayed.

    See Also
    --------
    :class:`compas.datastructures.Tree`
    :class:`compas.datastructures.tree.TreeNode`
    :class:`compas_viewer.layout.SidedockLayout`

    References
    ----------
    :PySide6:`PySide6/QtWidgets/QTreeWidget`

    Examples
    --------
    .. code-block:: python

        from compas_viewer import Viewer

        viewer = Viewer()

        for i in range(10):
            for j in range(10):
                sp = viewer.scene.add(Sphere(0.1, Frame([i, j, 0], [1, 0, 0], [0, 1, 0])), name=f"Sphere_{i}_{j}")

        viewer.layout.sidedock.add_element(Treeform(viewer._tree, {"Name":".object.name", "Object":".object"}))

        viewer.show()

    """

    def __init__(
        self,
        obj: "ViewerSceneObject",
        on_select: bool = False,
        title: Optional[str] = None,
        stretch: int = 2,
    ):
        super().__init__()
        self.object = obj
        self.on_select = on_select
        self.title = title or self.object.name
        self._stretch = stretch
        self.set_object(self.object)

    def set_object(self, obj: "ViewerSceneObject"):
        # Show object class
        self.add_label(self.object.name, self)
        self.add_label(str(self.object.__class__), self)

        # Map object transform
        self.map_transform(obj)

    def add_label(self, text: str, layout: QLayout):
        label = QLabel(str(text))
        layout.addWidget(label)

    def map_transform(self, obj: "ViewerSceneObject"):
        """Map the transformation of an object"""
        cb = self.add_collapsiblebox("Transform")
        v_layout = QVBoxLayout()

        self.add_label("translation", layout=v_layout)
        layout = QHBoxLayout()
        v_layout.addLayout(layout)
        self.map_number(obj.worldtransformation.translation[0, 3], "", name="x", layout=layout)
        self.map_number(obj.worldtransformation.translation[0,1], "1", name="y", layout=layout)
        self.map_number(obj.worldtransformation.translation[0,3], "2", name="z", layout=layout)

        self.add_label("rotation", layout=v_layout)
        layout = QHBoxLayout()
        v_layout.addLayout(layout)
        self.map_number(obj.worldtransformation.rotation, "0", name="x", layout=layout)
        self.map_number(obj.worldtransformation.rotation, "1", name="y", layout=layout)
        self.map_number(obj.worldtransformation.rotation, "2", name="z", layout=layout)

        self.add_label("scale", layout=v_layout)
        layout = QHBoxLayout()
        v_layout.addLayout(layout)
        self.map_number(obj.worldtransformation.scale, "0", name="x", layout=layout)
        self.map_number(obj.worldtransformation.scale, "1", name="y", layout=layout)
        self.map_number(obj.worldtransformation.scale, "2", name="z", layout=layout)

        cb.setContentLayout(v_layout)

    def add_collapsiblebox(self, name:str):
        cb = CollapsibleBox()
        self.addWidget(cb)
        return cb

    def map_number(
        self,
        obj: Any,
        attribute: str,
        name: Optional[str] = None,
        layout: Optional[QLayout] = None,
        update_data: bool = True,
        minimum: int = -(10**9),
        maximum: int = 10**9,
        step=None,
    ):
        """Map number input field to an object's attribute.

        Parameters
        ----------
        obj : Any
            Object to be edited.
        attribute : str
            Attribute to be edited.
        """
        if not layout:
            layout = QHBoxLayout()
            self.addLayout(layout)

        label = QLabel(name or str(attribute))
        if type(obj) in [list, dict, ndarray]:
            value = obj[attribute]
        else:
            value = getattr(obj, attribute)
        if isinstance(value, float):
            _input = QDoubleSpinBox()
            _input.setSingleStep(0.1)
            _input.setMinimum(minimum)
            _input.setMaximum(maximum)
        elif isinstance(value, int):
            _input = QSpinBox()
            _input.setMinimum(minimum)
            _input.setMaximum(maximum)
        else:
            raise ValueError("Unsupported type.")
        if step:
            _input.setSingleStep(step)
        _input.setValue(int(value))
        layout.addWidget(label)
        layout.addWidget(_input)

        def set_number(value):
            if type(obj) in [list, dict, ndarray]:
                obj[attribute] = value
            else:
                setattr(obj, attribute, value)
            self.update(update_data)

        _input.valueChanged.connect(set_number)
        return layout

    def update(self, update_data: bool = True):
        if self.on_select:
            for obj in self.object.scene.objects:
                if obj.is_selected:
                    self.object = obj
                    break

        self.object._update_matrix()

        if update_data:
            if hasattr(self, "data"):
                try:
                    self.object.item.data = self.data
                except Exception as e:
                    print(e)
                    print("Failed to update data of", self.obj)

            self.object.update()
