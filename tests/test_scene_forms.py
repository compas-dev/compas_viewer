from unittest.mock import Mock

import pytest
from PySide6.QtWidgets import QPlainTextEdit

from compas.colors import Color
from compas.colors import ColorDict
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Capsule
from compas.geometry import Cone
from compas.geometry import Cylinder
from compas.geometry import PlanarSurface
from compas.geometry import Shape
from compas.geometry import Sphere
from compas.geometry import Torus
from compas.scene import GeometryObject
from compas.scene import MeshObject
from compas.scene import SceneObject
from compas.scene import ShapeObject
from compas.scene import SurfaceObject
from compas_viewer import forms
from compas_viewer.components.boundcomponent import BoundComponent
from compas_viewer.components.colorpicker import ColorPicker
from compas_viewer.components.numberedit import NumberEdit
from compas_viewer.components.objectsetting import ObjectSetting
from compas_viewer.components.objectsetting import _EditableAttributeBinding
from compas_viewer.forms import REMOVE_EDITABLE_ATTRIBUTE
from compas_viewer.forms import register_scene_attribute_contribution
from compas_viewer.forms import scene_editable_attributes


@pytest.fixture
def isolated_registry(monkeypatch):
    monkeypatch.setattr(forms, "_CONTRIBUTIONS", {})
    monkeypatch.setattr(forms, "_CONTRIBUTIONS_DISCOVERED", True)


def test_duplicate_exact_registration_is_rejected(isolated_registry):
    register_scene_attribute_contribution("Viewer", SceneObject, "base", {"show": None})

    with pytest.raises(ValueError, match="already registered"):
        register_scene_attribute_contribution("Viewer", SceneObject, "base", {"show": None})


def test_registration_snapshots_the_ordered_mapping(isolated_registry):
    attributes = {"first": None, "second": None}
    register_scene_attribute_contribution("Viewer", SceneObject, "snapshot", attributes)

    attributes.clear()
    attributes["replacement"] = None

    assert list(scene_editable_attributes("Viewer", SceneObject()))[-2:] == ["first", "second"]


def test_contributions_compose_general_to_specific_and_lexically(isolated_registry):
    register_scene_attribute_contribution("Viewer", SceneObject, "z", {"base_z": None})
    register_scene_attribute_contribution("Viewer", SceneObject, "a", {"base_a": None})
    register_scene_attribute_contribution("Viewer", GeometryObject, "geometry", {"specific": None})

    names = list(scene_editable_attributes("Viewer", GeometryObject()))

    assert names[-3:] == ["base_a", "base_z", "specific"]


def test_replacement_retains_position_and_removal_is_explicit(isolated_registry):
    def update(sceneobject: SceneObject, value: object) -> None:
        sceneobject.opacity = float(value)

    register_scene_attribute_contribution(
        "Viewer",
        SceneObject,
        "custom",
        {"name": REMOVE_EDITABLE_ATTRIBUTE, "opacity": update, "extra": None},
    )

    attributes = scene_editable_attributes("Viewer", SceneObject())

    assert list(attributes) == ["opacity", "extra"]
    assert attributes["opacity"] is update


def test_same_specificity_attribute_conflict_is_rejected(isolated_registry):
    register_scene_attribute_contribution("Viewer", SceneObject, "a", {"opacity": None})
    register_scene_attribute_contribution("Viewer", SceneObject, "b", {"opacity": REMOVE_EDITABLE_ATTRIBUTE})

    with pytest.raises(ValueError, match="Viewer/SceneObject/opacity: a and b"):
        scene_editable_attributes("Viewer", SceneObject())


def test_contexts_resolve_independently(isolated_registry):
    register_scene_attribute_contribution("Viewer", SceneObject, "visibility", {"name": REMOVE_EDITABLE_ATTRIBUTE})
    register_scene_attribute_contribution("Browser", SceneObject, "visibility", {"opacity": REMOVE_EDITABLE_ATTRIBUTE})

    assert list(scene_editable_attributes("Viewer", SceneObject())) == ["opacity"]
    assert list(scene_editable_attributes("Browser", SceneObject())) == ["name"]


