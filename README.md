# AI Exercise Posture Analyzer

A Streamlit application for estimating exercise movement and providing
rule-based form cues from a live camera or a recorded video. MediaPipe Pose
detects body landmarks; exercise-specific geometry and state tracking estimate
movement phases, repetitions, hold time, and basic form feedback.

> **Important:** This project is a fitness-analysis prototype, not a medical
> device, a clinically validated coaching system, or a substitute for
> professional instruction. Pose estimates and form cues can be wrong,
> especially when landmarks are obscured or the camera view is unsuitable.
> Stop if you feel pain.

## What it does

- **Live analysis:** use a camera to view the current phase, repetition or
  plank hold time, form score, measurements, and feedback. Optional browser
  speech can read feedback aloud.
- **Recorded-video analysis:** upload an MP4, MOV, AVI, or MKV clip without
  using a camera. Review the summary and annotated H.264 MP4.
- **Timestamped correction report:** see the distinct feedback cues recorded
  across the video, with timestamps, frame numbers, levels, and cue scores.
  Read the report in the app or download it as a text file.
- **Six exercises:** Squat, Push-Up, Deadlift, Lunge, Bicep Curl, and Plank.
- **Optional personal movement trends:** compare measurements with a baseline
  stored in the current browser. This feature is off by default.

The correction report records a cue when its feedback level or message
changes, rather than repeating the same cue on every frame. When no person is
detected, it records a prompt to move fully into the camera frame. These are
the analyzer's observations—not a complete transcript or a guarantee that a
movement was performed safely.

## Supported exercises

| Exercise | Main estimates | Rep/hold behavior |
|---|---|---|
| Squat | Knee angle and estimated torso tilt | Counts a stable down-to-standing cycle |
| Push-Up | Elbow angle and shoulder/hip/ankle alignment | Counts a stable down-to-up cycle |
| Deadlift | Hip-hinge angle and standing lockout | Counts a stable hinge-to-lockout cycle |
| Lunge | Near-side knee angle and estimated torso tilt | Counts a stable lunge-to-standing cycle |
| Bicep Curl | Elbow angle and upper-arm tilt | Counts a stable curl-and-extension cycle |
| Plank | Shoulder/hip/ankle body-line angle | Accumulates consecutive valid hold time |

These estimates use geometric heuristics. The angle thresholds in
[`backend/config/settings.py`](backend/config/settings.py) are cues for
movement-phase detection in this implementation—not universal technique
standards or research-backed safety limits. A high score only reflects the
checks implemented by the app. In particular, 2D/3D pose landmarks cannot
reliably assess spinal curvature during a deadlift.

## Get started

### Requirements

- Python 3.12
- An operating system supported by the installed MediaPipe and OpenCV wheels
- Internet access on first use if the pose model is not already present
- For live camera use: camera permission and a supported browser; remote
  deployments require HTTPS for camera access

### Install and run

