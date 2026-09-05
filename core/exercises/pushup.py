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


class PushUpAnalyzer:

    name = "Push-Up"

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
            elbow,
            wrist,
            hip,
            knee,
            ankle,
        ) = side_landmarks(side)

        required = (
            shoulder,
            elbow,
            wrist,
            hip,
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
                        "Use a side view and keep shoulder, hip and ankle visible.",
                        0.0,
                    )
                ],
            )

        elbow_angle = limb_angle(
            pose,
            side,
            "elbow",
        )

        body_angle = angle_3d(
            pose[shoulder],
            pose[hip],
            pose[ankle],
        )

        is_down = (
            elbow_angle
            <= THRESHOLDS.pushup_down_elbow
        )

        is_up = (
            elbow_angle
            >= THRESHOLDS.pushup_up_elbow
        )

        body_straight = (
            body_angle
            >= THRESHOLDS.pushup_body_min
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

        valid = body_straight

        self.counter.update(
            phase,
            valid,
        )

        if not body_straight:

            feedback = Feedback(
                FeedbackLevel.BAD,
                "Keep your body in a straighter line.",
                40.0,
            )

        elif (
            phase == Phase.DOWN
            and elbow_angle
            > THRESHOLDS.pushup_down_elbow
        ):

            feedback = Feedback(
                FeedbackLevel.WARNING,
                "Lower a little more.",
                70.0,
            )

        else:

            feedback = Feedback(
                FeedbackLevel.GOOD,
                "Good push-up form.",
                100.0,
            )

        score = score_from_conditions(
            [
                body_straight,
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
                "elbow_angle": elbow_angle,
                "body_angle": body_angle,
            },
            feedback=[feedback],
        )