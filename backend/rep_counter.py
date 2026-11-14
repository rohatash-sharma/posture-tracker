from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from .state_machine import Phase


@dataclass
class RepCounter:

    count: int = 0
    armed: bool = False
    completed: bool = False
    rep_metrics: dict[str, tuple[float, float]] | None = None
    completed_metrics: dict[str, tuple[float, float]] | None = None

    def update(
        self,
        phase: Phase,
        valid_form: bool,
        metrics: dict[str, float] | None = None,
    ) -> bool:

        self.completed = False
        self.completed_metrics = None

        if (
            phase == Phase.DOWN
            and valid_form
        ):
            if not self.armed:
                self.armed = True
                self.rep_metrics = {}

        if self.armed:
            if self.rep_metrics is None:
                self.rep_metrics = {}
            for name, value in (metrics or {}).items():
                if not isfinite(value):
                    continue
                previous = self.rep_metrics.get(name)
                self.rep_metrics[name] = (
                    (value, value)
                    if previous is None
                    else (
                        min(previous[0], value),
                        max(previous[1], value),
                    )
                )

        if (
            phase == Phase.UP
            and self.armed
        ):
            if valid_form:
                self.count += 1
                self.completed = True
                self.completed_metrics = dict(
                    self.rep_metrics or {}
                )
            self.armed = False
            self.rep_metrics = None

        return self.completed

    def reset(self) -> None:

        self.count = 0
        self.armed = False
        self.completed = False
        self.rep_metrics = None
        self.completed_metrics = None