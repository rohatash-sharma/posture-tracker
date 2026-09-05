from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ASSETS_DIR = ROOT / "assets"
SESSIONS_DIR = ROOT / "sessions"

MODEL_PATH = ASSETS_DIR / "pose_landmarker_lite.task"

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_lite/float16/1/"
    "pose_landmarker_lite.task"
)


@dataclass(frozen=True)
class ExerciseThresholds:
    """
    Thresholds used by the exercise rules.

    The original project specification proposes:
    - Squat: knee around/below 90 degrees for the down state
    - Push-up: elbow around 90 degrees for the down state
    - Push-up: body line close to 180 degrees
    - Deadlift: neutral back and hip/knee extension
    """

    # Squat
    squat_down_knee: float = 100.0
    squat_up_knee: float = 165.0
    squat_back_min: float = 155.0

    # Push-up
    pushup_down_elbow: float = 110.0
    pushup_up_elbow: float = 160.0
    pushup_body_min: float = 165.0

    # Deadlift
    deadlift_down_knee: float = 145.0
    deadlift_lockout_hip: float = 165.0
    deadlift_back_min: float = 160.0

    # General
    min_visibility: float = 0.55
    smoothing_alpha: float = 0.35
    stable_frames: int = 3


THRESHOLDS = ExerciseThresholds()