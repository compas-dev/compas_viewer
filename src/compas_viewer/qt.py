from typing import Literal
from typing import overload

from PySide6.QtCore import Qt


@overload
def key_mapper(key: str, type: Literal[0]) -> Qt.Key: ...


@overload
def key_mapper(key: str, type: Literal[1]) -> Qt.KeyboardModifier: ...


@overload
def key_mapper(key: str, type: Literal[2]) -> Qt.MouseButton: ...


def key_mapper(
    key: str,
    type: Literal[0, 1, 2],
) -> Qt.Key | Qt.KeyboardModifier | Qt.MouseButton:
    """Map a normalized name to a Qt input enum.

    Parameters
    ----------
    key
        Lowercase Qt enum name with its prefix and underscores removed.
    type
        Enum family: `0` for keys, `1` for keyboard modifiers, or `2` for
        mouse buttons.

    Returns
    -------
    Qt.Key | Qt.KeyboardModifier | Qt.MouseButton
        The matching Qt enum value.

    Raises
    ------
    ValueError
        If the enum family is invalid or no matching enum value exists.

    Notes
    -----
    Names are matched against the corresponding Qt enum after normalization.

    Examples
    --------
    >>> from compas_viewer.qt import key_mapper
    >>> key_mapper("a", 0)
    <Key.Key_A: 65>
    >>> key_mapper("h", 0)
    <Key.Key_H: 72>
    >>> key_mapper("f5", 0)
    <Key.Key_F5: 16777268>
    >>> key_mapper("superl", 0)
    <Key.Key_Super_L: 16777299>
    >>> key_mapper("bracketleft", 0)
    <Key.Key_BracketLeft: 91>
    >>> key_mapper("colon", 0)
    <Key.Key_Colon: 58>
    >>> key_mapper("control", 1)
    <KeyboardModifier.ControlModifier: 67108864>
    >>> key_mapper("meta", 1)
    <KeyboardModifier.MetaModifier: 268435456>
    >>> key_mapper("left", 2)
    <MouseButton.LeftButton: 1>
    >>> key_mapper("middle", 2)
    <MouseButton.MiddleButton: 4>
    >>> key_mapper("back", 2)
    <MouseButton.BackButton: 8>
    >>> key_mapper("forward", 2)
    <MouseButton.ForwardButton: 16>
    >>> key_mapper("task", 2)
    <MouseButton.TaskButton: 32>
    >>> key_mapper("extra4", 2)
    <MouseButton.ExtraButton4: 64>

    """

    if type == 0:
        for v in Qt.Key:
            if v.name.replace("Key", "").replace("_", "").lower() == key:
                return Qt.Key(v.value)
        raise ValueError(f"Key mapping of {key} not found in Qt.Key. Check your typing?")

    elif type == 1:
        for v in Qt.KeyboardModifier:
            if v.name.replace("Modifier", "").lower() == key:
                return Qt.KeyboardModifier(v.value)
        if key == "no":
            return Qt.KeyboardModifier.NoModifier  # Some times the no modifier is not recognized.
        raise ValueError(f"Key mapping of {key} not found in Qt.KeyboardModifier. Check your typing?")

    elif type == 2:
        for v in Qt.MouseButton:
            if v.name.replace("Button", "").lower() == key:
                return Qt.MouseButton(v.value)
        raise ValueError(f"Key mapping of {key} not found in Qt.MouseButton. Check your typing?")

    else:
        raise ValueError("The type should be 0, 1, or 2.")
