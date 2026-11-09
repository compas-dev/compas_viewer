from types import SimpleNamespace

import pytest
from PySide6.QtWidgets import QApplication

from compas_viewer.base import Base
from compas_viewer.components.gridunitsetting import GridUnitSetting
from compas_viewer.components.sidebar import SideBarRight
from compas_viewer.config import Config
from compas_viewer.state import ViewerState
from compas_viewer.uidefinitions import default_sidebar_items


def test_grid_unit_panel_updates_grid_and_measurement_presentation(monkeypatch):
    app = QApplication.instance() or QApplication([])
    config = Config()
    state = ViewerState(config)
    viewer = SimpleNamespace(config=config, state=state)
    monkeypatch.setattr(GridUnitSetting, "viewer", property(lambda _self: viewer), raising=False)

    panel = GridUnitSetting()
    panel.unit_edit.setText(" mm ")
    panel.unit_edit.editingFinished.emit()
    panel.precision_edit.setValue(5)
    state.set("renderer.show_grid", False)
    state.set("renderer.gridsize", (20.0, 8, 30.0, 12))

    assert config.measurement.unit == "mm"
    assert config.measurement.precision == 5
    assert panel.unit_edit.text() == "mm"
    assert not panel._state_controls["renderer.show_grid"].checkbox.isChecked()
    assert (panel.grid.dx, panel.grid.nx, panel.grid.dy, panel.grid.ny) == (20.0, 8.0, 30.0, 12.0)
    assert not hasattr(panel, "tolerance_owner")
    assert not hasattr(panel, "tolerance_labels")
    assert app is not None


def test_grid_unit_panel_synchronizes_explicit_external_measurement_changes(monkeypatch):
    app = QApplication.instance() or QApplication([])
    config = Config()
    state = ViewerState(config)
    viewer = SimpleNamespace(config=config, state=state)
    monkeypatch.setattr(GridUnitSetting, "viewer", property(lambda _self: viewer), raising=False)
    panel = GridUnitSetting()

    state.set_measurement_unit("cm")
    state.set_measurement_precision(2)

    assert panel.unit_edit.text() == "cm"
    assert panel.precision_edit.value() == 2
    assert app is not None


def test_default_sidebar_contains_one_grid_and_units_panel():
    item_types = [item["type"] for item in default_sidebar_items()]

    assert item_types.count("GridUnitSetting") == 1
    assert "MeasurementSetting" not in item_types


def test_sidebar_loads_grid_and_units_and_rejects_retired_component(monkeypatch):
    app = QApplication.instance() or QApplication([])
    config = Config()
    viewer = SimpleNamespace(
        config=config,
        state=ViewerState(config),
        sidebar_items=[{"type": "GridUnitSetting"}],
    )
    monkeypatch.setattr(Base, "viewer", property(lambda _self: viewer))

    sidebar = SideBarRight(SimpleNamespace())

    assert list(sidebar.system_panel.sections) == ["Grid and Units"]
    assert isinstance(sidebar.grid_unit_setting, GridUnitSetting)

    viewer.sidebar_items = [{"type": "MeasurementSetting"}]
    with pytest.raises(ValueError, match="Use 'GridUnitSetting'"):
        SideBarRight(SimpleNamespace())
    assert app is not None
