from dataclasses import dataclass
from inspect import Parameter
from inspect import signature
from typing import Any


@dataclass(frozen=True, slots=True)
class ObjectParameter:
    """Describe a constructor parameter and its current instance value.

    Parameters
    ----------
    name
        Constructor parameter name.
    annotation
        Parameter type annotation, if available.
    default
        Constructor default, if available.
    has_default
        Whether the constructor declares a default.
    required
        Whether callers must provide the parameter.
    value
        Current value resolved from the object, if available.
    available
        Whether a current value could be resolved safely.
    writable
        Whether the value can be assigned through a public attribute.

    """

    name: str
    annotation: Any | None
    default: Any | None
    has_default: bool
    required: bool
    value: Any | None
    available: bool
    writable: bool


def inspect_object_parameters(obj: object | None) -> dict[str, ObjectParameter]:
    """Inspect constructor parameters and resolve their current values.

    Values are resolved from public attributes first and from COMPAS
    ``__data__`` mappings second. Variadic parameters are omitted because they
    do not describe stable object state.

    Parameters
    ----------
    obj
        Object whose constructor and state should be inspected.

    Returns
    -------
    dict[str, ObjectParameter]
        Parameter information keyed by constructor parameter name.

    """
    if obj is None:
        return {}

    try:
        parameters = signature(type(obj)).parameters.values()
    except (TypeError, ValueError):
        return {}

    try:
        serialized = getattr(obj, "__data__", None)
    except (AttributeError, RuntimeError, TypeError, ValueError):
        serialized = None
    if not isinstance(serialized, dict):
        serialized = {}

    result: dict[str, ObjectParameter] = {}
    for parameter in parameters:
        if parameter.name == "self" or parameter.kind in {Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD}:
            continue

        available = False
        resolved_from_attribute = False
        value = None
        try:
            value = getattr(obj, parameter.name)
            available = not callable(value)
            resolved_from_attribute = available
        except (AttributeError, RuntimeError, TypeError, ValueError):
            pass

        if not available and parameter.name in serialized:
            value = serialized[parameter.name]
            available = True

        has_default = parameter.default is not Parameter.empty
        annotation = None if parameter.annotation is Parameter.empty else parameter.annotation
        result[parameter.name] = ObjectParameter(
            name=parameter.name,
            annotation=annotation,
            default=parameter.default if has_default else None,
            has_default=has_default,
            required=not has_default,
            value=value if available else None,
            available=available,
            writable=resolved_from_attribute and _is_writable_attribute(obj, parameter.name),
        )

    return result


def _is_writable_attribute(obj: object, name: str) -> bool:
    """Return whether an object's public attribute can be assigned."""
    descriptor = getattr(type(obj), name, None)
    return not isinstance(descriptor, property) or descriptor.fset is not None


def modify_object_parameters(obj: object, values: dict[str, Any]) -> None:
    """Assign inspected constructor parameters to an existing object.

    All requested values are validated before assignment. If a setter rejects
    a value, parameters already changed by this call are restored.

    Parameters
    ----------
    obj
        Object whose public constructor parameters should be changed.
    values
        New parameter values keyed by constructor parameter name.

    Raises
    ------
    AttributeError
        If a requested parameter is unavailable or read-only.
    ValueError
        If a requested name is not a constructor parameter.

    """
    parameters = inspect_object_parameters(obj)
    originals: dict[str, Any] = {}
    for name in values:
        try:
            parameter = parameters[name]
        except KeyError as error:
            raise ValueError(f"{name!r} is not a constructor parameter of {type(obj).__name__}.") from error
        if not parameter.available or not parameter.writable:
            raise AttributeError(f"Parameter {name!r} of {type(obj).__name__} is not writable.")
        originals[name] = parameter.value

    changed: list[str] = []
    try:
        for name, value in values.items():
            setattr(obj, name, value)
            changed.append(name)
    except Exception:
        for name in reversed(changed):
            try:
                setattr(obj, name, originals[name])
            except Exception:
                pass
        raise


def object_parameter_values(obj: object | None) -> dict[str, Any]:
    """Return constructor parameter values available on an object.

    Parameters
    ----------
    obj
        Object whose current parameter values should be resolved.

    Returns
    -------
    dict[str, Any]
        Available values keyed by constructor parameter name.

    """
    return {name: parameter.value for name, parameter in inspect_object_parameters(obj).items() if parameter.available}


__all__ = ["ObjectParameter", "inspect_object_parameters", "modify_object_parameters", "object_parameter_values"]
