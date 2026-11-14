from __future__ import annotations

import threading
import time
from uuid import uuid4

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
        self.rep_metrics = {}

        self.last_rep_event = 0
        self.voice_session_id = uuid4().hex
        self.voice_event_id = 0
        self.voice_text = ""
        self._last_voice_feedback = ""
        self._last_voice_event_at = 0.0
        self.plank_hold_id = uuid4().hex


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

            if self.exercise == "Plank":
                self.analyzer.reset()

            with self.state.lock:
                self.state.score = 0.0
                self.state.phase = "unknown"
                self.state.feedback = "No person detected."
                if self.exercise == "Plank":
                    if self.state.metrics.get("hold_seconds", 0.0) > 0:
                        self.state.plank_hold_id = uuid4().hex
                    self.state.metrics = {
                        "hold_seconds": 0.0,
                    }
                else:
                    self.state.metrics = {}

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

            feedback_message = (
                analysis.feedback[0].message
                if analysis.feedback
                else "Analyzing."
            )
            now = time.monotonic()
            with self.state.lock:
                previous_hold = self.state.metrics.get(
                    "hold_seconds",
                    0.0,
                )
                current_hold = analysis.metrics.get(
                    "hold_seconds",
                    0.0,
                )
                if (
                    self.exercise == "Plank"
                    and previous_hold > 0
                    and current_hold == 0
                ):
                    self.state.plank_hold_id = uuid4().hex

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
                    feedback_message
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
                    self.state.voice_event_id += 1
                    self.state.voice_text = (
                        f"Rep {analysis.reps}. "
                        f"{feedback_message}"
                    )
                    self.state.rep_metrics = dict(
                        analysis.rep_metrics
                    )
                    self.state._last_voice_feedback = (
                        feedback_message
                    )
                    self.state._last_voice_event_at = now
                elif (
                    feedback_message
                    != self.state._last_voice_feedback
                    and now - self.state._last_voice_event_at >= 3.0
                ):
                    self.state.voice_event_id += 1
                    self.state.voice_text = feedback_message
                    self.state._last_voice_feedback = (
                        feedback_message
                    )
                    self.state._last_voice_event_at = now

        return av.VideoFrame.from_ndarray(
            image,
            format="bgr24",
        )

    def on_ended(self):

        try:
            self.engine.close()

        except Exception:
            pass