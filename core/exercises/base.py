from __future__ import annotations

from dataclasses import dataclass, field

from ..feedback import Feedback
from ..landmarks import PoseLandmarks
from ..state_machine import Phase


@dataclass
class Analysis:

    exercise: str

    phase_candidate: Phase = Phase.UNKNOWN
    phase: Phase = Phase.UNKNOWN

    valid_form: bool = False
    score: float = 0.0

    reps: int = 0

    metrics: dict[str, float] = field(
        default_factory=dict
    )

    feedback: list[Feedback] = field(
        default_factory=list
    )

    landmarks_ok: bool = True