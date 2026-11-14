from __future__ import annotations

from ..feedback import (
    Feedback,
    FeedbackLevel,
    score_from_conditions,
)
from ..geometry import angle_from_vertical
from ..rep_counter import RepCounter
from ..state_machine import (
    Phase,
    StateMachine,
)
from backend.config.settings import THRESHOLDS

from .base import Analysis
from .common import best_side, limb_angle, side_landmarks


class BicepCurlAnalyzer:
    name = "Bicep Curl"

    def __init__(self) -> None:
        self.state_machine = StateMachine(
            required_stable_frames=THRESHOLDS.stable_frames,
        )
        self.counter = RepCounter()

    def reset(self) -> None:
        self.state_machine.reset()
        self.counter.reset()

    def process(self, pose) -> Analysis:
        side = best_side(pose, (0, 1, 2))
        shoulder, elbow, wrist, _, _, _ = side_landmarks(side)
        required = (shoulder, elbow, wrist)
        if not pose.visible(
            *required,
            threshold=THRESHOLDS.min_visibility,
        ):
            return Analysis(
                exercise=self.name,
                landmarks_ok=False,
                feedback=[
                    Feedback(
                        FeedbackLevel.INFO,
                        "Keep your shoulder, elbow and wrist visible.",
                        0.0,
                    )
                ],
            )

        elbow_angle = limb_angle(pose, side, "elbow")
        upper_arm_tilt = angle_from_vertical(
            pose.geometry_point(shoulder),
            pose.geometry_point(elbow),
        )
        elbow_down = elbow_angle <= THRESHOLDS.curl_down_elbow
        elbow_up = elbow_angle >= THRESHOLDS.curl_up_elbow
        arm_stable = (
            upper_arm_tilt
            <= THRESHOLDS.curl_max_upper_arm_tilt
        )
        candidate = (
            Phase.DOWN
            if elbow_down
            else Phase.UP
            if elbow_up
            else Phase.TRANSITION
        )
        phase = self.state_machine.update(candidate)
        metrics = {
            "elbow_angle": elbow_angle,
            "upper_arm_tilt": upper_arm_tilt,
        }
        self.counter.update(phase, arm_stable, metrics)

        if not arm_stable:
            feedback = Feedback(
                FeedbackLevel.WARNING,
                "Keep your upper arm steady; avoid swinging.",
                50.0,
            )
        elif candidate == Phase.DOWN:
            feedback = Feedback(
                FeedbackLevel.GOOD,
                "Good curl; lower under control.",
                100.0,
            )
        elif candidate == Phase.UP:
            feedback = Feedback(
                FeedbackLevel.INFO,
                "Extend your arm with control.",
                100.0,
            )
        else:
            feedback = Feedback(
                FeedbackLevel.INFO,
                "Curl smoothly without swinging your elbow.",
                85.0,
            )

        score = score_from_conditions(
            [arm_stable, elbow_down or elbow_up],
        )
        return Analysis(
            exercise=self.name,
            phase_candidate=candidate,
            phase=phase,
            valid_form=arm_stable,
            score=score,
            reps=self.counter.count,
            metrics=metrics,
            rep_metrics=self.counter.completed_metrics or {},
            feedback=[feedback],
        )
