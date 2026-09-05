from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2

from .exercises.factory import create_analyzer
from .pose_engine import PoseEngine
from .renderer import (
    draw_dashboard,
    draw_pose,
)


@dataclass
class VideoSummary:

    exercise: str
    frames: int
    reps: int
    average_score: float
    valid_frames: int
    duration_seconds: float


def analyze_video(
    input_path: str | Path,
    output_path: str | Path,
    exercise: str,
) -> VideoSummary:

    capture = cv2.VideoCapture(
        str(input_path)
    )

    if not capture.isOpened():

        raise ValueError(
            "Could not open the video file."
        )

    fps = (
        capture.get(
            cv2.CAP_PROP_FPS
        )
        or 30.0
    )

    width = int(
        capture.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
        or 640
    )

    height = int(
        capture.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
        or 480
    )

    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(
            *"mp4v"
        ),
        fps,
        (width, height),
    )

    analyzer = create_analyzer(
        exercise
    )

    scores = []
    valid_frames = 0
    frames = 0

    try:

        with PoseEngine() as pose_engine:

            while True:

                ok, frame = (
                    capture.read()
                )

                if not ok:
                    break

                frames += 1

                pose = pose_engine.detect(
                    frame
                )

                if pose is None:

                    writer.write(frame)
                    continue

                analysis = (
                    analyzer.process(
                        pose
                    )
                )

                scores.append(
                    analysis.score
                )

                if analysis.valid_form:
                    valid_frames += 1

                draw_pose(
                    frame,
                    pose,
                )

                draw_dashboard(
                    frame,
                    analysis,
                )

                writer.write(frame)

    finally:

        capture.release()
        writer.release()

    duration = (
        frames / fps
        if fps > 0
        else 0.0
    )

    average_score = (
        sum(scores) / len(scores)
        if scores
        else 0.0
    )

    return VideoSummary(
        exercise=exercise,
        frames=frames,
        reps=analyzer.counter.count,
        average_score=average_score,
        valid_frames=valid_frames,
        duration_seconds=duration,
    )