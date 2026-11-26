from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
import math
from pathlib import Path
import tempfile
from typing import Callable

import cv2

from .exercises.factory import create_analyzer
from .exercises.plank import PlankAnalyzer
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
    hold_seconds: float = 0.0
    metric_ranges: dict[str, tuple[float, float]] = field(
        default_factory=dict
    )
    correction_timeline: list[dict[str, object]] = field(
        default_factory=list
    )


def analyze_video(
    input_path: str | Path,
    output_path: str | Path,
    exercise: str,
    progress_callback: Callable[[int, int], None] | None = None,
) -> VideoSummary:
    import av

    analyzer = create_analyzer(exercise)
    capture = cv2.VideoCapture(str(input_path))
    if not capture.isOpened():
        capture.release()
        raise ValueError("Could not open the video file.")

    output = Path(output_path)
    encoded_path: Path | None = None

    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            suffix=".mp4",
            dir=output.parent,
            delete=False,
        ) as encoded:
            encoded_path = Path(encoded.name)

        fps = capture.get(cv2.CAP_PROP_FPS)
        if not math.isfinite(fps) or fps <= 0:
            fps = 30.0
        frame_rate = Fraction(str(fps)).limit_denominator(1000)
        frame_time_base = Fraction(1, 1) / frame_rate

        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if width <= 0 or height <= 0:
            raise ValueError("The video has invalid frame dimensions.")

        output_width = width + width % 2
        output_height = height + height % 2
        total_frames = max(
            0,
            int(capture.get(cv2.CAP_PROP_FRAME_COUNT)),
        )

        scores: list[float] = []
        metric_values: dict[str, list[float]] = {}
        correction_timeline: list[dict[str, object]] = []
        last_correction: tuple[str, str] | None = None
        valid_frames = 0
        frames = 0
        hold_seconds = 0.0
        with PoseEngine() as pose_engine, av.open(
            str(encoded_path),
            mode="w",
            format="mp4",
            options={"movflags": "+faststart"},
        ) as container:
            stream = container.add_stream("libx264", rate=frame_rate)
            stream.width = output_width
            stream.height = output_height
            stream.pix_fmt = "yuv420p"
            stream.time_base = frame_time_base
            stream.options = {
                "preset": "ultrafast",
                "crf": "23",
            }

            while True:
                ok, frame = capture.read()
                if not ok:
                    break

                frames += 1
                if output_width != width or output_height != height:
                    frame = cv2.copyMakeBorder(
                        frame,
                        0,
                        output_height - height,
                        0,
                        output_width - width,
                        cv2.BORDER_REPLICATE,
                    )

                pose = pose_engine.detect(
                    frame,
                    timestamp_ms=round((frames - 1) * 1000 / fps),
                )
                timestamp_seconds = (frames - 1) / fps
                if pose is None:
                    if isinstance(analyzer, PlankAnalyzer):
                        analyzer.reset()
                        hold_seconds = 0.0
                    correction = (
                        "info",
                        "No person detected. Position yourself fully in the camera frame.",
                    )
                    if correction != last_correction:
                        correction_timeline.append({
                            "time_seconds": round(timestamp_seconds, 2),
                            "frame": frames,
                            "level": correction[0],
                            "message": correction[1],
                            "score": 0.0,
                        })
                        last_correction = correction
                else:
                    if isinstance(analyzer, PlankAnalyzer):
                        analysis = analyzer.process(
                            pose,
                            delta_seconds=1.0 / fps,
                        )
                        hold_seconds = analysis.hold_seconds
                    else:
                        analysis = analyzer.process(pose)

                    scores.append(analysis.score)
                    for name, value in analysis.metrics.items():
                        if math.isfinite(value):
                            metric_values.setdefault(name, []).append(value)
                    if analysis.valid_form:
                        valid_frames += 1
                    if analysis.feedback:
                        feedback = analysis.feedback[0]
                        correction = (
                            feedback.level.value,
                            feedback.message,
                        )
                        if correction != last_correction:
                            correction_timeline.append({
                                "time_seconds": round(timestamp_seconds, 2),
                                "frame": frames,
                                "level": correction[0],
                                "message": correction[1],
                                "score": feedback.score,
                            })
                            last_correction = correction
                    draw_pose(frame, pose)
                    draw_dashboard(frame, analysis)

                video_frame = av.VideoFrame.from_ndarray(
                    frame,
                    format="bgr24",
                ).reformat(
                    width=output_width,
                    height=output_height,
                    format="yuv420p",
                )
                video_frame.pts = frames - 1
                video_frame.time_base = frame_time_base
                for packet in stream.encode(video_frame):
                    container.mux(packet)

                if (
                    progress_callback is not None
                    and (
                        frames % max(1, round(fps)) == 0
                        or frames == total_frames
                    )
                ):
                    progress_callback(frames, total_frames)

            if frames == 0:
                raise ValueError("The video contains no decodable frames.")

            for packet in stream.encode():
                container.mux(packet)

        encoded_path.replace(output)
    finally:
        capture.release()
        if encoded_path is not None:
            encoded_path.unlink(missing_ok=True)

    return VideoSummary(
        exercise=exercise,
        frames=frames,
        reps=(
            0
            if isinstance(analyzer, PlankAnalyzer)
            else analyzer.counter.count
        ),
        average_score=(
            sum(scores) / len(scores)
            if scores
            else 0.0
        ),
        valid_frames=valid_frames,
        duration_seconds=frames / fps,
        hold_seconds=hold_seconds,
        metric_ranges={
            name: (min(values), max(values))
            for name, values in metric_values.items()
            if values
        },
        correction_timeline=correction_timeline,
    )
