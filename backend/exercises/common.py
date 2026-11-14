from __future__ import annotations

from ..geometry import angle_3d
from ..landmarks import (
    Landmark as L,
    PoseLandmarks,
)


SIDES = (
    "left",
    "right",
)


def side_landmarks(
    side: str,
):

    if side == "left":

        return (
            L.LEFT_SHOULDER,
            L.LEFT_ELBOW,
            L.LEFT_WRIST,
            L.LEFT_HIP,
            L.LEFT_KNEE,
            L.LEFT_ANKLE,
        )

    return (
        L.RIGHT_SHOULDER,
        L.RIGHT_ELBOW,
        L.RIGHT_WRIST,
        L.RIGHT_HIP,
        L.RIGHT_KNEE,
        L.RIGHT_ANKLE,
    )


def best_side(
    pose: PoseLandmarks,
    required_landmarks: tuple[int, ...],
) -> str:

    scores = {}

    for side in SIDES:

        landmarks = side_landmarks(
            side
        )

        scores[side] = min(
            pose[landmarks[index]].visibility
            for index in required_landmarks
        )

    return max(
        scores,
        key=scores.get,
    )


def limb_angle(
    pose: PoseLandmarks,
    side: str,
    joint: str,
) -> float:

    (
        shoulder,
        elbow,
        wrist,
        hip,
        knee,
        ankle,
    ) = side_landmarks(side)

    if joint == "elbow":

        return angle_3d(
            pose.geometry_point(shoulder),
            pose.geometry_point(elbow),
            pose.geometry_point(wrist),
        )

    if joint == "knee":

        return angle_3d(
            pose.geometry_point(hip),
            pose.geometry_point(knee),
            pose.geometry_point(ankle),
        )

    if joint == "hip":

        return angle_3d(
            pose.geometry_point(shoulder),
            pose.geometry_point(hip),
            pose.geometry_point(knee),
        )

    raise ValueError(
        f"Unknown joint: {joint}"
    )