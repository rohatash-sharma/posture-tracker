from __future__ import annotations

import io
from types import SimpleNamespace

import numpy as np
import pytest

import backend.pose_engine as pose_engine


def test_model_download_replaces_file_after_success(
    tmp_path,
    monkeypatch,
):
    model_path = tmp_path / "pose.task"
    model_path.write_bytes(b"old model")
    response = io.BytesIO(b"complete model")
    monkeypatch.setattr(
        pose_engine.urllib.request,
        "urlopen",
        lambda *_args, **_kwargs: response,
    )

    pose_engine.PoseEngine._download_model(model_path)

    assert model_path.read_bytes() == b"complete model"
    assert list(tmp_path.iterdir()) == [model_path]


def test_empty_model_download_does_not_replace_existing_file(
    tmp_path,
    monkeypatch,
):
    model_path = tmp_path / "pose.task"
    model_path.write_bytes(b"existing model")
    monkeypatch.setattr(
        pose_engine.urllib.request,
        "urlopen",
        lambda *_args, **_kwargs: io.BytesIO(),
    )

    with pytest.raises(RuntimeError, match="empty"):
        pose_engine.PoseEngine._download_model(model_path)

    assert model_path.read_bytes() == b"existing model"
    assert list(tmp_path.iterdir()) == [model_path]


def test_pose_detection_downscales_input_and_keeps_world_landmarks():
    image_points = [
        SimpleNamespace(
            x=0.5,
            y=0.5,
            z=0.0,
            visibility=1.0,
            presence=1.0,
        )
        for _ in range(33)
    ]
    world_points = [
        SimpleNamespace(
            x=float(index),
            y=1.0,
            z=0.0,
            visibility=1.0,
            presence=1.0,
        )
        for index in range(33)
    ]

    class FakeLandmarker:
        image_shape = None

        def detect_for_video(self, image, timestamp_ms):
            self.image_shape = image.numpy_view().shape
            self.timestamp_ms = timestamp_ms
            return SimpleNamespace(
                pose_landmarks=[image_points],
                pose_world_landmarks=[world_points],
            )

    engine = pose_engine.PoseEngine.__new__(
        pose_engine.PoseEngine
    )
    engine.landmarker = FakeLandmarker()
    engine._last_timestamp_ms = None
    engine._smoother = pose_engine.PoseLandmarkSmoother()

    pose = engine.detect(
        np.zeros((1080, 1920, 3), dtype=np.uint8)
    )

    assert engine.landmarker.image_shape == (360, 640, 3)
    assert engine.landmarker.timestamp_ms == 0
    assert pose is not None
    assert pose[0].x == 0.5
    assert pose.geometry_point(0).x == 0.0
    assert pose.geometry_point(32).x == 32.0


@pytest.mark.parametrize(
    ("last_timestamp_ms", "timestamp_ms"),
    [(None, -1), (100, 99), (100, 100)],
)
def test_pose_detection_rejects_invalid_timestamps(
    last_timestamp_ms,
    timestamp_ms,
):
    engine = pose_engine.PoseEngine.__new__(
        pose_engine.PoseEngine
    )
    engine._last_timestamp_ms = last_timestamp_ms
    engine._smoother = pose_engine.PoseLandmarkSmoother()

    with pytest.raises(ValueError, match="timestamp"):
        engine.detect(
            np.zeros((48, 64, 3), dtype=np.uint8),
            timestamp_ms=timestamp_ms,
        )
