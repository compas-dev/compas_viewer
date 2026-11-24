"""Private COMPAS Viewer application-theme construction."""

from dataclasses import dataclass
from typing import Literal

from PySide6.QtGui import QColor
from PySide6.QtGui import QPalette


@dataclass(frozen=True, slots=True)
class _ThemeColors:
    window: str
    surface: str
    surface_raised: str
    surface_alternate: str
    text: str
    text_muted: str
    text_disabled: str
    border: str
    accent: str
    accent_hover: str
    accent_pressed: str
    selection: str
    selection_text: str
    link: str
    error: str
    focus: str
    tooltip_surface: str
    tooltip_text: str


_THEMES: dict[Literal["light", "dark"], _ThemeColors] = {
    "light": _ThemeColors(
        window="#F4F7F9",
        surface="#FFFFFF",
        surface_raised="#E8EEF2",
        surface_alternate="#ECF2F5",
        text="#17242D",
        text_muted="#526674",
        text_disabled="#71818C",
        border="#AAB8C2",
        accent="#0077B6",
        accent_hover="#00689D",
        accent_pressed="#005985",
        selection="#0077B6",
        selection_text="#FFFFFF",
        link="#00689D",
        error="#B42318",
        focus="#0077B6",
        tooltip_surface="#17242D",
        tooltip_text="#FFFFFF",
    ),
    "dark": _ThemeColors(
        window="#18242C",
        surface="#10191F",
        surface_raised="#24343E",
        surface_alternate="#1E2D36",
        text="#F2F6F8",
        text_muted="#B8C5CC",
        text_disabled="#87969E",
        border="#52636D",
        accent="#38BDF2",
        accent_hover="#159ED0",
        accent_pressed="#0777AD",
        selection="#0777AD",
        selection_text="#FFFFFF",
        link="#5CC8F2",
        error="#FF8A80",
        focus="#38BDF2",
        tooltip_surface="#24343E",
        tooltip_text="#F2F6F8",
    ),
}


def application_palette(appearance: Literal["light", "dark"]) -> QPalette:
    """Build the application palette for one effective appearance."""
    colors = _THEMES[appearance]
    palette = QPalette()
    roles = {
        QPalette.ColorRole.Window: colors.window,
        QPalette.ColorRole.WindowText: colors.text,
        QPalette.ColorRole.Base: colors.surface,
        QPalette.ColorRole.AlternateBase: colors.surface_alternate,
        QPalette.ColorRole.ToolTipBase: colors.tooltip_surface,
        QPalette.ColorRole.ToolTipText: colors.tooltip_text,
        QPalette.ColorRole.Text: colors.text,
        QPalette.ColorRole.Button: colors.surface_raised,
        QPalette.ColorRole.ButtonText: colors.text,
        QPalette.ColorRole.BrightText: colors.error,
        QPalette.ColorRole.Link: colors.link,
        QPalette.ColorRole.Highlight: colors.selection,
        QPalette.ColorRole.HighlightedText: colors.selection_text,
        QPalette.ColorRole.PlaceholderText: colors.text_disabled,
        QPalette.ColorRole.Light: colors.surface,
        QPalette.ColorRole.Midlight: colors.surface_alternate,
        QPalette.ColorRole.Mid: colors.border,
        QPalette.ColorRole.Dark: colors.border,
        QPalette.ColorRole.Shadow: colors.border,
    }
    for role, color in roles.items():
        palette.setColor(role, QColor(color))

    for role in (
        QPalette.ColorRole.WindowText,
        QPalette.ColorRole.Text,
        QPalette.ColorRole.ButtonText,
        QPalette.ColorRole.PlaceholderText,
    ):
        palette.setColor(QPalette.ColorGroup.Disabled, role, QColor(colors.text_disabled))
    return palette


def application_stylesheet(appearance: Literal["light", "dark"]) -> str:
    """Build the narrow application stylesheet for one appearance."""
    colors = _THEMES[appearance]
    return f"""
QAbstractButton:focus,
QAbstractItemView:focus,
QComboBox:focus,
QLineEdit:focus,
QSpinBox:focus,
QDoubleSpinBox:focus {{
    border: 2px solid {colors.focus};
}}
QAbstractButton:hover {{
    border-color: {colors.accent_hover};
}}
QAbstractButton:pressed {{
    border-color: {colors.accent_pressed};
}}
QLabel[openExternalLinks="true"] {{
    color: {colors.link};
    text-decoration: underline;
}}
QLabel[mutedText="true"] {{
    color: {colors.text_muted};
    font-style: italic;
    padding: 10px;
}}
QGroupBox#viewerSettingsSection {{
    color: {colors.text};
    font-size: 12pt;
    font-weight: bold;
    margin-top: 14px;
}}
QGroupBox#viewerSettingsSection::title {{
    subcontrol-origin: margin;
    left: 6px;
    padding: 2px 4px;
}}
"""
