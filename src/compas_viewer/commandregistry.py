from collections.abc import Iterator

from compas_viewer.commands import Command


class CommandRegistry:
    """Resolve stable command identifiers to runtime command objects.

    Parameters
    ----------
    commands
        Initial commands keyed by stable identifier.

    """

    def __init__(self, commands: dict[str, Command] | None = None) -> None:
        self._commands = dict(commands or {})

    def __contains__(self, identifier: str) -> bool:
        return identifier in self._commands

    def __getitem__(self, identifier: str) -> Command:
        try:
            return self._commands[identifier]
        except KeyError as error:
            raise KeyError(f"Unknown viewer command: {identifier!r}.") from error

    def __iter__(self) -> Iterator[Command]:
        return iter(self._commands.values())

    def register(self, identifier: str, command: Command, *, replace: bool = False) -> None:
        """Register a command under a stable identifier.

        Parameters
        ----------
        identifier
            Stable, namespaced command identifier.
        command
            Runtime command to register.
        replace
            Whether an existing registration may be replaced.

        Raises
        ------
        ValueError
            If the identifier is empty or already registered.

        """
        if not identifier.strip():
            raise ValueError("Command identifiers cannot be empty.")
        if identifier in self._commands and not replace:
            raise ValueError(f"Command {identifier!r} is already registered.")
        self._commands[identifier] = command


__all__ = ["CommandRegistry"]
