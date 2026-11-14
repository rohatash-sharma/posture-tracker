from __future__ import annotations

from ..feedback import (
    Feedback,
    FeedbackLevel,
    score_from_conditions,
)

from ..geometry import angle_from_vertical

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


class SquatAnalyzer:

    name = "Squat"

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
                        "Move so your full body is visible.",
                        0.0,
                    )
                ],
            )

        knee_angle = limb_angle(
            pose,
            side,
            "knee",
        )

        torso_tilt = angle_from_vertical(
            pose.geometry_point(shoulder),
            pose.geometry_point(hip),
        )

        is_down = (
            knee_angle
            <= THRESHOLDS.squat_down_knee
        )

        is_up = (
            knee_angle
            >= THRESHOLDS.squat_up_knee
        )

        torso_ok = (
            torso_tilt
            <= THRESHOLDS.squat_max_torso_tilt
        )

        candidate = (
            Phase.DOWN
            if is_down
            else Phase.UP
            if is_up
            else Phase.TRANSITION
        )

        phase = (
            self.state_machine.update(
                candidate
            )
        )

        valid = torso_ok

        metrics = {
            "knee_angle": knee_angle,
            "torso_tilt": torso_tilt,
        }
        self.counter.update(
            phase,
            valid,
            metrics,
        )

        if not torso_ok:

            feedback = Feedback(
                FeedbackLevel.BAD,
                "Reduce forward torso lean.",
                40.0,
            )

        elif candidate == Phase.DOWN:

            feedback = Feedback(
                FeedbackLevel.GOOD,
                "Good depth; drive up with control.",
                100.0,
            )

        elif (
            candidate == Phase.TRANSITION
            and knee_angle
            <= THRESHOLDS.squat_down_knee + 15
        ):

            feedback = Feedback(
                FeedbackLevel.WARNING,
                "Go a little deeper.",
                70.0,
            )

        else:

            feedback = Feedback(
                FeedbackLevel.INFO,
                "Move through a controlled range.",
                85.0,
            )

        score = score_from_conditions(
            [
                torso_ok,
                is_down or is_up,
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