def test_read_only_default_assignment_is_omitted_but_callback_is_retained(isolated_registry):
    class ReadOnlyObject(SceneObject):
        @property
        def status(self):
            return "fixed"

    sceneobject = ReadOnlyObject()
    register_scene_attribute_contribution("Viewer", ReadOnlyObject, "default", {"status": None})

    assert "status" not in scene_editable_attributes("Viewer", sceneobject)

    forms._CONTRIBUTIONS.clear()

    def update(owner: ReadOnlyObject, value: object) -> None:
        pass

    register_scene_attribute_contribution("Viewer", ReadOnlyObject, "callback", {"status": update})

    assert scene_editable_attributes("Viewer", sceneobject)["status"] is update


def test_object_setting_inferrs_supported_controls_and_omits_unsupported(isolated_registry, monkeypatch):
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    class InspectableObject(SceneObject):
        __editable_attributes__ = {"show": None, "color": None, "item": None}

    sceneobject = InspectableObject(name="Example")
    setting = ObjectSetting()
    monkeypatch.setattr(ObjectSetting, "viewer", Mock())

    setting.populate(sceneobject)

    assert [control.label.text() for control in setting.children] == ["Name", "Opacity", "Show", "Color"]
    assert setting.widget.findChild(QPlainTextEdit, "objectInfo") is None
    assert setting.details_button.text() == "Details"
    assert setting.details_button.isEnabled()
    assert app is not None


