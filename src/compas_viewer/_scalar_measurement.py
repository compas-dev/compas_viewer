"""Exact scalar measurements for selected scene objects."""

from inspect import getattr_static
from math import hypot
from math import isfinite
from typing import Literal
from typing import SupportsFloat

from compas.scene import SceneItemNotBoundError
from compas.scene import SceneObject
from compas.tolerance import TOL

type ScalarMeasurementKind = Literal["area", "volume"]


class ScalarMeasurementError(ValueError):
    """Report an invalid scalar-measurement request or result."""


class UnsupportedScalarMeasurementError(NotImplementedError):
    """Report a scalar measurement that cannot be resolved exactly."""


def measure_sceneobject_scalar(sceneobject: SceneObject, kind: ScalarMeasurementKind) -> float:
    """Return an exact world-space area or volume for a scene object.

    Parameters
    ----------
    sceneobject
        Stable scene object whose represented item provides the scalar.
    kind
        Scalar measurement to resolve.

    Returns
    -------
    float
        Nonnegative finite world-space scalar.

    Raises
    ------
    ScalarMeasurementError
        If the item returns an invalid scalar.
    UnsupportedScalarMeasurementError
        If the item or its world transformation does not support an exact
        measurement.

    """
    try:
        item = sceneobject.item
    except SceneItemNotBoundError as error:
        raise UnsupportedScalarMeasurementError("The selected scene object has no resolved data item.") from error

    member = _measurement_member(item, kind)

    try:
        value = member() if callable(member) else member
    except NotImplementedError as error:
        raise UnsupportedScalarMeasurementError(f"{type(item).__name__} does not implement {kind} measurement.") from error

    if value is None:
        if kind == "volume":
            raise UnsupportedScalarMeasurementError(f"{type(item).__name__} does not enclose a measurable volume.")
        raise UnsupportedScalarMeasurementError(f"{type(item).__name__} does not provide a measurable area.")

    scalar = _finite_nonnegative_scalar(value, kind)
    matrix = _affine_matrix(sceneobject, kind)
    if kind == "area":
        return _finite_nonnegative_scalar(scalar * _similarity_area_factor(matrix), kind)
    return _finite_nonnegative_scalar(scalar * abs(_linear_determinant(matrix)), kind)


def _measurement_member(item: object, kind: ScalarMeasurementKind) -> object:
    """Return one structural member while preserving descriptor failures."""
    try:
        getattr_static(item, kind)
    except AttributeError:
        try:
            return getattr(item, kind)
        except AttributeError as error:
            raise UnsupportedScalarMeasurementError(f"{type(item).__name__} does not provide a {kind} measurement.") from error
        except NotImplementedError as error:
            raise UnsupportedScalarMeasurementError(f"{type(item).__name__} does not implement {kind} measurement.") from error
    try:
        return getattr(item, kind)
    except NotImplementedError as error:
        raise UnsupportedScalarMeasurementError(f"{type(item).__name__} does not implement {kind} measurement.") from error


def _finite_nonnegative_scalar(value: object, kind: ScalarMeasurementKind) -> float:
    """Normalize a numeric measurement result without accepting text or booleans."""
    if isinstance(value, (bool, str, bytes)) or not isinstance(value, SupportsFloat):
        raise ScalarMeasurementError(f"The {kind} measurement should return a nonnegative finite number.")
    try:
        scalar = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ScalarMeasurementError(f"The {kind} measurement should return a nonnegative finite number.") from error
    if not isfinite(scalar) or scalar < 0:
        raise ScalarMeasurementError(f"The {kind} measurement should return a nonnegative finite number.")
    return scalar


def _affine_matrix(sceneobject: SceneObject, kind: ScalarMeasurementKind) -> list[list[float]]:
    """Return a finite affine world matrix or reject projective measurement."""
    try:
        matrix = [[float(sceneobject.worldtransformation.matrix[row][column]) for column in range(4)] for row in range(4)]
    except (AttributeError, IndexError, TypeError, ValueError, OverflowError) as error:
        raise ScalarMeasurementError("The selected scene object has an invalid world transformation.") from error
    if not all(isfinite(value) for row in matrix for value in row):
        raise ScalarMeasurementError("The selected scene object has a non-finite world transformation.")
    if not TOL.is_allclose(matrix[3], [0.0, 0.0, 0.0, 1.0], rtol=0):
        raise UnsupportedScalarMeasurementError(f"Exact {kind} inspection does not support projective world transformations.")
    return matrix


def _similarity_area_factor(matrix: list[list[float]]) -> float:
    """Return the squared uniform scale of a similarity transformation."""
    columns = [[matrix[row][column] for row in range(3)] for column in range(3)]
    lengths = [hypot(*column) for column in columns]
    reference = max(lengths)
    if reference == 0 or not isfinite(reference):
        raise UnsupportedScalarMeasurementError("Exact area inspection requires a finite nonzero uniform world scale.")
    relative_lengths = [length / reference for length in lengths]
    normalized = [[value / length for value in column] for column, length in zip(columns, lengths, strict=True) if length > 0]
    if len(normalized) != 3:
        raise UnsupportedScalarMeasurementError("Exact area inspection requires a finite nonzero uniform world scale.")
    orthogonal = [_dot(normalized[0], normalized[1]), _dot(normalized[0], normalized[2]), _dot(normalized[1], normalized[2])]
    if not TOL.is_allclose(relative_lengths, [1.0] * 3, rtol=TOL.relative, atol=0) or not TOL.is_allclose(orthogonal, [0.0] * 3, rtol=0):
        raise UnsupportedScalarMeasurementError("Exact area inspection supports only rigid, reflected, or uniformly scaled world transformations.")
    scale = sum(lengths) / 3.0
    factor = scale * scale
    if factor == 0 or not isfinite(factor):
        raise UnsupportedScalarMeasurementError("Exact area inspection requires a finite nonzero uniform world scale.")
    return factor


def _linear_determinant(matrix: list[list[float]]) -> float:
    """Return the determinant of the affine matrix's linear part."""
    a, b, c = matrix[0][:3]
    d, e, f = matrix[1][:3]
    g, h, i = matrix[2][:3]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def _dot(left: list[float], right: list[float]) -> float:
    """Return the dot product of two three-dimensional vectors."""
    return left[0] * right[0] + left[1] * right[1] + left[2] * right[2]


__all__ = []
