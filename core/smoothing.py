from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExponentialSmoother:

    alpha: float = 0.35

    values: dict[str, float] = field(
        default_factory=dict
    )

    def update(
        self,
        key: str,
        value: float,
    ) -> float:

        if key not in self.values:

            self.values[key] = value

        else:

            old = self.values[key]

            self.values[key] = (
                self.alpha * value
                + (1.0 - self.alpha) * old
            )

        return self.values[key]

    def reset(self) -> None:
        self.values.clear()