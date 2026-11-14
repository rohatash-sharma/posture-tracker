from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

STORAGE_DIR = ROOT / "storage"
MODEL_DIR = STORAGE_DIR / "models"
SESSIONS_DIR = STORAGE_DIR / "sessions"

MODEL_PATH = MODEL_DIR / "pose_landmarker_lite.task"

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_lite/float16/1/"
    "pose_landmarker_lite.task"
)


@dataclass(frozen=True)
class ExerciseThresholds:
    """
    Tunable angle and visibility limits used by the pose heuristics.
    """

    # Squat
    squat_down_knee: float = 100.0
    squat_up_knee: float = 165.0
    squat_max_torso_tilt: float = 45.0

    # Push-up
    pushup_down_elbow: float = 110.0
    pushup_up_elbow: float = 160.0
    pushup_body_min: float = 165.0

    # Lunge
    lunge_down_knee: float = 105.0
    lunge_up_knee: float = 160.0
    lunge_max_torso_tilt: float = 45.0

    # Bicep curl
    curl_down_elbow: float = 75.0
    curl_up_elbow: float = 155.0
    curl_max_upper_arm_tilt: float = 40.0

    # Plank
    plank_body_min: float = 160.0

    # Deadlift
    deadlift_down_hip: float = 120.0
    deadlift_lockout_hip: float = 165.0

    # General
    min_visibility: float = 0.55
    smoothing_alpha: float = 0.35
    stable_frames: int = 3


THRESHOLDS = ExerciseThresholds()