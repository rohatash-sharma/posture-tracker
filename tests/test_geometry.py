import math

from core.geometry import angle_3d


def test_right_angle():

    result = angle_3d(
        (1, 0, 0),
        (0, 0, 0),
        (0, 1, 0),
    )

    assert math.isclose(
        result,
        90.0,
        abs_tol=1e-6,
    )


def test_straight_angle():

    result = angle_3d(
        (-1, 0, 0),
        (0, 0, 0),
        (1, 0, 0),
    )

    assert math.isclose(
        result,
        180.0,
        abs_tol=1e-6,
    )