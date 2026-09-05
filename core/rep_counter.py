from __future__ import annotations

from dataclasses import dataclass

from .state_machine import Phase


@dataclass
class RepCounter:

    count: int = 0
    last_phase: Phase = Phase.UNKNOWN
    armed: bool = False
    completed: bool = False

    def update(
        self,
        phase: Phase,
        valid_form: bool,
    ) -> bool:

        self.completed = False

        if (
            phase == Phase.DOWN
            and valid_form
        ):
            self.armed = True

        if (
            phase == Phase.UP
            and self.armed
            and valid_form
            and self.last_phase == Phase.DOWN
        ):

            self.count += 1
            self.armed = False
            self.completed = True

        self.last_phase = phase

        return self.completed

    def reset(self) -> None:

        self.count = 0
        self.last_phase = Phase.UNKNOWN
        self.armed = False
        self.completed = False