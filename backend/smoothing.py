from __future__ import annotations

from dataclasses import dataclass, field

from .landmarks import Point, PoseLandmarks


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


class PoseLandmarkSmoother:
    def __init__(self, alpha: float = 0.35) -> None:
        self._smoother = ExponentialSmoother(alpha=alpha)

    def update(self, pose: PoseLandmarks) -> PoseLandmarks:
        points = self._smooth_points(pose.points, "image")
        world_points = (
            self._smooth_points(pose.world_points, "world")
            if pose.world_points is not None
            else None
        )
        return PoseLandmarks(points, world_points)

    def reset(self) -> None:
        self._smoother.reset()

    def _smooth_points(
        self,
        points: list[Point],
        coordinate_space: str,
    ) -> list[Point]:
        smoothed = []
        for index, point in enumerate(points):
            key = f"{coordinate_space}:{index}"
            smoothed.append(
                Point(
                    x=self._smoother.update(f"{key}:x", point.x),
                    y=self._smoother.update(f"{key}:y", point.y),
                    z=self._smoother.update(f"{key}:z", point.z),
                    visibility=point.visibility,
                    presence=point.presence,
                )
            )
        return smoothed