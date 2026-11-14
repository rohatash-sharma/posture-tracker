from __future__ import annotations

from ..feedback import (
    Feedback,
    FeedbackLevel,
    score_from_conditions,
)

from ..landmarks import PoseLandmarks

from ..rep_counter import RepCounter

from ..state_machine import (
    Phase,
    StateMachine,
)

from backend.config.settings import THRESHOLDS

from .base import Analysis

from .common import (
    best_side,
    limb_angle,
    side_landmarks,
)


class DeadliftAnalyzer:

    name = "Deadlift"

    def __init__(self):

        self.state_machine = (
            StateMachine(
                required_stable_frames=(
                    THRESHOLDS.stable_frames
                )
            )
        )

        self.counter = RepCounter()

    def reset(self):

        self.state_machine.reset()
        self.counter.reset()

    def process(
        self,
        pose: PoseLandmarks,
    ) -> Analysis:

        side = best_side(pose, (0, 3, 4, 5))

        (
            shoulder,
            _,
            _,
            hip,
            knee,
            ankle,
        ) = side_landmarks(side)

        required = (
            shoulder,
            hip,
            knee,
            ankle,
        )

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
                        "Use a clear side view with shoulder, hip, knee and ankle visible.",
                        0.0,
                    )
                ],
            )

        knee_angle = limb_angle(
            pose,
            side,
            "knee",
        )

        hip_angle = limb_angle(
            pose,
            side,
            "hip",
        )

        lockout = (
            hip_angle
            >= THRESHOLDS.deadlift_lockout_hip
            and knee_angle
            >= THRESHOLDS.deadlift_lockout_hip
        )

        lowered = (
            hip_angle
            <= THRESHOLDS.deadlift_down_hip
        )

        candidate = (
            Phase.UP
            if lockout
            else Phase.DOWN
            if lowered
            else Phase.TRANSITION
        )

        phase = (
            self.state_machine.update(
                candidate
            )
        )

        valid = lockout or lowered

        metrics = {
            "knee_angle": knee_angle,
            "hip_angle": hip_angle,
        }
        self.counter.update(
            phase,
            valid,
            metrics,
        )

        if candidate == Phase.UP:

            feedback = Feedback(
                FeedbackLevel.GOOD,
                "Stand tall to finish the rep.",
                100.0,
            )

        elif candidate == Phase.DOWN:

            feedback = Feedback(
                FeedbackLevel.INFO,
                "Hinge reached; maintain a neutral spine.",
                100.0,
            )

        else:

            feedback = Feedback(
                FeedbackLevel.INFO,
                "Hinge with control; spinal rounding is not measured.",
                70.0,
            )

        score = score_from_conditions(
            [
                lockout or lowered,
                phase in (Phase.UP, Phase.DOWN),
            ]
        )

        return Analysis(
            exercise=self.name,
            phase_candidate=candidate,
            phase=phase,
            valid_form=valid,
            score=score,
            reps=self.counter.count,
            metrics=metrics,
            rep_metrics=self.counter.completed_metrics or {},
            feedback=[feedback],
        )