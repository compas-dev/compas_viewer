from dataclasses import asdict
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QSize
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

from compas.colors import Color
from compas_viewer import HERE
from compas_viewer._theme import _THEMES
from compas_viewer._theme import application_palette
from compas_viewer._theme import application_stylesheet
from compas_viewer.components.button import Button
from compas_viewer.components.button import set_icon_path
from compas_viewer.components.container import Container
from compas_viewer.config import Config
from compas_viewer.viewer import Viewer


APPROVED_TOKENS = {
    "light": {
        "window": "#F4F7F9",
        "surface": "#FFFFFF",
        "surface_raised": "#E8EEF2",
        "surface_alternate": "#ECF2F5",
        "text": "#17242D",
        "text_muted": "#526674",
        "text_disabled": "#71818C",
        "border": "#AAB8C2",
        "accent": "#0077B6",
        "accent_hover": "#00689D",
        "accent_pressed": "#005985",
        "selection": "#0077B6",
        "selection_text": "#FFFFFF",
        "link": "#00689D",
        "error": "#B42318",
        "focus": "#0077B6",
        "tooltip_surface": "#17242D",
        "tooltip_text": "#FFFFFF",
    },
    "dark": {
        "window": "#18242C",
        "surface": "#10191F",
        "surface_raised": "#24343E",
        "surface_alternate": "#1E2D36",
        "text": "#F2F6F8",
        "text_muted": "#B8C5CC",
        "text_disabled": "#87969E",
        "border": "#52636D",
        "accent": "#38BDF2",
        "accent_hover": "#159ED0",
        "accent_pressed": "#0777AD",
        "selection": "#0777AD",
        "selection_text": "#FFFFFF",
        "link": "#5CC8F2",
        "error": "#FF8A80",
        "focus": "#38BDF2",
        "tooltip_surface": "#24343E",
        "tooltip_text": "#F2F6F8",
    },
}


@pytest.fixture
def application(request):
    app = QApplication.instance() or QApplication([])
    previous_palette = app.palette()
    previous_stylesheet = app.styleSheet()
    previous_icon = app.windowIcon()

    def restore():
        app.setPalette(previous_palette)
        app.setStyleSheet(previous_stylesheet)
        app.setWindowIcon(previous_icon)

    request.addfinalizer(restore)
    return app


@pytest.mark.parametrize("appearance", ["light", "dark"])
def test_theme_tokens_equal_the_approved_literals(appearance):
    assert asdict(_THEMES[appearance]) == APPROVED_TOKENS[appearance]


@pytest.mark.parametrize("appearance", ["light", "dark"])
def test_palette_maps_all_semantic_application_roles(appearance):
    colors = APPROVED_TOKENS[appearance]
    palette = application_palette(appearance)
    expected = {
        QPalette.ColorRole.Window: colors["window"],
        QPalette.ColorRole.WindowText: colors["text"],
        QPalette.ColorRole.Base: colors["surface"],
        QPalette.ColorRole.AlternateBase: colors["surface_alternate"],
        QPalette.ColorRole.ToolTipBase: colors["tooltip_surface"],
        QPalette.ColorRole.ToolTipText: colors["tooltip_text"],
        QPalette.ColorRole.Text: colors["text"],
        QPalette.ColorRole.Button: colors["surface_raised"],
        QPalette.ColorRole.ButtonText: colors["text"],
        QPalette.ColorRole.BrightText: colors["error"],
        QPalette.ColorRole.Link: colors["link"],
        QPalette.ColorRole.Highlight: colors["selection"],
        QPalette.ColorRole.HighlightedText: colors["selection_text"],
        QPalette.ColorRole.PlaceholderText: colors["text_disabled"],
        QPalette.ColorRole.Light: colors["surface"],
        QPalette.ColorRole.Midlight: colors["surface_alternate"],
        QPalette.ColorRole.Mid: colors["border"],
        QPalette.ColorRole.Dark: colors["border"],
        QPalette.ColorRole.Shadow: colors["border"],
    }

    for role, color in expected.items():
        assert palette.color(QPalette.ColorGroup.Active, role).name().upper() == color

    for role in (
        QPalette.ColorRole.WindowText,
        QPalette.ColorRole.Text,
        QPalette.ColorRole.ButtonText,
        QPalette.ColorRole.PlaceholderText,
    ):
        assert palette.color(QPalette.ColorGroup.Disabled, role).name().upper() == colors["text_disabled"]


@pytest.mark.parametrize("appearance", ["light", "dark"])
def test_stylesheet_uses_accessible_interaction_and_component_tokens(appearance):
    colors = APPROVED_TOKENS[appearance]
    stylesheet = application_stylesheet(appearance)

    assert f"border: 2px solid {colors['focus']}" in stylesheet
    assert f"border-color: {colors['accent_hover']}" in stylesheet
    assert f"border-color: {colors['accent_pressed']}" in stylesheet
    assert f"color: {colors['link']}" in stylesheet
    assert f"color: {colors['text_muted']}" in stylesheet
    assert 'QLabel[openExternalLinks="true"]' in stylesheet
    assert 'QLabel[mutedText="true"]' in stylesheet
    assert "QGroupBox#viewerSettingsSection" in stylesheet
    assert "font-size: 12pt" in stylesheet
    assert "font-weight: bold" in stylesheet


