from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Phase(str, Enum):

    UNKNOWN = "unknown"
    UP = "up"
    DOWN = "down"
    TRANSITION = "transition"


@dataclass
class StateMachine:

    phase: Phase = Phase.UNKNOWN
    stable_frames: int = 0
    required_stable_frames: int = 3

    def update(
        self,
        candidate: Phase,
    ) -> Phase:

        if candidate == self.phase:

            self.stable_frames += 1
            return self.phase

        self.stable_frames += 1

        if (
            self.stable_frames
            >= self.required_stable_frames
        ):

            self.phase = candidate
            self.stable_frames = 0

        return self.phase

    def reset(self) -> None:

        self.phase = Phase.UNKNOWN
        self.stable_frames = 0