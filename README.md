# AI Exercise Posture Analyzer

A Streamlit application that estimates exercise movement from a live camera or
an uploaded video. MediaPipe detects body landmarks; exercise-specific rules
calculate joint angles, track movement phases, count repetitions, and report
simple form cues.

> **Scope:** This is a local, rule-based fitness prototype—not a medical
> device, a trained coaching model, or a substitute for professional advice.
> Pose estimates can be wrong when landmarks are hidden, the camera angle is
> poor, or a movement differs from the configured thresholds.

## Features

- Live webcam analysis using WebRTC.
- Camera-free analysis by uploading MP4, MOV, AVI, or MKV videos.
- Annotated, browser-playable H.264 MP4 downloads.
- Six supported movements: Squat, Push-Up, Deadlift, Lunge, Bicep Curl, and
  Plank.
- Repetition counts for the five dynamic exercises; Plank reports a continuous
  hold time instead.
- Per-frame feedback and joint-angle metrics.
- Analysis input is resized for pose detection when necessary; video output
  retains the original dimensions (padding by one pixel if the encoder needs
  even dimensions).

## Project layout

```text
posture-tracker/
├── app.py                         # Streamlit entry point
├── run.py                         # Convenience launcher
├── frontend/                      # Streamlit UI only
│   ├── app.py                     # Navigation and page routing
│   └── pages/
│       ├── about.py
│       ├── live_analyzer.py
│       ├── personal_learning.py
│       └── video_analysis.py
├── backend/                       # Pose and exercise-analysis logic
│   ├── config/
│   │   └── settings.py            # Model location and rule thresholds
│   ├── exercises/                 # One analyzer per exercise
│   ├── pose_engine.py             # MediaPipe inference
│   ├── video_analyzer.py          # Uploaded-video processing/encoding
│   ├── live_processor.py          # WebRTC frame processing
│   ├── renderer.py                # Annotated video frame drawing
│   ├── landmarks.py
│   ├── geometry.py
│   ├── state_machine.py
│   ├── rep_counter.py
│   ├── feedback.py
│   ├── smoothing.py
│   └── audio.py
├── storage/                       # Runtime data; model weights are ignored
│   ├── models/
│   └── sessions/                  # Temporary annotated results
├── tests/                         # Unit and integration tests
├── .streamlit/config.toml
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
└── pyproject.toml
```

The app is a single Streamlit process: `frontend/` is the presentation layer,
and `backend/` is the application and analysis layer. There is intentionally no
separate HTTP API or database service. Uploaded source videos are processed in
a temporary directory; the annotated result is retained in `storage/sessions/`
for up to 24 hours so it remains available across Streamlit reruns.

Pose tracking uses MediaPipe's video mode and smooths successive landmarks
before exercise geometry is calculated. Detector input is downscaled to a
maximum dimension of 640 pixels to keep processing responsive. These measures
reduce tracking jitter and processing time; they cannot eliminate uncertainty
from occlusion, camera angle, lighting, or fast movement.

## Supported exercises

| Exercise | Main estimates | Rep/hold behavior |
|---|---|---|
| Squat | Knee angle and torso tilt | Counts a stable down-to-standing cycle |
| Push-Up | Elbow angle and shoulder/hip/ankle line | Counts a stable down-to-up cycle |
| Deadlift | Hip-hinge angle and hip/knee lockout | Counts a stable hinge-to-lockout cycle |
| Lunge | Near-side knee angle and torso tilt | Counts a stable lunge-to-standing cycle |
| Bicep Curl | Elbow angle and upper-arm tilt | Counts a stable curl-and-extension cycle |
| Plank | Shoulder/hip/ankle body-line angle | Accumulates consecutive valid hold time |

These are geometric heuristics. The angle cutoffs in
`backend/config/settings.py` are movement-phase cues for this implementation,
not universal definitions of good or bad form. In particular, landmarks cannot
reliably measure spinal curvature during a deadlift. A high form score only
means the implemented checks passed; it is not proof that a movement is safe
or injury-free.

### Personal movement trends

Live analysis can optionally save counted-repetition angle measurements in the
browser's local storage. This opt-in feature keeps up to 50 measurements per
exercise, reports a personal range and median, and compares recent reps with
the app's phase cue. Once it has enough samples, it also compares new
measurements (starting with the sixth sample) with a robust personal range
learned from earlier measurements.
Plank stores periodic body-line measurements during a hold. No pose images or
videos are saved by this feature. Use **Clear saved learning data** to remove
the browser-stored measurements. The feature is isolated in
`frontend/pages/personal_learning.py`; leaving its sidebar option off keeps
the normal analyzer workflow unchanged.

This is an adaptive statistical baseline, not a trained or clinically
validated ML model. It has no labeled examples of correct and incorrect form
from which to learn form quality. A person's historical range is only a
reference—not proof that reps were safe or technically correct—and being
outside it is not a form failure. Camera position, body proportions, occlusion,
and landmark estimation affect measured angles. The existing scores and
coaching thresholds are not modified by personal learning.

