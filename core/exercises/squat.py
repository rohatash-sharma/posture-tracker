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

        back_angle = angle_3d(
            pose[shoulder],
            pose[hip],
            pose[knee],
        )

        is_down = (
            knee_angle
            <= THRESHOLDS.squat_down_knee
        )

        is_up = (
            knee_angle
            >= THRESHOLDS.squat_up_knee
        )

        back_ok = (
            back_angle
            >= THRESHOLDS.squat_back_min
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

        valid = back_ok

        self.counter.update(
            phase,
            valid,
        )

        if not back_ok:

            feedback = Feedback(
                FeedbackLevel.BAD,
                "Keep your back more upright.",
                40.0,
            )

        elif (
            phase == Phase.DOWN
            and knee_angle
            > THRESHOLDS.squat_down_knee
        ):

            feedback = Feedback(
                FeedbackLevel.WARNING,
                "Go a little deeper.",
                70.0,
            )

        else:

            feedback = Feedback(
                FeedbackLevel.GOOD,
                "Good squat form.",
                100.0,
            )

        score = score_from_conditions(
            [
                back_ok,
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
            metrics={
                "knee_angle": knee_angle,
                "back_angle": back_angle,
            },
            feedback=[feedback],
        )