def test_object_details_dialog_snapshots_single_and_multiple_selection(isolated_registry, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from PySide6.QtWidgets import QDialog
    from PySide6.QtWidgets import QPlainTextEdit
    from PySide6.QtWidgets import QWidget

    app = QApplication.instance() or QApplication([])
    first = ShapeObject(item=Sphere(1.0), name="First", show=False)
    second = SceneObject(name="Second")
    window = QWidget()
    viewer = Mock()
    viewer.ui.window.widget = window
    viewer.state.selection.objects = (first,)
    monkeypatch.setattr(ObjectSetting, "viewer", viewer)
    captured = []

    def capture(dialog):
        assert dialog.parent() is window
        assert dialog.isModal()
        text = dialog.findChild(QPlainTextEdit, "objectDetailsText")
        assert text is not None
        captured.append(text.toPlainText())
        return 0

    monkeypatch.setattr(QDialog, "exec", capture)
    setting = ObjectSetting()
    setting.update()
    setting.details_button.click()

    assert "Name: First" in captured[0]
    assert "Type: Sphere" in captured[0]
    assert "Visible: False" in captured[0]
    assert "Parameters:" in captured[0]
    assert "radius: 1.0" in captured[0]

    viewer.state.selection.objects = (first, second)
    setting.update()
    setting.details_button.click()

    assert captured[1] == "2 objects selected\nTypes: Sphere, Unresolved\nNames:\n  First\n  Second"
    assert app is not None


def test_object_details_button_is_disabled_without_selection(monkeypatch):
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    viewer = Mock()
    viewer.state.selection.objects = ()
    monkeypatch.setattr(ObjectSetting, "viewer", viewer)
    setting = ObjectSetting()

    setting.update()

    assert not setting.details_button.isEnabled()
    assert setting.widget.findChild(QPlainTextEdit, "objectInfo") is None
    assert app is not None


def test_color_mutation_refreshes_appearance_data(monkeypatch):
    sceneobject = SceneObject()
    setting = ObjectSetting()
    viewer = Mock()
    viewer.scene.objects = []
    viewer.state.selection.objects = ()
    monkeypatch.setattr(ObjectSetting, "viewer", viewer)

    setting._refresh_object(sceneobject, "color")

    viewer.scene.render_object.assert_called_once_with(sceneobject)
    viewer.scene.render_object.return_value.update.assert_called_once_with(update_data=True)
    viewer.renderer.update.assert_called_once_with()
    viewer.ui.sidebar.sceneform.update.assert_not_called()


def test_name_mutation_refreshes_the_scene_tree_label_without_rebuilding_buffers(monkeypatch):
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    sceneobject = SceneObject(name="Original")
    viewer = Mock()
    monkeypatch.setattr(ObjectSetting, "viewer", viewer)
    setting = ObjectSetting()
    setting.populate(sceneobject)
    name_control = next(control for control in setting.children if control.label.text() == "Name")

    name_control.text_edit.setPlainText("Renamed")

    assert sceneobject.name == "Renamed"
    viewer.scene.render_object.assert_not_called()
    viewer.scene.render_object.return_value.update.assert_not_called()
    viewer.scene.render_object.return_value.refresh_data.assert_not_called()
    viewer.ui.sidebar.sceneform.update.assert_called_once_with(refresh=True)
    viewer.renderer.buffer_manager.update_object_data.assert_not_called()
    viewer.renderer.buffer_manager.update_object_settings.assert_not_called()
    viewer.renderer.rebuild_buffers.assert_not_called()
    viewer.renderer.update.assert_not_called()
    assert app is not None


def test_display_setting_updates_only_one_gpu_settings_record(monkeypatch):
    sceneobject = ShapeObject(item=Torus(2.0, 0.5), u=128, v=128, show_lines=True)
    setting = ObjectSetting()
    viewer = Mock()
    viewer.running = True
    render_object = viewer.scene.render_object.return_value
    monkeypatch.setattr(ObjectSetting, "viewer", viewer)

    setting._refresh_object(sceneobject, "show_lines")

    viewer.scene.render_object.assert_called_once_with(sceneobject)
    viewer.renderer.makeCurrent.assert_called_once_with()
    viewer.renderer.buffer_manager.update_object_settings.assert_called_once_with(render_object)
    viewer.renderer.doneCurrent.assert_called_once_with()
    viewer.renderer.update.assert_called_once_with()
    render_object.refresh_data.assert_not_called()
    render_object.update.assert_not_called()
    viewer.renderer.buffer_manager.update_object_data.assert_not_called()
    viewer.renderer.rebuild_buffers.assert_not_called()
    viewer.ui.sidebar.sceneform.update.assert_not_called()


def test_show_setting_also_refreshes_the_scene_tree(monkeypatch):
    sceneobject = ShapeObject(item=Sphere(1.0))
    setting = ObjectSetting()
    viewer = Mock()
    viewer.running = True
    monkeypatch.setattr(ObjectSetting, "viewer", viewer)

    setting._refresh_object(sceneobject, "show")

    viewer.ui.sidebar.sceneform.update.assert_called_once_with(refresh=True)


def test_display_setting_releases_context_when_gpu_update_fails(monkeypatch):
    sceneobject = ShapeObject(item=Sphere(1.0))
    setting = ObjectSetting()
    viewer = Mock()
    viewer.running = True
    viewer.renderer.buffer_manager.update_object_settings.side_effect = RuntimeError("GPU update failed")
    monkeypatch.setattr(ObjectSetting, "viewer", viewer)

    with pytest.raises(RuntimeError, match="GPU update failed"):
        setting._refresh_object(sceneobject, "show")

    viewer.renderer.makeCurrent.assert_called_once_with()
    viewer.renderer.doneCurrent.assert_called_once_with()
    viewer.renderer.update.assert_not_called()
    viewer.ui.sidebar.sceneform.update.assert_not_called()


def test_shape_line_controls_use_wireframe_labels_but_mesh_keeps_edges(monkeypatch):
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    setting = ObjectSetting()
    monkeypatch.setattr(ObjectSetting, "viewer", Mock())
    shape = ShapeObject(item=Sphere(1.0))
    mesh = MeshObject(item=Mesh.from_vertices_and_faces([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]]))

    shape_controls = [setting._create_control(_EditableAttributeBinding(shape, name, None)) for name in ("show_lines", "linecolor", "linewidth")]
    mesh_controls = [setting._create_control(_EditableAttributeBinding(mesh, name, None)) for name in ("show_edges", "edgecolor", "edgewidth")]
    shape_labels = [control.label.text() for control in shape_controls]
    mesh_labels = [control.label.text() for control in mesh_controls]

    assert shape_labels == ["Show wireframe", "Wireframe color", "Wireframe width"]
    assert mesh_labels == ["Show edges", "Edgecolor", "Edgewidth"]
    assert app is not None


