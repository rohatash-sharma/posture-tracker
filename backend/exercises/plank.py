from __future__ import annotations

import time

from ..feedback import (
    Feedback,
    FeedbackLevel,
)
from ..geometry import angle_3d
from ..state_machine import Phase
from backend.config.settings import THRESHOLDS

from .base import Analysis
from .common import best_side, side_landmarks


class PlankAnalyzer:
    name = "Plank"

    def __init__(self) -> None:
        self.hold_seconds = 0.0
        self._last_timestamp: float | None = None

    def reset(self) -> None:
        self.hold_seconds = 0.0
        self._last_timestamp = None

    def process(
        self,
        pose,
        delta_seconds: float | None = None,
    ) -> Analysis:
        side = best_side(pose, (0, 3, 5))
        shoulder, _, _, hip, _, ankle = side_landmarks(side)
        required = (shoulder, hip, ankle)
        if not pose.visible(
            *required,
            threshold=THRESHOLDS.min_visibility,
        ):
            self.hold_seconds = 0.0
            self._last_timestamp = None
            return Analysis(
                exercise=self.name,
                landmarks_ok=False,
                feedback=[
                    Feedback(
                        FeedbackLevel.INFO,
                        "Keep your shoulder, hip and ankle visible.",
                        0.0,
                    )
                ],
            )

        body_angle = angle_3d(
            pose.geometry_point(shoulder),
            pose.geometry_point(hip),
            pose.geometry_point(ankle),
        )
        body_straight = body_angle >= THRESHOLDS.plank_body_min
        now = time.monotonic()
        elapsed = (
            delta_seconds
            if delta_seconds is not None
            else (
                now - self._last_timestamp
                if self._last_timestamp is not None
                else 0.0
            )
        )
        self._last_timestamp = now

        if body_straight:
            self.hold_seconds += max(0.0, min(elapsed, 1.0))
            phase = Phase.UP
            feedback = Feedback(
                FeedbackLevel.GOOD,
                "Body line looks steady; hold the position.",
                100.0,
            )
            score = 100.0
        else:
            self.hold_seconds = 0.0
            phase = Phase.TRANSITION
            feedback = Feedback(
                FeedbackLevel.WARNING,
                "Keep your shoulders, hips and ankles in a straight line.",
                40.0,
            )
            score = 40.0

        return Analysis(
            exercise=self.name,
            phase_candidate=phase,
            phase=phase,
            valid_form=body_straight,
            score=score,
            hold_seconds=self.hold_seconds,
            metrics={
                "body_angle": body_angle,
                "hold_seconds": self.hold_seconds,
            },
            feedback=[feedback],
        )
