from typing import Literal
from typing import Union

from PySide6.QtCore import Qt


def key_mapper(
    key: str,
    type: Literal[0, 1, 2],
) -> Union[Qt.Key, Qt.KeyboardModifier, Qt.MouseButton]:
    """
    Map the key string to the Qt key.

    Parameters
    ----------
    key : str
        The key string which is the same as what it was called in the :class:`PySide6.QtCore.Qt`,
        with **lowercases and with prefix&underscores removed**.
        Check out the reference page to find out the supported keys and the original names.
    type : Literal[0, 1, 2]
        The type of the key for mapping.

        * 0 for :class:`PySide6.QtCore.Qt.Key`,
        * 1 for :class:`PySide6.QtCore.Qt.KeyboardModifier`,
        * 2 for :class:`PySide6.QtCore.Qt.MouseButton`.

    Returns
    -------
    Literal[:class:`Qt.Key`, :class:`Qt.KeyboardModifier`, :class:`Qt.MouseButton`]
        The mapped Qt key.

    Notes
    -----
    This function provides the possibility to use all the supported keys in Qt for the viewer
    by mapping the key string to the Qt key.

    This function handles:

    * :class:`PySide6.QtCore.Qt.Key`
    * :class:`PySide6.QtCore.Qt.KeyboardModifier`
    * :class:`PySide6.QtCore.Qt.MouseButton`

    Examples
    --------
    >>> from compas_viewer.utilities import key_mapper
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

    References
    ----------
    * https://doc.qt.io/qtforpython-6/PySide6/QtCore/Qt.html#PySide6.QtCore.PySide6.QtCore.Qt.Key
    * https://doc.qt.io/qtforpython-6/PySide6/QtCore/Qt.html#PySide6.QtCore.PySide6.QtCore.Qt.KeyboardModifier
    * https://doc.qt.io/qtforpython-6/PySide6/QtCore/Qt.html#PySide6.QtCore.PySide6.QtCore.Qt.MouseButton
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
        raise ValueError(f"Key mapping of {key} not found in Qt.KeyboardModifier. Check your typing?")
    elif type == 2:
        for v in Qt.MouseButton:
            if v.name.replace("Button", "").lower() == key:
                return Qt.MouseButton(v.value)
        raise ValueError(f"Key mapping of {key} not found in Qt.MouseButton. Check your typing?")
    else:
        raise ValueError("The type should be 0, 1, or 2.")