def test_failed_sceneobject_setter_restores_control_and_does_not_refresh():
    class RejectingSceneObject(SceneObject):
        __editable_attributes__ = {"level": None}

        def __init__(self):
            super().__init__()
            self._level = 1.0

        @property
        def level(self):
            return self._level

        @level.setter
        def level(self, value):
            self._level = value
            if value < 0:
                raise ValueError("negative levels are rejected")

    binding = _EditableAttributeBinding(RejectingSceneObject(), "level", None)
    component = object.__new__(BoundComponent)
    component.obj = binding
    component.attr = "value"
    component.action = Mock()
    component.sync_from_bound_object = Mock()

    with pytest.raises(ValueError, match="negative levels"):
        component.on_value_changed(-1.0)

    assert binding.value == 1.0
    component.sync_from_bound_object.assert_called_once_with(1.0)
    component.action.assert_not_called()


def test_context_callback_is_used_for_mutation(isolated_registry):
    seen = []

    def update(sceneobject: SceneObject, value: object) -> None:
        seen.append((sceneobject, value))
        sceneobject.opacity = float(value)

    sceneobject = SceneObject()
    register_scene_attribute_contribution("Viewer", SceneObject, "opacity", {"opacity": update})
    binding = _EditableAttributeBinding(sceneobject, "opacity", scene_editable_attributes("Viewer", sceneobject)["opacity"])

    binding.value = 0.5

    assert seen == [(sceneobject, 0.5)]
    assert sceneobject.opacity == 0.5


def test_context_attribute_with_none_uses_ordinary_assignment(isolated_registry):
    sceneobject = SceneObject()
    sceneobject.level = 1
    register_scene_attribute_contribution("Viewer", SceneObject, "level", {"level": None})
    binding = _EditableAttributeBinding(sceneobject, "level", scene_editable_attributes("Viewer", sceneobject)["level"])

    binding.value = 2

    assert sceneobject.level == 2


def test_integer_attribute_preserves_type_and_serializes_after_edit(isolated_registry):
    def update_resolution(sceneobject: ShapeObject, value: object) -> None:
        if not isinstance(value, int):
            raise TypeError("Shape resolution should be an integer.")
        sceneobject.u = value

    sceneobject = ShapeObject(item=Sphere(1.0))
    register_scene_attribute_contribution("Viewer", ShapeObject, "resolution", {"u": update_resolution})
    binding = _EditableAttributeBinding(sceneobject, "u", scene_editable_attributes("Viewer", sceneobject)["u"])

    binding.value = 32.0

    assert sceneobject.u == 32
    assert type(sceneobject.u) is int
    restored = ShapeObject.__from_data__(sceneobject.__data__)
    assert restored.u == 32
    assert type(restored.u) is int


def test_fractional_scene_field_uses_fractional_editor_for_integer_initial_value(isolated_registry, monkeypatch):
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    mesh = Mesh.from_vertices_and_faces([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]])
    sceneobject = MeshObject(item=mesh, vertexsize=10)
    setting = ObjectSetting()
    viewer = Mock()
    monkeypatch.setattr(ObjectSetting, "viewer", viewer)
    binding = _EditableAttributeBinding(sceneobject, "vertexsize", None)

    control = setting._create_control(binding)

    assert isinstance(control, NumberEdit)
    assert control.spinbox.decimals() == 1
    assert control.spinbox.singleStep() == 0.1

    control.spinbox.setValue(10.5)

    assert sceneobject.vertexsize == 10.5
    assert type(sceneobject.vertexsize) is float
    viewer.scene.render_object.assert_called_once_with(sceneobject)
    assert app is not None