From the project directory:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
streamlit run app.py
```

Open the URL printed by Streamlit, usually <http://localhost:8501>. After
installing dependencies, you can also start the application with:

```bash
python run.py
```

On first use, the application downloads
`pose_landmarker_lite.task` to `storage/models/`. The model is not committed to
source control, so the application needs write access to that directory.

## Use the application

1. Choose an exercise in the sidebar.
2. Select **Live Analyzer** to use a camera. Grant camera access when prompted.
   Enable voice feedback in the sidebar and use the on-page control to enable
   speech in the browser.
3. Or select **Video Analysis**, upload a clip, and click **Analyze Video**.
   This path does not require camera access. Wait for frame processing to
   complete.
4. Review the summary, observed angle ranges, and timestamped correction
   report. Download the annotated video or the correction report text as
   needed.

For more reliable estimates, record one person at a time, keep the full body
and required joints visible, use good lighting, and avoid obstructing clothing
or objects. A side-on view is useful for many of the configured angle checks,
but no camera angle guarantees accurate measurements.

## Personal movement trends

The **Learn my range on this browser** option is off by default. When enabled,
the app stores up to 50 measurements per exercise in that browser's local
storage. It can show a personal range and median, and starts comparing new
measurements with a robust personal range after enough samples (starting with
the sixth measurement). Plank records periodic body-line measurements during
a hold. Use **Clear saved learning data** in the Live Analyzer to remove these
browser-stored measurements.

This feature is a statistical reference, not a trained model. It does not
verify that past movements were correct or safe, and it does not change the
app's form scores or coaching thresholds. Measurements can vary with camera
position, body proportions, occlusion, and pose-estimation error.

## How it works

The application runs as one Streamlit process. The `frontend/` package renders
the interface; `backend/` handles pose estimation and exercise analysis.
There is no separate API server or database.

For video analysis, the application processes uploaded frames, smooths pose
landmarks, calculates exercise-specific measurements, and encodes an annotated
H.264 MP4. Detector input is downscaled to a maximum dimension of 640 pixels
to reduce processing work; output retains the original dimensions, with
one-pixel padding if an even frame size is required by the encoder. The
correction report preserves timestamps for changes in feedback as the clip is
processed.

```text
posture-tracker/
├── app.py                         # Streamlit entry point
├── run.py                         # Convenience launcher
├── frontend/
│   ├── app.py                     # Navigation and page routing
│   └── pages/                     # Live, video, learning, and about views
├── backend/
│   ├── config/settings.py         # Model location and rule thresholds
│   ├── exercises/                 # Exercise-specific analyzers
│   ├── pose_engine.py             # MediaPipe inference
│   ├── video_analyzer.py          # Uploaded-video processing and summary
│   ├── live_processor.py          # Live frame processing
│   ├── renderer.py                # Annotated frame rendering
│   └── ...                         # Geometry, feedback, smoothing, state
├── storage/
│   ├── models/                    # Downloaded pose model
│   └── sessions/                  # Temporary annotated results
└── tests/                         # Unit and integration tests
```

## Tests

Install the development dependencies as shown above, then run:

```bash
pytest -q
```

The test suite covers geometry, movement-state stability, repetition counting,
exercise analyzers using constructed landmarks, pose-model behavior, detector
input resizing, and annotated H.264 video output.

## Configuration and limitations

Exercise thresholds and shared visibility/state settings are centralized in
[`backend/config/settings.py`](backend/config/settings.py). They are
implementation parameters, not universal targets. Adjustments should be
evaluated against representative videos and should not be interpreted as
clinical or safety guidance.

MediaPipe pose estimation is sensitive to camera position, lighting,
occlusion, body orientation, and fast movement. The app does not use labeled
examples to learn what correct form looks like, and its scores are not
biomechanical assessments. No automated output can guarantee that an exercise
is safe or performed correctly.

## Docker

Build and run:

```bash
docker build -t posture-tracker .
docker run --rm -p 8501:8501 -e PORT=8501 posture-tracker
```

For deployment, forward the platform-provided `PORT`, enable WebSockets, and
serve over HTTPS for camera access. The container runs as a non-root user.
Persist or mount `storage/models/` to avoid downloading the model again after
a container restart.

Do not expose an unauthenticated instance to untrusted users. The application
does not provide accounts, rate limits, durable video storage, or coordination
between multiple instances.

## Data and privacy

- Pose inference and video analysis run in the application process.
- Uploaded source videos are held by Streamlit and processed from a temporary
  directory; the temporary source copy is removed after analysis.
- Annotated MP4 files are kept in `storage/sessions/` so results survive page
  reruns. They are removed after 24 hours or when replaced by a new result in
  the same session.
- Optional personal measurements are stored in the current browser's local
  storage, not sent as a personal profile to the application server. They can
  be cleared from the Live Analyzer.
- The pose model is downloaded from Google's MediaPipe model storage if it is
  not already available locally.
- No user account, database, permanent video archive, or cross-device profile
  is configured. For hosted deployments, review the provider's upload and
  temporary-storage behavior before handling sensitive video.

## References and context

There is no single universally accepted joint angle for the movements
estimated here. The following references provide context on resistance
training, squat/deadlift variation, and measurement error; they do not
validate this application's thresholds:

- American College of Sports Medicine, *Progression Models in Resistance
  Training for Healthy Adults*,
  [doi:10.1249/MSS.0b013e3181915670](https://doi.org/10.1249/MSS.0b013e3181915670).
- Hartmann et al., *Analysis of the load on the knee joint and vertebral
  column with changes in squatting depth and weight load*,
  [doi:10.1007/s40279-013-0073-6](https://doi.org/10.1007/s40279-013-0073-6).
- Cholewa et al., *Anthropometrical Determinants of Deadlift Variant
  Performance*, [PubMed](https://pubmed.ncbi.nlm.nih.gov/31427866/).
- Atkinson & Nevill, *Statistical methods for assessing measurement error
  (reliability) in variables relevant to sports medicine*,
  [doi:10.2165/00007256-199826040-00002](https://doi.org/10.2165/00007256-199826040-00002).
