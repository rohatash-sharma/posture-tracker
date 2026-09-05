from __future__ import annotations

from ..feedback import (
    Feedback,
    FeedbackLevel,
    score_from_conditions,
)

from ..geometry import angle_3d

from ..landmarks import PoseLandmarks

from ..rep_counter import RepCounter

from ..state_machine import (
    Phase,
    StateMachine,
)

from config.settings import THRESHOLDS

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

        side = best_side(pose)

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

        back_angle = angle_3d(
            pose[shoulder],
            pose[hip],
            pose[knee],
        )

        lockout = (
            hip_angle
            >= THRESHOLDS.deadlift_lockout_hip
            and knee_angle
            >= THRESHOLDS.deadlift_lockout_hip
        )

        lowered = (
            knee_angle
            <= THRESHOLDS.deadlift_down_knee
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

        back_ok = (
            back_angle
            >= THRESHOLDS.deadlift_back_min
        )

        valid = back_ok

        self.counter.update(
            phase,
            valid,
        )

        if not back_ok:

            feedback = Feedback(
                FeedbackLevel.BAD,
                "Avoid rounding your back.",
                40.0,
            )

        elif phase == Phase.UP:

            feedback = Feedback(
                FeedbackLevel.GOOD,
                "Strong lockout. Keep the back neutral.",
                100.0,
            )

        else:

            feedback = Feedback(
                FeedbackLevel.GOOD,
                "Control the hinge.",
                100.0,
            )

        score = score_from_conditions(
            [
                back_ok,
                lockout or lowered,
            ]
        )

        return Analysis(
            exercise=self.name,
            phase_candidate=candidate,
            phase=phase,
            valid_form=valid,
            score=score,
            reps=self.counter.count,
            metrics={
                "knee_angle": knee_angle,
                "hip_angle": hip_angle,
                "back_angle": back_angle,
            },
            feedback=[feedback],
        )