def test_integer_scene_field_uses_integer_editor_and_preserves_type(isolated_registry, monkeypatch):
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    def update_resolution(sceneobject: ShapeObject, value: object) -> None:
        if not isinstance(value, int):
            raise TypeError("Shape resolution should be an integer.")
        sceneobject.u = value

    sceneobject = ShapeObject(item=Sphere(1.0))
    register_scene_attribute_contribution("Viewer", ShapeObject, "resolution", {"u": update_resolution})
    setting = ObjectSetting()
    viewer = Mock()
    monkeypatch.setattr(ObjectSetting, "viewer", viewer)
    binding = _EditableAttributeBinding(sceneobject, "u", scene_editable_attributes("Viewer", sceneobject)["u"])

    control = setting._create_control(binding)

    assert isinstance(control, NumberEdit)
    assert control.spinbox.decimals() == 0
    assert control.spinbox.singleStep() == 1.0

    control.spinbox.stepUp()

    assert sceneobject.u == 17
    assert type(sceneobject.u) is int
    viewer.scene.render_object.assert_called_once_with(sceneobject)
    assert app is not None


@pytest.mark.parametrize(
    ("sceneobject", "resolution_labels"),
    [
        (ShapeObject(item=Box(1.0)), []),
        (ShapeObject(item=Cone(1.0, 2.0)), ["U Resolution"]),
        (ShapeObject(item=Cylinder(1.0, 2.0)), ["U Resolution"]),
        (ShapeObject(item=Sphere(1.0)), ["U Resolution", "V Resolution"]),
        (ShapeObject(item=Torus(2.0, 0.5)), ["U Resolution", "V Resolution"]),
        (ShapeObject(item=Capsule(1.0, 2.0)), ["U Resolution", "V Resolution"]),
        (ShapeObject(item=Mock(spec=Shape)), []),
        (SurfaceObject(item=PlanarSurface()), ["U Resolution", "V Resolution"]),
    ],
)
def test_resolution_controls_follow_represented_producer(isolated_registry, monkeypatch, sceneobject, resolution_labels):
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    setting = ObjectSetting()
    monkeypatch.setattr(ObjectSetting, "viewer", Mock())

    setting.populate(sceneobject)

    labels = [control.label.text() for control in setting.children]
    assert [label for label in labels if label.endswith("Resolution")] == resolution_labels
    assert app is not None


def test_keyboard_resolution_edit_rebuilds_render_data_and_sidebar_once(isolated_registry, monkeypatch):
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    sceneobject = ShapeObject(item=Torus(2.0, 0.5), u=16, v=16)
    selection = (sceneobject,)
    setting = ObjectSetting()
    viewer = Mock()
    viewer.state.selection.objects = selection
    monkeypatch.setattr(ObjectSetting, "viewer", viewer)
    setting.populate(sceneobject)
    u_control = next(control for control in setting.children if control.label.text() == "U Resolution")
    refresh_controls = Mock()
    monkeypatch.setattr(setting, "update", refresh_controls)

    u_control.spinbox.selectAll()
    QTest.keyClicks(u_control.spinbox, "64")
    assert sceneobject.u == 16
    QTest.keyClick(u_control.spinbox, Qt.Key.Key_Enter)

    assert sceneobject.u == 64
    assert viewer.state.selection.objects == selection
    render_object = viewer.scene.render_object.return_value
    render_object.refresh_data.assert_called_once_with()
    viewer.renderer.rebuild_buffers.assert_called_once_with()
    viewer.renderer.update.assert_called_once_with()
    viewer.ui.sidebar.sceneform.update.assert_called_once_with(refresh=True)
    refresh_controls.assert_not_called()
    assert u_control.spinbox.value() == 64
    assert app is not None


