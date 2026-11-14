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


class LungeAnalyzer:
    name = "Lunge"

    def __init__(self) -> None:
        self.state_machine = StateMachine(
            required_stable_frames=THRESHOLDS.stable_frames,
        )
        self.counter = RepCounter()

    def reset(self) -> None:
        self.state_machine.reset()
        self.counter.reset()

    def process(self, pose) -> Analysis:
        side = best_side(pose, (0, 3, 4, 5))
        shoulder, _, _, hip, knee, ankle = side_landmarks(side)
        required = (shoulder, hip, knee, ankle)
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
                        "Keep your near-side hip, knee and ankle visible.",
                        0.0,
                    )
                ],
            )

        knee_angle = limb_angle(pose, side, "knee")
        torso_tilt = angle_from_vertical(
            pose.geometry_point(shoulder),
            pose.geometry_point(hip),
        )
        knee_down = knee_angle <= THRESHOLDS.lunge_down_knee
        knee_up = knee_angle >= THRESHOLDS.lunge_up_knee
        torso_ok = torso_tilt <= THRESHOLDS.lunge_max_torso_tilt
        candidate = (
            Phase.DOWN
            if knee_down
            else Phase.UP
            if knee_up
            else Phase.TRANSITION
        )
        phase = self.state_machine.update(candidate)
        metrics = {
            "knee_angle": knee_angle,
            "torso_tilt": torso_tilt,
        }
        self.counter.update(phase, torso_ok, metrics)

        if not torso_ok:
            feedback = Feedback(
                FeedbackLevel.BAD,
                "Keep your torso more upright.",
                40.0,
            )
        elif candidate == Phase.DOWN:
            feedback = Feedback(
                FeedbackLevel.GOOD,
                "Good lunge depth; push back to standing.",
                100.0,
            )
        elif candidate == Phase.UP:
            feedback = Feedback(
                FeedbackLevel.INFO,
                "Stand tall and control the next lunge.",
                100.0,
            )
        else:
            feedback = Feedback(
                FeedbackLevel.INFO,
                "Lower with control; keep the front knee aligned.",
                85.0,
            )

        score = score_from_conditions(
            [torso_ok, knee_down or knee_up],
        )
        return Analysis(
            exercise=self.name,
            phase_candidate=candidate,
            phase=phase,
            valid_form=torso_ok,
            score=score,
            reps=self.counter.count,
            metrics=metrics,
            rep_metrics=self.counter.completed_metrics or {},
            feedback=[feedback],
        )
