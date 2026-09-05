from core.exercises.factory import (
    create_analyzer,
)

from core.landmarks import (
    Point,
    PoseLandmarks,
)


def make_pose():

    points = [
        Point(
            x=0.0,
            y=0.0,
            visibility=1.0,
        )
        for _ in range(33)
    ]

    # Left side

    points[11] = Point(
        0.3,
        0.2,
    )

    points[13] = Point(
        0.35,
        0.35,
    )

    points[15] = Point(
        0.3,
        0.5,
    )

    points[23] = Point(
        0.35,
        0.55,
    )

    points[25] = Point(
        0.45,
        0.75,
    )

    points[27] = Point(
        0.45,
        0.95,
    )

    # Right side

    points[12] = Point(
        0.7,
        0.2,
    )

    points[14] = Point(
        0.75,
        0.35,
    )

    points[16] = Point(
        0.7,
        0.5,
    )

    points[24] = Point(
        0.65,
        0.55,
    )

    points[26] = Point(
        0.75,
        0.75,
    )

    points[28] = Point(
        0.75,
        0.95,
    )

    return PoseLandmarks(points)


def test_factory():

    assert (
        create_analyzer(
            "Squat"
        ).name
        == "Squat"
    )

    assert (
        create_analyzer(
            "Push-Up"
        ).name
        == "Push-Up"
    )

    assert (
        create_analyzer(
            "Deadlift"
        ).name
        == "Deadlift"
    )


def test_pose_has_33_landmarks():

    pose = make_pose()

    assert len(pose.points) == 33