@pytest.mark.parametrize(
    ("sceneobject", "name", "invalid", "error"),
    [
        (ShapeObject(item=Sphere(1.0), u=6, v=4), "u", 2, ValueError),
        (ShapeObject(item=Sphere(1.0), u=6, v=4), "u", 6.5, ValueError),
        (ShapeObject(item=Sphere(1.0), u=6, v=4), "u", True, TypeError),
        (ShapeObject(item=Capsule(1.0, 2.0), u=6, v=4), "v", 5, ValueError),
        (SurfaceObject(item=PlanarSurface(), u=6, v=4), "v", 0, ValueError),
    ],
)
def test_invalid_resolution_edit_rolls_back_without_refresh(isolated_registry, sceneobject, name, invalid, error):
    previous = getattr(sceneobject, name)
    callback = scene_editable_attributes("Viewer", sceneobject)[name]
    binding = _EditableAttributeBinding(sceneobject, name, callback)
    component = object.__new__(BoundComponent)
    component.obj = binding
    component.attr = "value"
    component.action = Mock()
    component.sync_from_bound_object = Mock()

    with pytest.raises(error):
        component.on_value_changed(invalid)

    assert getattr(sceneobject, name) == previous
    component.sync_from_bound_object.assert_called_once_with(previous)
    component.action.assert_not_called()


def test_fractional_integer_edit_restores_control_without_refresh(isolated_registry):
    sceneobject = ShapeObject(item=Sphere(1.0))
    register_scene_attribute_contribution("Viewer", ShapeObject, "resolution", {"u": None})
    binding = _EditableAttributeBinding(sceneobject, "u", scene_editable_attributes("Viewer", sceneobject)["u"])
    component = object.__new__(BoundComponent)
    component.obj = binding
    component.attr = "value"
    component.action = Mock()
    component.sync_from_bound_object = Mock()

    with pytest.raises(ValueError, match="requires a whole number"):
        component.on_value_changed(16.5)

    assert sceneobject.u == 16
    component.sync_from_bound_object.assert_called_once_with(16)
    component.action.assert_not_called()


def test_registration_and_resolution_do_not_change_scene_json(isolated_registry):
    from compas import json_dumps

    sceneobject = SceneObject(name="Example")
    before = json_dumps(sceneobject.__data__)
    register_scene_attribute_contribution("Viewer", SceneObject, "context", {"show": None})

    scene_editable_attributes("Viewer", sceneobject)

    assert json_dumps(sceneobject.__data__) == before


def test_builtin_mesh_color_control_preserves_colordict_semantics(isolated_registry, monkeypatch):
    from PySide6.QtGui import QColor
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    mesh = Mesh.from_vertices_and_faces([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]])
    sceneobject = MeshObject(item=mesh)
    sceneobject.vertexcolor[0] = Color.blue()
    setting = ObjectSetting()
    viewer = Mock()
    viewer.scene.objects = []
    viewer.state.selection.objects = ()
    monkeypatch.setattr(ObjectSetting, "viewer", viewer)
    binding = _EditableAttributeBinding(sceneobject, "vertexcolor", None)
    control = setting._create_control(binding)

    assert isinstance(control, ColorPicker)
    control.change_color(QColor(0, 255, 0))

    assert isinstance(sceneobject.vertexcolor, ColorDict)
    assert sceneobject.vertexcolor.default == Color.green()
    assert dict(sceneobject.vertexcolor) == {}
    assert app is not None


def test_failed_colordict_callback_restores_mapping_and_control():
    class ColorObject(SceneObject):
        __editable_attributes__ = {"colors": None}

        def __init__(self):
            super().__init__()
            self.colors = ColorDict(Color.red())
            self.colors[0] = Color.blue()

    sceneobject = ColorObject()

    def reject(owner: SceneObject, value: object) -> None:
        colors = owner.colors
        colors.default = value
        colors.clear()
        raise ValueError("rejected")

    binding = _EditableAttributeBinding(sceneobject, "colors", reject)
    component = object.__new__(BoundComponent)
    component.obj = binding
    component.attr = "value"
    component.action = Mock()
    component.sync_from_bound_object = Mock()

    with pytest.raises(ValueError, match="rejected"):
        component.on_value_changed(Color.green())

    restored = binding.value
    assert isinstance(restored, ColorDict)
    assert restored.default == Color.red()
    assert restored[0] == Color.blue()
    component.sync_from_bound_object.assert_called_once()
    component.action.assert_not_called()
