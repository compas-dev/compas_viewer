from functools import partial
from typing import TYPE_CHECKING
from typing import Any
from typing import Optional

from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLayout
from PySide6.QtWidgets import QSpinBox
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas.colors import Color
from compas.geometry import Rotation
from compas.geometry import Scale
from compas.geometry import Transformation
from compas.geometry import Translation
from compas_viewer.scene.geometryobject import GeometryObject
from compas_viewer.scene.meshobject import MeshObject
from compas_viewer.scene.sceneobject import ViewerSceneObject

from .collapsiblebox import CollapsibleBox

if TYPE_CHECKING:
    from compas_viewer.viewer import Viewer


class Propertyform(QWidget):
    """
    Class for displaying basic properties of a scene object in a form.
    Propertyform is an abstract layout class that could be placed the sidedock.

    Parameters
    ----------
    obj : :class:`compas_viewer.scene.ViewerSceneObject`, optional
        The object to be displayed initially.
    on_select : bool, optional
        If ``True``, the form will be updated when the object is selected.
    title : str, optional
        The title of the form.
    stretch : int, optional
        The stretch factor of the form.

    See Also
    --------
    :class:`compas_viewer.layout.Treeform`

    References
    ----------
    :PySide6:`PySide6/QWidgets/QWidget`
    """

    def __init__(
        self,
        obj: Optional["ViewerSceneObject"] = None,
        on_select: bool = True,
        title: Optional[str] = None,
        stretch: int = 2,
    ):
        super().__init__()
        self.viewer: "Viewer"
        self.object = obj
        self.on_select = on_select
        self.title = title or "Property Form"
        self.stretch = stretch
        self.setLayout(QVBoxLayout())

        if self.object:
            self.set_object(self.object)

    # ==========================================================================
    # Set object
    # ==========================================================================

    def set_object(self, obj: "ViewerSceneObject"):
        """Set the object to be displayed in the form.

        Parameters
        ----------
        obj : :class:`compas_viewer.scene.ViewerSceneObject`
            The object to be displayed in the form.
        """

        self.clearLayout(self.layout())

        # Show object class
        self.add_label(obj.name, self.layout())
        self.add_label(str(self.object.__class__), self.layout())

        # Map object transform
        self.add_transformation(obj, self.layout())

        # Map object visualization
        self.add_visual_properties(obj, self.layout())

        self.layout().addStretch()  # type: ignore

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # ==========================================================================
    # Add sections
    # ==========================================================================

    def add_label(self, text: str, layout: QLayout) -> QLabel:
        """Add a label to the layout.

        Parameters
        ----------
        text : str
            Text of the label.
        layout : :PySide6:`PySide6/QtWidgets/QLayout`
            Layout to be added to.

        Returns
        -------
        label : :PySide6:`PySide6/QtWidgets/QLabel`
            The label added to the layout.

        """
        label = QLabel(str(text))
        layout.addWidget(label)
        return label

    def add_collapsiblebox(self, name: str, layout: QLayout) -> CollapsibleBox:
        """Add a collapsible box to the layout.

        Parameters
        ----------
        name : str
            Name of the collapsible box.
        layout : :PySide6:`PySide6/QtWidgets/QLayout`
            Layout to be added to.

        Returns
        -------
        :class:`compas_viewer.layout.CollapsibleBox`
            The collapsible box added to the layout.
        """
        cb = CollapsibleBox(name=name)
        layout.addWidget(cb)
        return cb

    def add_transformation(self, obj: "ViewerSceneObject", layout: QLayout):
        """Map the transformation of an object.

        Parameters
        ----------
        obj : :class:`compas_viewer.scene.ViewerSceneObject`
            The object to be edited.
        layout : :PySide6:`PySide6/QtWidgets/QLayout`
            Layout to be added to.

        Returns
        -------
        :class:`compas_viewer.layout.CollapsibleBox`
            The collapsible box added to the layout.
        """

        def set_transformation(value: float, label: str, index: int):
            if obj.transformation is None:
                obj.transformation = Transformation()
            s, _, r, t, _ = obj.transformation.decomposed()
            if label == "Translation":
                _vectors = t.translation_vector
                _vectors[index] = value
                t = Translation.from_vector(_vectors)
            elif label == "Scale":
                _scales = [s[0, 0], s[1, 1], s[2, 2]]
                _scales[index] = value
                s = Scale.from_factors(_scales)
            elif label == "Rotation":
                _angles = r.euler_angles()
                _angles[index] = value
                r = Rotation.from_euler_angles(_angles)
            obj.transformation = t * r * s
            obj.update()

        def get_transformation(label: str, index: int) -> float:  # type: ignore
            if obj.transformation is None:
                obj.transformation = Transformation()
            s, _, r, t, _ = obj.transformation.decomposed()
            if label == "Translation":
                return t.translation_vector[index]  # type: ignore
            elif label == "Scale":
                return s[index, index]
            elif label == "Rotation":
                return r.euler_angles()[index]

        collapsibleBox = self.add_collapsiblebox("Transformation", layout)

        for label in ["Translation", "Scale", "Rotation"]:
            collapsibleBox.content_area.layout().addWidget(QLabel(label))
            _layout = QHBoxLayout()
            for i, name in enumerate(["x", "y", "z"]):
                _label = QLabel(name)
                _input = QDoubleSpinBox()
                _input.setSingleStep(0.1)
                _input.setMinimum(-1000)
                _input.setMaximum(1000)
                _input.setValue(get_transformation(label, i))
                _input.valueChanged.connect(partial(set_transformation, label=label, index=i))
                _layout.addWidget(_label)
                _layout.addWidget(_input)
            collapsibleBox.content_area.layout().addLayout(_layout)  # type: ignore

        layout.addWidget(collapsibleBox)
        collapsibleBox.update()
        return collapsibleBox

    def add_visual_properties(self, obj: "ViewerSceneObject", layout: QLayout):
        """Map the visual properties of an object.

        Parameters
        ----------
        obj : :class:`compas_viewer.scene.ViewerSceneObject`
            The object to be edited.
        layout : :PySide6:`PySide6/QtWidgets/QLayout`
            Layout to be added to.

        Returns
        -------
        collapsibleBox : :class:`compas_viewer.layout.CollapsibleBox`
            The collapsible box added to the layout.
        """

        def get_color(label: str, index: int) -> int:  # type: ignore
            if isinstance(obj, GeometryObject):
                if label == "Point":
                    return obj.pointcolor.rgb255[index]
                elif label == "Line":
                    return obj.linecolor.rgb255[index]
                elif label == "Face":
                    return obj.surfacecolor.rgb255[index]
            elif isinstance(obj, MeshObject):
                if label == "Point":
                    return obj.vertexcolor.default.rgb255[index]  # type: ignore
                elif label == "Line":
                    return obj.edgecolor.default.rgb255[index]  # type: ignore
                elif label == "Face":
                    return obj.facecolor.default.rgb255[index]  # type: ignore
            else:
                raise NotImplementedError

        def set_color(value: float, label: str, index: int):
            if isinstance(obj, GeometryObject):
                if label == "Point":
                    color = list(obj.pointcolor.rgb255)
                    color[index] = value  # type: ignore
                    obj.pointcolor = Color.from_rgb255(*color)
                    obj._points_data = obj._read_points_data()
                elif label == "Line":
                    color = list(obj.linecolor.rgb255)
                    color[index] = value  # type: ignore
                    obj.linecolor = Color.from_rgb255(*color)
                    obj._lines_data = obj._read_lines_data()
                elif label == "Face":
                    color = list(obj.surfacecolor.rgb255)
                    color[index] = value  # type: ignore
                    obj.surfacecolor = Color.from_rgb255(*color)
                    obj._frontfaces_data = obj._read_frontfaces_data()
                    obj._backfaces_data = obj._read_backfaces_data()
            elif isinstance(obj, MeshObject):
                if label == "Point":
                    color = list(obj.vertexcolor.default.rgb255)  # type: ignore
                    color[index] = value
                    obj.vertexcolor.default = Color.from_rgb255(*color)  # type: ignore
                    obj._points_data = obj._read_points_data()
                elif label == "Line":
                    color = list(obj.edgecolor.default.rgb255)  # type: ignore
                    color[index] = value
                    obj.edgecolor.default = Color.from_rgb255(*color)  # type: ignore
                    obj._lines_data = obj._read_lines_data()
                elif label == "Face":
                    color = list(obj.facecolor.default.rgb255)  # type: ignore
                    color[index] = value
                    obj.facecolor.default = Color.from_rgb255(*color)  # type: ignore
                    obj._frontfaces_data = obj._read_frontfaces_data()
                    obj._backfaces_data = obj._read_backfaces_data()
            obj.update(update_positions=False, update_elements=False)

        collapsibleBox = self.add_collapsiblebox("Visualization", layout)

        for label in ["Point", "Line", "Face"]:
            _layout = QHBoxLayout()
            _layout.addWidget(QLabel(label))
            self.map_bool(obj, f"show_{label.lower()}s", _layout)
            collapsibleBox.content_area.layout().addLayout(_layout)  # type: ignore
            _layout = QHBoxLayout()
            for i, name in enumerate(["R", "G", "B"]):
                _label = QLabel(name)
                _input = QSpinBox()
                _input.setSingleStep(1)
                _input.setMinimum(0)
                _input.setMaximum(255)
                _input.setValue(int(get_color(label, i)))
                _input.valueChanged.connect(partial(set_color, label=label, index=i))
                _layout.addWidget(_label)
                _layout.addWidget(_input)
            collapsibleBox.content_area.layout().addLayout(_layout)  # type: ignore

        self.map_number(
            obj,
            "opacity",
            collapsibleBox.content_area.layout(),  # type: ignore
            "Opacity",
            minimum=0,
            maximum=1,
            step=0.1,
        )

        self.map_number(
            obj,
            "pointsize",
            collapsibleBox.content_area.layout(),  # type: ignore
            "Point Size",
            minimum=1,
            maximum=20,
            step=1,
        )

        self.map_number(
            obj,
            "linewidth",
            collapsibleBox.content_area.layout(),  # type: ignore
            "Line Width",
            minimum=1,
            maximum=20,
            step=1,
        )

        for name in ["is_selected", "is_locked", "is_visible"]:
            self.map_bool(obj, name, collapsibleBox.content_area.layout())

        layout.addWidget(collapsibleBox)
        collapsibleBox.update()

        return collapsibleBox

    # ==========================================================================
    # Add elements
    # ==========================================================================

    def map_bool(self, obj: Any, attribute: str, layout, name=None) -> QLayout:
        """Map color input field to an object attribute"""

        value = getattr(obj, attribute)
        _input = QCheckBox(name or str(attribute))
        _input.setChecked(value)
        layout.addWidget(_input)

        def set_bool(value):
            setattr(obj, attribute, bool(value))
            obj.update()

        _input.stateChanged.connect(set_bool)

        return layout

    def map_number(
        self,
        obj: Any,
        attribute: str,
        layout: QHBoxLayout,
        name: Optional[str] = None,
        minimum: int = -(10**9),
        maximum: int = 10**9,
        step=None,
    ) -> QLayout:
        """Map number input field to an object's attribute.

        Parameters
        ----------
        obj : Any
            Object to be edited.
        attribute : str
            Attribute to be edited.
        layout : QLayout
            Layout to be added to.
        name : str, optional
            Name of the attribute.
        minimum : int, optional
            Minimum value of the input field.
        maximum : int, optional
            Maximum value of the input field.
        step : int, optional
            Step of the input field.
        """

        label = QLabel(name or attribute)
        value: int = getattr(obj, attribute, 0)

        if isinstance(value, float):
            _input = QDoubleSpinBox()
            _input.setSingleStep(0.1)
        elif isinstance(value, int):
            _input = QSpinBox()

        _input.setMinimum(minimum)
        _input.setMaximum(maximum)

        if step:
            _input.setSingleStep(step)

        _input.setValue(value)
        layout.addWidget(label)
        layout.addWidget(_input)

        def set_number(value):
            setattr(obj, attribute, value)

        _input.valueChanged.connect(set_number)

        return layout

    def update(self):
        """Update the form."""
        if self.on_select:
            for obj in self.viewer.scene.objects:
                if obj.is_selected:
                    self.object = obj
                    break

        if self.object:
            self.set_object(self.object)
