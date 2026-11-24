import subprocess
import sys
from unittest.mock import Mock

import pytest

from compas.scene import SceneObject
from compas_viewer.selection import Selection


def make_selection():
    first = SceneObject(name="First")
    second = SceneObject(name="Second")
    third = SceneObject(name="Third")
    objects = {sceneobject.guid: sceneobject for sceneobject in (first, second, third)}
    changes = []
    selection = Selection(objects.__getitem__, changes.append)
    return selection, (first, second, third), changes


def test_selection_is_ordered_and_deduplicates_each_batch():
    selection, (first, second, third), changes = make_selection()

    assert selection.replace((second, first, second))
    assert selection.add(third, first)

    assert selection.guids == (second.guid, first.guid, third.guid)
    assert selection.objects == (second, first, third)
    assert tuple(selection) == selection.objects
    assert len(selection) == 3
    assert selection
    assert first in selection
    assert first.guid in selection
    assert changes == [
        (second.guid, first.guid),
        (second.guid, first.guid, third.guid),
    ]


def test_selection_mutations_notify_once_and_no_ops_do_not_notify():
    selection, (first, second, third), changes = make_selection()

    assert selection.add(first, second)
    assert not selection.add(first, first)
    assert not selection.replace((first, second, first))
    assert not selection.remove(third)
    assert selection.toggle(second) is False
    assert selection.toggle(third) is True
    assert selection.remove(first, third)
    assert not selection.clear()

    assert changes == [
        (first.guid, second.guid),
        (first.guid,),
        (first.guid, third.guid),
        (),
    ]
    assert not selection


def test_selection_rejects_objects_outside_the_current_scene():
    selection, _, changes = make_selection()
    foreign = SceneObject(name="Foreign")

    with pytest.raises(ValueError, match="current Viewer scene"):
        selection.add(foreign)

    assert not selection
    assert changes == []


def test_selection_module_is_qt_neutral():
    code = "from compas_viewer import Selection; import sys; assert not any(name.startswith('PySide6') for name in sys.modules)"

    result = subprocess.run([sys.executable, "-c", code], check=False, capture_output=True, text=True)

    assert result.returncode == 0, result.stderr


def test_viewer_refresh_handler_synchronizes_sidebar_and_renderer_once():
    from compas_viewer import Viewer
    from compas_viewer.config import Config
    from compas_viewer.state import ViewerState

    viewer = object.__new__(Viewer)
    renderer = Mock()
    sidebar = Mock()
    viewer.ui = Mock(viewport=Mock(renderer=renderer), sidebar=sidebar)
    first = SceneObject(name="First")
    second = SceneObject(name="Second")
    objects = {sceneobject.guid: sceneobject for sceneobject in (first, second)}
    viewer.state = ViewerState(Config(), objects.__getitem__)
    viewer.state.changed.connect(viewer._on_state_changed)

    viewer.state.selection.add(first, second)
    viewer.state.selection.add(first)

    sidebar.update_spatial_selection.assert_called_once_with()
    sidebar.update.assert_not_called()
    renderer.update.assert_called_once_with()
