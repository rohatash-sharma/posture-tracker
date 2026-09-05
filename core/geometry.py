from __future__ import annotations

import math
from typing import Iterable

import numpy as np


def as_xyz(point) -> np.ndarray:
    """
    Convert a point-like object into a NumPy XYZ vector.
    """

    if hasattr(point, "x"):
        return np.array(
            [
                point.x,
                point.y,
                getattr(point, "z", 0.0),
            ],
            dtype=float,
        )

    values = np.asarray(
        point,
        dtype=float,
    )

    if values.size < 3:
        values = np.pad(
            values,
            (0, 3 - values.size),
        )

    return values[:3]


def angle_3d(a, b, c) -> float:
    """
    Calculate angle ABC in degrees.

    B is the vertex.
    """

    va = as_xyz(a) - as_xyz(b)
    vc = as_xyz(c) - as_xyz(b)

    denom = (
        np.linalg.norm(va)
        * np.linalg.norm(vc)
    )

    if denom < 1e-9:
        return float("nan")

    cosine = float(
        np.dot(va, vc) / denom
    )

    cosine = max(
        -1.0,
        min(1.0, cosine),
    )

    return math.degrees(
        math.acos(cosine)
    )


def angle_2d(a, b, c) -> float:
    """
    Calculate angle ABC using only X/Y.
    """

    return angle_3d(
        as_xyz(a)[:2],
        as_xyz(b)[:2],
        as_xyz(c)[:2],
    )


def line_angle(a, b) -> float:
    """
    Angle of AB relative to horizontal.
    """

    vector = (
        as_xyz(b)
        - as_xyz(a)
    )

    return math.degrees(
        math.atan2(
            abs(float(vector[1])),
            abs(float(vector[0])) + 1e-12,
        )
    )


def midpoint(a, b) -> np.ndarray:
    return (
        as_xyz(a)
        + as_xyz(b)
    ) / 2.0


def is_finite(*values: float) -> bool:
    return all(
        np.isfinite(value)
        for value in values
    )


def mean_or_nan(
    values: Iterable[float],
) -> float:

    valid = [
        value
        for value in values
        if np.isfinite(value)
    ]

    if not valid:
        return float("nan")

    return float(
        np.mean(valid)
    )