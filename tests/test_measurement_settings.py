from types import SimpleNamespace

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QLabel

from compas.tolerance import TOL
from compas_viewer.base import Base
from compas_viewer.components.measurementsetting import MeasurementSetting
from compas_viewer.components.sidebar import SideBarRight
from compas_viewer.config import Config
from compas_viewer.state import ViewerState
from compas_viewer.uidefinitions import default_sidebar_items


def test_measurement_panel_updates_viewer_presentation_without_mutating_tolerance(monkeypatch):
    app = QApplication.instance() or QApplication([])
    config = Config()
    state = ViewerState(config)
    viewer = SimpleNamespace(config=config, state=state)
    tolerance_before = dict(TOL.__data__)
    monkeypatch.setattr(MeasurementSetting, "viewer", property(lambda _self: viewer), raising=False)

    panel = MeasurementSetting()
    panel.unit_edit.setText(" mm ")
    panel.unit_edit.editingFinished.emit()
    panel.precision_edit.setValue(5)

    assert config.measurement.unit == "mm"
    assert config.measurement.precision == 5
    assert panel.unit_edit.text() == "mm"
    assert dict(TOL.__data__) == tolerance_before
    assert "process-wide, read-only" in panel.tolerance_owner.text()
    assert all(isinstance(label, QLabel) for label in panel.tolerance_labels.values())
    assert panel.tolerance_labels["absolute"].text() == str(TOL.absolute)

    with TOL.temporary(absolute=0.125):
        panel.update()
        assert panel.tolerance_labels["absolute"].text() == "0.125"

    assert dict(TOL.__data__) == tolerance_before
    assert app is not None


def test_measurement_panel_synchronizes_explicit_external_state_changes(monkeypatch):
    app = QApplication.instance() or QApplication([])
    config = Config()
    state = ViewerState(config)
    viewer = SimpleNamespace(config=config, state=state)
    monkeypatch.setattr(MeasurementSetting, "viewer", property(lambda _self: viewer), raising=False)
    panel = MeasurementSetting()

    state.set_measurement_unit("cm")
    state.set_measurement_precision(2)

    assert panel.unit_edit.text() == "cm"
    assert panel.precision_edit.value() == 2
    assert app is not None


def test_default_sidebar_contains_one_units_and_measurement_panel():
    item_types = [item["type"] for item in default_sidebar_items()]

    assert item_types.count("MeasurementSetting") == 1


def test_sidebar_loads_one_units_and_measurement_tab(monkeypatch):
    app = QApplication.instance() or QApplication([])
    config = Config()
    viewer = SimpleNamespace(
        config=config,
        state=ViewerState(config),
        sidebar_items=[{"type": "MeasurementSetting"}],
    )
    monkeypatch.setattr(Base, "viewer", property(lambda _self: viewer))

    sidebar = SideBarRight(SimpleNamespace())

    assert list(sidebar.tabform.tabs) == ["Units and Measurement"]
    assert isinstance(sidebar.measurement_setting, MeasurementSetting)
    assert app is not None
