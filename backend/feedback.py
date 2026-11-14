from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FeedbackLevel(str, Enum):

    GOOD = "good"
    WARNING = "warning"
    BAD = "bad"
    INFO = "info"


@dataclass(frozen=True)
class Feedback:

    level: FeedbackLevel
    message: str
    score: float


def score_from_conditions(
    conditions: list[bool],
) -> float:

    if not conditions:
        return 0.0

    return (
        100.0
        * sum(
            bool(condition)
            for condition in conditions
        )
        / len(conditions)
    )