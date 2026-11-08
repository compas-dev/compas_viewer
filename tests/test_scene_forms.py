from unittest.mock import Mock

import pytest

from compas.colors import Color
from compas.colors import ColorDict
from compas.datastructures import Mesh
from compas.geometry import Sphere
from compas.scene import GeometryObject
from compas.scene import MeshObject
from compas.scene import SceneObject
from compas.scene import ShapeObject
from compas_viewer import forms
from compas_viewer.components.boundcomponent import BoundComponent
from compas_viewer.components.colorpicker import ColorPicker
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
    assert app is not None


def test_successful_mutation_conservatively_refreshes_viewer(monkeypatch):
    sceneobject = SceneObject()
    setting = ObjectSetting()
    viewer = Mock()
    viewer.scene.objects = []
    monkeypatch.setattr(ObjectSetting, "viewer", viewer)

    setting._refresh_object(sceneobject)

    viewer.scene.render_object.assert_called_once_with(sceneobject)
    viewer.scene.render_object.return_value.update.assert_called_once_with(update_data=True)
    viewer.renderer.update.assert_called_once_with()
    viewer.ui.sidebar.sceneform.update.assert_called_once_with(refresh=True)


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
