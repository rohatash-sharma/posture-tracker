from __future__ import annotations

import threading

import av
import cv2

from streamlit_webrtc import VideoProcessorBase

from .exercises.factory import create_analyzer
from .pose_engine import PoseEngine
from .renderer import (
    draw_dashboard,
    draw_pose,
)


class LiveState:

    def __init__(self):

        self.lock = threading.Lock()

        self.reps = 0
        self.score = 0.0
        self.phase = "unknown"

        self.feedback = (
            "Starting camera..."
        )

        self.metrics = {}

        self.last_rep_event = 0


class ExerciseVideoProcessor(
    VideoProcessorBase
):

    def __init__(
        self,
        exercise: str,
        state: LiveState,
    ):

        self.exercise = exercise
        self.state = state

        self.engine = PoseEngine()

        self.analyzer = (
            create_analyzer(exercise)
        )

    def recv(self, frame):

        image = frame.to_ndarray(
            format="bgr24"
        )

        image = cv2.flip(
            image,
            1,
        )

        pose = self.engine.detect(
            image
        )

        if pose is None:

            cv2.putText(
                image,
                "No person detected",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (40, 80, 255),
                2,
                cv2.LINE_AA,
            )

        else:

            analysis = (
                self.analyzer.process(
                    pose
                )
            )

            draw_pose(
                image,
                pose,
            )

            draw_dashboard(
                image,
                analysis,
            )

            with self.state.lock:

                self.state.reps = (
                    analysis.reps
                )

                self.state.score = (
                    analysis.score
                )

                self.state.phase = (
                    analysis.phase.value
                )

                self.state.feedback = (
                    analysis.feedback[0].message
                    if analysis.feedback
                    else "Analyzing..."
                )

                self.state.metrics = (
                    dict(
                        analysis.metrics
                    )
                )

                if (
                    analysis.reps
                    > self.state.last_rep_event
                ):

                    self.state.last_rep_event = (
                        analysis.reps
                    )

        return av.VideoFrame.from_ndarray(
            image,
            format="bgr24",
        )

    def on_ended(self):

        try:
            self.engine.close()

        except Exception:
            pass