@pytest.mark.parametrize("appearance", ["light", "dark"])
def test_approved_contrast_targets(appearance):
    colors = APPROVED_TOKENS[appearance]

    assert contrast(colors["text"], colors["window"]) >= 4.5
    assert contrast(colors["text_muted"], colors["window"]) >= 4.5
    assert contrast(colors["text_disabled"], colors["window"]) >= 3.0
    assert contrast(colors["selection_text"], colors["selection"]) >= 4.5
    assert contrast(colors["link"], colors["surface"]) >= 4.5
    assert contrast(colors["error"], colors["surface"]) >= 4.5
    assert contrast(colors["focus"], colors["surface"]) >= 3.0


@pytest.mark.parametrize("icon_name", ["view_perspective.svg", "view_top.svg", "view_front.svg", "view_right.svg", "view_ortho.svg"])
@pytest.mark.parametrize("appearance", ["light", "dark"])
def test_monochrome_button_icons_follow_the_active_palette(application, appearance, icon_name):
    colors = APPROVED_TOKENS[appearance]
    application.setPalette(application_palette(appearance))
    icon = set_icon_path(icon_name)

    assert rendered_icon_color(icon) == colors["text"]


def test_existing_button_icon_retints_when_the_application_palette_changes(application):
    application.setPalette(application_palette("light"))
    button = Button(icon_path="view_top.svg")
    assert rendered_icon_color(button.widget.icon()) == APPROVED_TOKENS["light"]["text"]

    application.setPalette(application_palette("dark"))
    application.processEvents()

    assert rendered_icon_color(button.widget.icon()) == APPROVED_TOKENS["dark"]["text"]


def test_palette_icon_rendering_does_not_change_the_configured_application_icon(application):
    configured = QIcon(str(HERE / "assets" / "icons" / "compas_icon_white.png"))
    application.setWindowIcon(configured)
    cache_key = application.windowIcon().cacheKey()

    set_icon_path("view_top.svg").pixmap(QSize(32, 32))

    assert application.windowIcon().cacheKey() == cache_key


def test_container_muted_text_uses_theme_semantics():
    container = Container()

    container.display_text("Nothing selected")

    label = container.layout.itemAt(0).widget()
    assert label is not None
    assert label.property("mutedText") is True
    assert not label.styleSheet()


def test_public_appearance_switch_applies_the_requested_variant():
    instance = object.__new__(Viewer)
    instance.state = Mock()
    instance.state.set.return_value = False
    instance._apply_appearance = Mock()

    Viewer.set_appearance(instance, "dark")

    instance.state.set.assert_called_once_with("ui.appearance", "dark")
    instance._apply_appearance.assert_called_once_with("dark")


def test_system_color_scheme_changes_reapply_only_system_appearance():
    instance = object.__new__(Viewer)
    instance._config = Config()
    instance._apply_appearance = Mock()

    Viewer._on_system_color_scheme_changed(instance, Qt.ColorScheme.Dark)
    instance._apply_appearance.assert_called_once_with("system")

    instance._apply_appearance.reset_mock()
    instance.config.ui.appearance = "light"
    Viewer._on_system_color_scheme_changed(instance, Qt.ColorScheme.Dark)
    instance._apply_appearance.assert_not_called()


def test_applying_appearance_preserves_actual_renderer_colors():
    instance = object.__new__(Viewer)
    instance.app = Mock()
    instance.state = Mock()
    instance._config = Config()
    instance.config.renderer.backgroundcolor = Color(0.1, 0.2, 0.3)
    instance.config.renderer.selectioncolor = Color(0.3, 0.4, 0.5)
    instance.config.renderer.gridcolor = Color(0.5, 0.6, 0.7)
    before = (
        instance.config.renderer.backgroundcolor.rgba,
        instance.config.renderer.selectioncolor.rgba,
        instance.config.renderer.gridcolor.rgba,
    )

    Viewer._apply_appearance(instance, "dark")

    assert instance.app.setPalette.call_count == 1
    instance.app.setStyleSheet.assert_called_once_with(application_stylesheet("dark"))
    assert (
        instance.config.renderer.backgroundcolor.rgba,
        instance.config.renderer.selectioncolor.rgba,
        instance.config.renderer.gridcolor.rgba,
    ) == before
    instance.state.set.assert_not_called()


def contrast(foreground: str, background: str) -> float:
    lighter, darker = sorted((relative_luminance(foreground), relative_luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def relative_luminance(color: str) -> float:
    channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    red, green, blue = (channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def rendered_icon_color(icon: QIcon) -> str:
    image = icon.pixmap(QSize(32, 32)).toImage()
    rendered = [image.pixelColor(x, y) for y in range(image.height()) for x in range(image.width()) if image.pixelColor(x, y).alpha() > 128]
    assert rendered
    return max(rendered, key=lambda color: color.alpha()).name().upper()
