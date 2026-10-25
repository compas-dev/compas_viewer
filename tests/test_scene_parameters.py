from compas.geometry import Point
from compas.geometry import Sphere
from compas_viewer.scene import ViewerSceneObject
from compas_viewer.scene import inspect_object_parameters
from compas_viewer.scene import modify_object_parameters
from compas_viewer.scene import object_parameter_values


class PartiallyExposed:
    def __init__(self, exposed, hidden=2):
        self.exposed = exposed
        self._hidden = hidden


class SerializedFallback:
    def __init__(self, value):
        self._value = value

    @property
    def __data__(self):
        return {"value": self._value}


class SceneObjectProperties:
    data = ViewerSceneObject.data
    parameters = ViewerSceneObject.parameters
    parameter_info = ViewerSceneObject.parameter_info

    def __init__(self, item):
        self.item = item


class RejectingParameter:
    def __init__(self, first=1, second=2):
        self.first = first
        self._second = second

    @property
    def second(self):
        return self._second

    @second.setter
    def second(self, value):
        if value < 0:
            raise ValueError("second must be nonnegative")
        self._second = value


def test_parameter_values_are_deduced_from_compas_signature_and_attributes():
    point = Point(1, 2, 3, name="A")

    parameters = object_parameter_values(point)

    assert parameters == {"x": 1.0, "y": 2.0, "z": 3.0, "name": "A"}


def test_parameter_info_includes_defaults_and_unavailable_values():
    parameters = inspect_object_parameters(PartiallyExposed(1))

    assert parameters["exposed"].required
    assert parameters["exposed"].available
    assert parameters["exposed"].value == 1
    assert parameters["hidden"].has_default
    assert parameters["hidden"].default == 2
    assert not parameters["hidden"].available


def test_parameter_values_fall_back_to_compas_data_mapping():
    assert object_parameter_values(SerializedFallback(42)) == {"value": 42}
    assert not inspect_object_parameters(SerializedFallback(42))["value"].writable


def test_scene_object_exposes_underlying_data_and_parameters():
    sphere = Sphere(2.5)
    sceneobject = SceneObjectProperties(sphere)

    assert sceneobject.data is sphere
    assert sceneobject.parameters["radius"] == 2.5
    assert sceneobject.parameter_info["frame"].available


def test_modify_object_parameters_assigns_public_constructor_parameters():
    point = Point(1, 2, 3)

    modify_object_parameters(point, {"x": 4.0, "z": 6.0})

    assert list(point) == [4.0, 2.0, 6.0]


def test_modify_object_parameters_rolls_back_after_rejected_value():
    obj = RejectingParameter()

    try:
        modify_object_parameters(obj, {"first": 3, "second": -1})
    except ValueError:
        pass

    assert obj.first == 1
    assert obj.second == 2