### Evidence on angle targets

The research reviewed does not establish one universally acceptable joint
angle for these exercises. ACSM recommends applying resistance-training
progression in the context of a person's goals and capacity. Reviews of squat
depth and deadlift variants discuss differences in loading, technique, and
anthropometry rather than a single correct angle. Sports-medicine measurement
guidance also distinguishes measurement error from real change. Therefore,
the values in this app are explicitly phase-detection heuristics, not
research-backed safety boundaries:

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

## Requirements

- Python 3.12
- A supported operating system for the installed MediaPipe and OpenCV wheels
- Internet access the first time the app runs, to download the pose model
- For live camera use: a working browser camera and microphone permission
  (audio capture is not used); HTTPS is required when hosted remotely
- For Docker deployment: Docker and a platform that supports WebSockets

## Run locally

From the project directory:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
streamlit run app.py
```

Alternatively, after installing dependencies:

```bash
python run.py
```

Open the local URL printed by Streamlit, normally
<http://localhost:8501>.

The first launch downloads `pose_landmarker_lite.task` to
`storage/models/`. The model is not committed to source control. Keep that
directory writable by the application user.

## Use the application

1. Choose an exercise in the sidebar.
2. Select **Live Analyzer** to use an available camera. To collect personal
   movement trends, opt in with **Learn my range on this browser** in the
   sidebar; it is off by default. The baseline appears after six measurements.
   The feature only provides advisory comparisons and does not change form
   scores or coaching thresholds. Clear browser-stored measurements with
   **Clear saved learning data**.
3. If there is no camera or it cannot be accessed, select **Video Analysis**,
   upload a saved clip, and click **Analyze Video**.
4. Wait for the frame progress indicator, review the metrics and annotated
   result, and optionally download the processed MP4.

For best estimates, record one person at a time, show the required joints
clearly, keep the full movement in frame, use good lighting, and avoid
obstructing clothing or objects. A side-on view is useful for most of these
angle checks, but no single camera view makes the estimate perfect.

## Run tests

Install the development dependencies (included in the local setup above), then
run:

```bash
pytest -q
```

The tests cover geometry, phase stability, repetition counting, all six
exercise analyzers using constructed landmarks, model download behavior,
detector input resizing, and H.264 video output.

## Configuration

Exercise angles and common visibility/state settings are centralized in
[`backend/config/settings.py`](backend/config/settings.py). Adjust them only
against representative video examples; thresholds are not universal across
body proportions, camera positions, or exercise styles.

The detector scales frames down to a maximum dimension of 640 pixels before
inference to reduce CPU work. It still processes each video frame to preserve
movement sampling. Annotated output is encoded once as H.264 using the
`ultrafast` preset.

## Docker

Build and run:

```bash
docker build -t posture-tracker .
docker run --rm -p 8501:8501 -e PORT=8501 posture-tracker
```

For a deployment, forward the platform-provided `PORT`, enable WebSockets, and
serve the site over HTTPS for camera access. The container runs as a non-root
user. Persist or mount `storage/models/` if you want to avoid downloading the
model again after a container restart.

Do not expose an unauthenticated instance to untrusted users. The app does not
provide accounts, rate limits, durable video storage, or multi-instance session
coordination.

## Data and privacy

- Pose inference and video analysis run in the application process.
- Uploaded videos are held in memory by Streamlit and processed from a
  temporary directory; the source file is removed after analysis.
- Annotated MP4 results are stored in `storage/sessions/` to survive page
  reruns, then automatically removed after 24 hours or when replaced by a new
  analysis in the same session.
- Optional personalized movement measurements are stored only in the current
  browser's local storage, are limited to 50 samples per exercise, and can be
  cleared from the Live Analyzer. They are not sent to the app server.
- The model is downloaded from Google's MediaPipe model storage on first use.
- No user account, database, permanent video archive, or cross-device profile
  is configured.
- For deployment, review the hosting provider's upload and temporary-storage
  behavior before handling sensitive video.

## Troubleshooting

### Camera is unavailable

Use **Video Analysis** to upload a saved clip. For a live camera, check browser
permission, close other camera apps, and use localhost or HTTPS.

### The first run fails while loading the model

Check outbound HTTPS access to Google's model storage and confirm that
`storage/models/` is writable. Then restart the app.

### Analysis is slow

Long or high-resolution videos still require pose inference for every frame
and H.264 encoding. Use a shorter clip, crop it to the exercise, and avoid
unnecessarily high frame rates. The detector input is already capped at a
640-pixel maximum dimension.

### Feedback seems inaccurate

Ensure the required joints are visible and the person is not too far from the
camera. Review the displayed angles and remember that this is a heuristic
prototype; it cannot judge every aspect of form or replace a qualified coach.

## License

See [`LICENSE`](LICENSE).
