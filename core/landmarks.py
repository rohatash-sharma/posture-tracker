from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any


class Landmark(IntEnum):
    NOSE = 0

    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3

    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6

    LEFT_EAR = 7
    RIGHT_EAR = 8

    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14

    LEFT_WRIST = 15
    RIGHT_WRIST = 16

    LEFT_PINKY = 17
    RIGHT_PINKY = 18

    LEFT_INDEX = 19
    RIGHT_INDEX = 20

    LEFT_THUMB = 21
    RIGHT_THUMB = 22

    LEFT_HIP = 23
    RIGHT_HIP = 24

    LEFT_KNEE = 25
    RIGHT_KNEE = 26

    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    LEFT_HEEL = 29
    RIGHT_HEEL = 30

    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32


@dataclass(frozen=True)
class Point:
    x: float
    y: float
    z: float = 0.0
    visibility: float = 1.0
    presence: float = 1.0

    @classmethod
    def from_mp(
        cls,
        point: Any,
    ) -> "Point":

        return cls(
            x=float(point.x),
            y=float(point.y),
            z=float(
                getattr(
                    point,
                    "z",
                    0.0,
                )
            ),
            visibility=float(
                getattr(
                    point,
                    "visibility",
                    1.0,
                )
                or 0.0
            ),
            presence=float(
                getattr(
                    point,
                    "presence",
                    1.0,
                )
                or 0.0
            ),
        )


class PoseLandmarks:

    def __init__(
        self,
        points: list[Point],
    ):

        if len(points) != 33:
            raise ValueError(
                "Expected exactly 33 "
                f"landmarks, got {len(points)}"
            )

        self.points = points

    @classmethod
    def from_mediapipe(
        cls,
        points,
    ):

        return cls(
            [
                Point.from_mp(point)
                for point in points
            ]
        )

    def __getitem__(
        self,
        landmark: Landmark | int,
    ) -> Point:

        return self.points[
            int(landmark)
        ]

    def visible(
        self,
        *landmarks: Landmark,
        threshold: float = 0.55,
    ) -> bool:

        return all(
            self[landmark].visibility
            >= threshold
            for landmark in landmarks
        )

    def visibility_mean(
        self,
        *landmarks: Landmark,
    ) -> float:

        if not landmarks:
            return 0.0

        return float(
            sum(
                self[landmark].visibility
                for landmark in landmarks
            )
            / len(landmarks)
        )