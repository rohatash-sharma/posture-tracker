from __future__ import annotations

import atexit
import logging
import os
import shutil
import tempfile
import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp

from backend.config.settings import (
    MODEL_PATH,
    MODEL_URL,
    THRESHOLDS,
)

from .landmarks import PoseLandmarks
from .smoothing import PoseLandmarkSmoother


logger = logging.getLogger(__name__)


class PoseEngine:

    MAX_DETECTION_DIMENSION = 640

    def __init__(
        self,
        model_path: Path = MODEL_PATH,
    ):

        model_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not model_path.exists() or model_path.stat().st_size == 0:
            self._download_model(model_path)

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
                    vision.RunningMode.VIDEO
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

        self._last_timestamp_ms: int | None = None
        self._smoother = PoseLandmarkSmoother(
            alpha=THRESHOLDS.smoothing_alpha,
        )
        self._closed = False

        atexit.register(self.close)

    @staticmethod
    def _download_model(model_path: Path) -> None:
        logger.info("Downloading MediaPipe pose model.")
        temporary_path: Path | None = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=model_path.parent,
                prefix=f".{model_path.name}.",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                with urllib.request.urlopen(
                    MODEL_URL,
                    timeout=30,
                ) as response:
                    shutil.copyfileobj(response, temporary_file)

            if temporary_path.stat().st_size == 0:
                raise RuntimeError("The downloaded pose model is empty.")

            os.replace(temporary_path, model_path)
        except (OSError, TimeoutError) as exc:
            raise RuntimeError(
                f"Could not download the pose model from {MODEL_URL}."
            ) from exc
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def detect(
        self,
        frame_bgr,
        timestamp_ms: int | None = None,
    ) -> PoseLandmarks | None:

        if timestamp_ms is None:
            timestamp_ms = (
                0
                if self._last_timestamp_ms is None
                else self._last_timestamp_ms + 33
            )
        elif timestamp_ms < 0:
            raise ValueError("Video timestamps cannot be negative.")
        if (
            self._last_timestamp_ms is not None
            and timestamp_ms <= self._last_timestamp_ms
        ):
            raise ValueError(
                "Video timestamps must increase for each frame."
            )
        self._last_timestamp_ms = timestamp_ms

        height, width = frame_bgr.shape[:2]
        scale = min(
            1.0,
            self.MAX_DETECTION_DIMENSION / max(height, width),
        )
        if scale < 1.0:
            frame_bgr = cv2.resize(
                frame_bgr,
                (
                    round(width * scale),
                    round(height * scale),
                ),
                interpolation=cv2.INTER_AREA,
            )

        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb,
        )

        result = self.landmarker.detect_for_video(
            image,
            timestamp_ms,
        )

        if not result.pose_landmarks:
            self._smoother.reset()
            return None

        pose = PoseLandmarks.from_mediapipe(
            result.pose_landmarks[0],
            (
                result.pose_world_landmarks[0]
                if result.pose_world_landmarks
                else None
            ),
        )
        return self._smoother.update(pose)

    def close(self):

        if getattr(self, "_closed", True):
            return

        self.landmarker.close()
        self._closed = True
        atexit.unregister(self.close)

    def __enter__(self):

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):

        self.close()