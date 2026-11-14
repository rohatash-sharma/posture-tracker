from __future__ import annotations

import cv2
import numpy as np
import pytest
import av

import backend.video_analyzer as video_analyzer


class NoPoseEngine:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def detect(self, _frame, timestamp_ms=None):
        return None


def test_analyze_video_returns_browser_playable_mp4(
    tmp_path,
    monkeypatch,
):
    source_path = tmp_path / "input.mp4"
    output_path = tmp_path / "annotated.mp4"
    writer = cv2.VideoWriter(
        str(source_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        10,
        (64, 48),
    )
    if not writer.isOpened():
        pytest.skip("OpenCV cannot encode the test video in this environment.")

    for _ in range(3):
        writer.write(np.zeros((48, 64, 3), dtype=np.uint8))
    writer.release()

    monkeypatch.setattr(video_analyzer, "PoseEngine", NoPoseEngine)

    progress = []
    summary = video_analyzer.analyze_video(
        source_path,
        output_path,
        "Squat",
        progress_callback=lambda current, total: progress.append(
            (current, total)
        ),
    )

    assert summary.frames == 3
    assert summary.duration_seconds == pytest.approx(0.3)
    assert progress[-1] == (3, 3)
    assert output_path.is_file()
    with av.open(str(output_path)) as container:
        stream = container.streams.video[0]
        assert stream.codec_context.name == "h264"
        assert (stream.width, stream.height) == (64, 48)
        assert sum(1 for _ in container.decode(stream)) == 3


def test_analyze_video_rejects_unreadable_input(tmp_path):
    with pytest.raises(ValueError, match="Could not open"):
        video_analyzer.analyze_video(
            tmp_path / "missing.mp4",
            tmp_path / "output.mp4",
            "Squat",
        )
