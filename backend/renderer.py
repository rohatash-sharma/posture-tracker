from __future__ import annotations

import cv2

from .exercises.base import Analysis
from .landmarks import (
    Landmark as L,
    PoseLandmarks,
)


CONNECTIONS = [

    (
        L.LEFT_SHOULDER,
        L.RIGHT_SHOULDER,
    ),

    (
        L.LEFT_SHOULDER,
        L.LEFT_ELBOW,
    ),

    (
        L.LEFT_ELBOW,
        L.LEFT_WRIST,
    ),

    (
        L.RIGHT_SHOULDER,
        L.RIGHT_ELBOW,
    ),

    (
        L.RIGHT_ELBOW,
        L.RIGHT_WRIST,
    ),

    (
        L.LEFT_SHOULDER,
        L.LEFT_HIP,
    ),

    (
        L.RIGHT_SHOULDER,
        L.RIGHT_HIP,
    ),

    (
        L.LEFT_HIP,
        L.RIGHT_HIP,
    ),

    (
        L.LEFT_HIP,
        L.LEFT_KNEE,
    ),

    (
        L.LEFT_KNEE,
        L.LEFT_ANKLE,
    ),

    (
        L.RIGHT_HIP,
        L.RIGHT_KNEE,
    ),

    (
        L.RIGHT_KNEE,
        L.RIGHT_ANKLE,
    ),
]


def draw_pose(
    frame,
    pose: PoseLandmarks | None,
):

    if pose is None:
        return frame

    height, width = frame.shape[:2]

    for left, right in CONNECTIONS:

        first = pose[left]
        second = pose[right]

        if (
            first.visibility < 0.35
            or second.visibility < 0.35
        ):
            continue

        p1 = (
            int(first.x * width),
            int(first.y * height),
        )

        p2 = (
            int(second.x * width),
            int(second.y * height),
        )

        cv2.line(
            frame,
            p1,
            p2,
            (0, 210, 255),
            2,
            cv2.LINE_AA,
        )

    for point in pose.points:

        if point.visibility < 0.35:
            continue

        cv2.circle(
            frame,
            (
                int(point.x * width),
                int(point.y * height),
            ),
            4,
            (255, 255, 255),
            -1,
            cv2.LINE_AA,
        )

    return frame


def draw_dashboard(
    frame,
    analysis: Analysis,
):

    height, width = frame.shape[:2]

    panel_width = min(
        470,
        width,
    )

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (0, 0),
        (panel_width, 175),
        (15, 20, 28),
        -1,
    )

    frame[:] = cv2.addWeighted(
        overlay,
        0.82,
        frame,
        0.18,
        0,
    )

    if analysis.score >= 80:

        score_color = (
            80,
            235,
            130,
        )

    elif analysis.score >= 50:

        score_color = (
            0,
            215,
            255,
        )

    else:

        score_color = (
            70,
            80,
            255,
        )

    feedback = (
        analysis.feedback[0].message
        if analysis.feedback
        else "Analyzing..."
    )

    lines = [
        (
            f"{analysis.exercise} | "
            f"REPS: {analysis.reps}"
        ),
        (
            f"PHASE: "
            f"{analysis.phase.value.upper()} | "
            f"FORM: {analysis.score:.0f}%"
        ),
        feedback,
    ]

    for index, text in enumerate(lines):

        cv2.putText(
            frame,
            text,
            (
                16,
                32 + index * 38,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (
                score_color
                if index > 0
                else (245, 245, 245)
            ),
            2,
            cv2.LINE_AA,
        )

    y = 200

    for key, value in analysis.metrics.items():

        cv2.putText(
            frame,
            (
                f"{key.replace('_', ' ').title()}: "
                f"{value:.1f}"
            ),
            (16, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (235, 235, 235),
            1,
            cv2.LINE_AA,
        )

        y += 25

    return frame