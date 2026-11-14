import math

import pytest

from backend.exercises.factory import (
    create_analyzer,
)

from backend.state_machine import Phase
from backend.landmarks import (
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

    expected = {
        "Squat",
        "Push-Up",
        "Deadlift",
        "Lunge",
        "Bicep Curl",
        "Plank",
    }
    assert {
        create_analyzer(name).name
        for name in expected
    } == expected


def test_pose_has_33_landmarks():

    pose = make_pose()

    assert len(pose.points) == 33


def pose_with_world_points(positions):
    image_points = [
        Point(0.5, 0.5, visibility=1.0)
        for _ in range(33)
    ]
    world_points = [
        Point(0.0, 0.0, visibility=1.0)
        for _ in range(33)
    ]
    for index, position in positions.items():
        world_points[index] = Point(
            *position,
            visibility=1.0,
        )
    return PoseLandmarks(image_points, world_points)


def standing_pose():
    return pose_with_world_points(
        {
            11: (0.0, 1.5, 0.0),
            13: (0.0, 1.0, 0.0),
            15: (0.0, 0.5, 0.0),
            23: (0.0, 1.0, 0.0),
            25: (0.0, 0.5, 0.0),
            27: (0.0, 0.0, 0.0),
        }
    )


def pose_with_elbow_angle(angle):
    radians = math.radians(angle)
    return pose_with_world_points(
        {
            11: (0.0, 2.0, 0.0),
            13: (0.0, 1.0, 0.0),
            15: (
                math.sin(radians),
                1.0 + math.cos(radians),
                0.0,
            ),
        }
    )


def pose_with_knee_angle(angle, shoulder_x=0.0):
    radians = math.radians(angle)
    knee_x = 0.5 / math.tan(radians / 2)
    return pose_with_world_points(
        {
            11: (shoulder_x, 1.5, 0.0),
            23: (0.0, 1.0, 0.0),
            25: (knee_x, 0.5, 0.0),
            27: (0.0, 0.0, 0.0),
        }
    )


def pose_with_pushup_elbow_angle(angle):
    radians = math.radians(angle)
    elbow_offset = 0.5 / math.tan(radians / 2)
    return pose_with_world_points(
        {
            11: (0.0, 1.0, 0.0),
            13: (0.5, 1.0 - elbow_offset, 0.0),
            15: (1.0, 1.0, 0.0),
            23: (1.0, 1.0, 0.0),
            27: (2.0, 1.0, 0.0),
        }
    )


def pose_with_deadlift_hip_angle(angle):
    radians = math.radians(angle)
    return pose_with_world_points(
        {
            11: (0.5 * math.sin(radians), 1.0 - 0.5 * math.cos(radians), 0.0),
            23: (0.0, 1.0, 0.0),
            25: (0.0, 0.5, 0.0),
            27: (0.0, 0.0, 0.0),
        }
    )


def rep_cycle_poses(exercise):
    if exercise == "Squat":
        return (
            pose_with_knee_angle(90),
            pose_with_knee_angle(130),
            standing_pose(),
        )
    if exercise == "Push-Up":
        return (
            pose_with_pushup_elbow_angle(90),
            pose_with_pushup_elbow_angle(130),
            pose_with_pushup_elbow_angle(180),
        )
    if exercise == "Deadlift":
        return (
            pose_with_deadlift_hip_angle(90),
            pose_with_deadlift_hip_angle(140),
            standing_pose(),
        )
    if exercise == "Lunge":
        return (
            pose_with_knee_angle(90),
            pose_with_knee_angle(130),
            standing_pose(),
        )
    if exercise == "Bicep Curl":
        return (
            pose_with_elbow_angle(60),
            pose_with_elbow_angle(120),
            pose_with_elbow_angle(180),
        )
    raise AssertionError(f"Unexpected repetition exercise: {exercise}")


def test_squat_uses_world_landmarks_for_angles():
    result = create_analyzer("Squat").process(standing_pose())

    assert result.valid_form
    assert result.metrics["torso_tilt"] == 0.0
    assert result.metrics["knee_angle"] == 180.0


def test_lunge_detects_bent_knee_and_upright_torso():
    pose = pose_with_world_points(
        {
            11: (0.0, 1.5, 0.0),
            23: (0.0, 1.0, 0.0),
            25: (0.5, 0.5, 0.0),
            27: (0.0, 0.0, 0.0),
        }
    )

    result = create_analyzer("Lunge").process(pose)

    assert result.valid_form
    assert result.phase_candidate is Phase.DOWN
    assert result.metrics["knee_angle"] == 90.0


def test_bicep_curl_counts_flexion_and_extension():
    analyzer = create_analyzer("Bicep Curl")
    flexed = pose_with_world_points(
        {
            11: (0.0, 2.0, 0.0),
            13: (0.0, 1.0, 0.0),
            15: (0.866, 1.5, 0.0),
        }
    )
    extended = pose_with_world_points(
        {
            11: (0.0, 2.0, 0.0),
            13: (0.0, 1.0, 0.0),
            15: (0.0, 0.0, 0.0),
        }
    )

    for _ in range(3):
        analyzer.process(flexed)
    for _ in range(3):
        result = analyzer.process(extended)

    assert result.reps == 1
    assert result.valid_form


@pytest.mark.parametrize(
    "exercise",
    ["Squat", "Push-Up", "Deadlift", "Lunge", "Bicep Curl"],
)
def test_repetition_exercises_count_through_transition_phase(exercise):
    analyzer = create_analyzer(exercise)
    down, transition, up = rep_cycle_poses(exercise)

    for pose in (down, transition, up):
        for _ in range(3):
            result = analyzer.process(pose)

    assert result.reps == 1
    assert result.phase is Phase.UP
    metric, target = {
        "Squat": ("knee_angle", 90.0),
        "Push-Up": ("elbow_angle", 90.0),
        "Deadlift": ("hip_angle", 90.0),
        "Lunge": ("knee_angle", 90.0),
        "Bicep Curl": ("elbow_angle", 60.0),
    }[exercise]
    assert result.rep_metrics[metric][0] == pytest.approx(target)


def test_deadlift_counts_hinge_without_mistaking_it_for_back_rounding():
    analyzer = create_analyzer("Deadlift")
    hinged = pose_with_world_points(
        {
            11: (-0.5, 1.0, 0.0),
            23: (0.0, 1.0, 0.0),
            25: (0.0, 0.5, 0.0),
            27: (0.5, 0.0, 0.0),
        }
    )

    for _ in range(3):
        analyzer.process(hinged)
    for _ in range(3):
        result = analyzer.process(standing_pose())

    assert result.reps == 1
    assert result.valid_form
    assert "back_angle" not in result.metrics


def test_plank_tracks_only_consecutive_straight_hold():
    analyzer = create_analyzer("Plank")
    straight = pose_with_world_points(
        {
            11: (0.0, 1.0, 0.0),
            23: (0.0, 0.5, 0.0),
            27: (0.0, 0.0, 0.0),
        }
    )
    bent = pose_with_world_points(
        {
            11: (0.0, 1.0, 0.0),
            23: (0.4, 0.5, 0.0),
            27: (0.0, 0.0, 0.0),
        }
    )

    analyzer.process(straight, delta_seconds=0.5)
    result = analyzer.process(straight, delta_seconds=0.5)
    assert result.hold_seconds == 1.0

    result = analyzer.process(bent, delta_seconds=0.5)
    assert result.hold_seconds == 0.0
    assert not result.valid_form