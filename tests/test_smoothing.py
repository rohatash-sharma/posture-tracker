from backend.landmarks import Point, PoseLandmarks
from backend.smoothing import PoseLandmarkSmoother


def pose_at(x: float) -> PoseLandmarks:
    points = [
        Point(x, 0.5, 0.0, visibility=0.9)
        for _ in range(33)
    ]
    world_points = [
        Point(x, 1.0, 0.0, visibility=0.9)
        for _ in range(33)
    ]
    return PoseLandmarks(points, world_points)


def test_pose_smoother_reduces_frame_to_frame_jitter():
    smoother = PoseLandmarkSmoother(alpha=0.25)

    smoother.update(pose_at(0.0))
    smoothed = smoother.update(pose_at(1.0))

    assert smoothed[0].x == 0.25
    assert smoothed.geometry_point(0).x == 0.25
    assert smoothed[0].visibility == 0.9


def test_pose_smoother_reset_starts_fresh_after_tracking_loss():
    smoother = PoseLandmarkSmoother(alpha=0.25)

    smoother.update(pose_at(0.0))
    smoother.reset()
    smoothed = smoother.update(pose_at(1.0))

    assert smoothed[0].x == 1.0
