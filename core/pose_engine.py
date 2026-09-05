from __future__ import annotations

import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp

from config.settings import (
    MODEL_PATH,
    MODEL_URL,
)

from .landmarks import PoseLandmarks


class PoseEngine:

    def __init__(
        self,
        model_path: Path = MODEL_PATH,
    ):

        model_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not model_path.exists():

            print(
                "Downloading MediaPipe "
                "pose model..."
            )

            urllib.request.urlretrieve(
                MODEL_URL,
                model_path,
            )

        base_options = mp.tasks.BaseOptions

        vision = (
            mp.tasks.vision
        )

        options = (
            vision.PoseLandmarkerOptions(
                base_options=(
                    base_options(
                        model_asset_path=str(
                            model_path
                        )
                    )
                ),
                running_mode=(
                    vision.RunningMode.IMAGE
                ),
                num_poses=1,
                min_pose_detection_confidence=0.5,
                min_pose_presence_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        )

        self.landmarker = (
            vision.PoseLandmarker
            .create_from_options(options)
        )

    def detect(
        self,
        frame_bgr,
    ) -> PoseLandmarks | None:

        rgb = cv2.cvtColor(
            frame_bgr,
            cv2.COLOR_BGR2RGB,
        )

        image = mp.Image(
            image_format=(
                mp.ImageFormat.SRGB
            ),
            data=rgb,
        )

        result = (
            self.landmarker.detect(
                image
            )
        )

        if not result.pose_landmarks:
            return None

        return PoseLandmarks.from_mediapipe(
            result.pose_landmarks[0]
        )

    def close(self):

        self.landmarker.close()

    def __enter__(self):

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):

        self.close()