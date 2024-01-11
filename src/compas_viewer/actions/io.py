from PySide6.QtGui import QDesktopServices
from .action import Action


class ImportFile(Action):
    """Import a file into the viewer."""

    def pressed_action(self):
        raise NotImplementedError("Importing files is not yet implemented.")


class ExportFile(Action):
    """Export a file from the viewer."""

    def pressed_action(self):
        raise NotImplementedError("Exporting files is not yet implemented.")


class OpenURL(Action):
    """Open external url."""

    def pressed_action(self, url: str):
        """ "
        Open external url.

        Parameters
        ----------
        url : str
            The url to open.

        See Also
        --------
        :PySide6:`PySide6/QtGui/QDesktopServices`
        """
        QDesktopServices.openUrl(url)
