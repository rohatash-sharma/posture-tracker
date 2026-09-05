# 🏋️ AI Exercise Posture Analyzer

A computer-vision based exercise posture analysis system that uses a normal webcam or an uploaded exercise video to estimate human body pose, calculate joint angles, evaluate exercise form, track exercise phases, count repetitions, and provide feedback.

This project is based on the supplied technical blueprint for an **AI/ML-Based Exercise Posture Analyzer**. The blueprint describes a pipeline of video input → pose estimation → 33 body landmarks → angle calculation → form validation → exercise state machine → repetition counter → dashboard/audio feedback.

> **Current implementation:** MediaPipe Pose + OpenCV + Python + Streamlit + `streamlit-webrtc` with deterministic exercise rules.
>
> **Current exercises:** Squat, Push-Up, Deadlift.

---

## 📑 Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. Problem Statement](#2-problem-statement)
- [3. Proposed Solution](#3-proposed-solution)
- [4. Project Objectives](#4-project-objectives)
- [5. Current Features](#5-current-features)
- [6. How the System Works](#6-how-the-system-works)
- [7. System Architecture](#7-system-architecture)
- [8. Technology Stack](#8-technology-stack)
- [9. Why These Technologies?](#9-why-these-technologies)
- [10. Project Structure](#10-project-structure)
- [11. File-by-File Explanation](#11-file-by-file-explanation)
- [12. Requirements](#12-requirements)
- [13. Installation on Linux](#13-installation-on-linux)
- [14. Open the Project in VS Code](#14-open-the-project-in-vs-code)
- [15. Create the Python Virtual Environment](#15-create-the-python-virtual-environment)
- [16. Install Dependencies](#16-install-dependencies)
- [17. Run the Tests](#17-run-the-tests)
- [18. Run the Application](#18-run-the-application)
- [19. Live Analyzer](#19-live-analyzer)
- [20. Recorded Video Analysis](#20-recorded-video-analysis)
- [21. Squat Analysis](#21-squat-analysis)
- [22. Push-Up Analysis](#22-push-up-analysis)
- [23. Deadlift Analysis](#23-deadlift-analysis)
- [24. Pose Landmarks](#24-pose-landmarks)
- [25. Joint Angle Calculation](#25-joint-angle-calculation)
- [26. Form Validation](#26-form-validation)
- [27. Exercise State Machine](#27-exercise-state-machine)
- [28. Repetition Counting](#28-repetition-counting)
- [29. Form Score](#29-form-score)
- [30. Configuration and Thresholds](#30-configuration-and-thresholds)
- [31. Model File](#31-model-file)
- [32. Troubleshooting](#32-troubleshooting)
- [33. Git and GitHub Workflow](#33-git-and-github-workflow)
- [34. Presentation Explanation](#34-presentation-explanation)
- [35. Demo Checklist](#35-demo-checklist)
- [36. Advantages](#36-advantages)
- [37. Limitations](#37-limitations)
- [38. Future Improvements](#38-future-improvements)
- [39. Future Scope](#39-future-scope)
- [40. Privacy Considerations](#40-privacy-considerations)
- [41. Disclaimer](#41-disclaimer)
- [42. License](#42-license)
- [43. Author](#43-author)

---

# 1. Project Overview

The **AI Exercise Posture Analyzer** is a real-time computer-vision application for analyzing exercise movements through a camera.

Instead of requiring wearable sensors, the application uses a standard camera and estimates body landmarks from the video.

The general pipeline is:

```text
Camera / Uploaded Video
          ↓
     Video Frames
          ↓
  MediaPipe Pose Landmarker
          ↓
    33 Body Landmarks
          ↓
   Joint Angle Calculation
          ↓
   Exercise-Specific Rules
          ↓
     Form Validation
          ↓
     State Machine
          ↓
   Repetition Counter
          ↓
 Feedback + Dashboard + Audio
```

The supplied project blueprint describes this same high-level processing flow and identifies angle calculation, form validation, state tracking, repetition counting, and user feedback as the central parts of the system.

---

# 2. Problem Statement

Improper exercise posture can reduce the effectiveness of a workout and may increase the risk of musculoskeletal injury.

Traditional correction generally depends on a personal trainer or another person watching the exercise and providing feedback.

The goal of this project is to explore whether computer vision can automate part of that process using a standard camera.

### Example problem

A person performs a squat:

```text
Correct movement:

Standing
   ↓
Controlled descent
   ↓
Adequate squat depth
   ↓
Controlled ascent
   ↓
Standing
```

The system attempts to measure this movement using body landmarks and joint angles instead of relying on manual observation.

---

# 3. Proposed Solution

The proposed solution uses pose estimation to convert a video frame into a structured representation of the human body.

The system then evaluates the relationships between important landmarks.

For example:

```text
Hip → Knee → Ankle
```

can be used to calculate a knee angle.

Similarly:

```text
Shoulder → Elbow → Wrist
```

can be used to calculate an elbow angle.

These values are passed into exercise-specific rules that determine movement phase and form quality.

---

# 4. Project Objectives

The project aims to:

1. Detect human body landmarks from normal video.
2. Calculate important joint and body-alignment angles.
3. Analyze exercise-specific movement patterns.
4. Validate form using configurable rules.
5. Track exercise phases using a state machine.
6. Count completed repetitions.
7. Provide real-time visual feedback.
8. Provide a simple audio cue when a repetition is completed.
9. Support both live webcam analysis and recorded-video analysis.
10. Keep the system modular so more exercises and different pose models can be added later.

---

# 5. Current Features

## ✅ Live webcam analysis

The browser camera can be processed frame-by-frame.

## ✅ Recorded video analysis

The application can process uploaded exercise videos.

## ✅ 33-point pose representation

The internal landmark layer models 33 body landmarks.

## ✅ Joint-angle calculations

The system calculates values such as:

- Knee angle
- Elbow angle
- Hip angle
- Back/body alignment angle

## ✅ Exercise-specific analyzers

Current analyzers:

- Squat
- Push-Up
- Deadlift

## ✅ State machine

The movement can be represented as:

```text
UNKNOWN
   ↓
UP
   ↓
TRANSITION
   ↓
DOWN
```

or the reverse depending on the exercise movement.

## ✅ Repetition counter

A repetition is counted only after the required phase sequence has been completed.

## ✅ Form feedback

The analyzer provides messages such as:

```text
Good squat form.
Go a little deeper.
Keep your back more upright.

Good push-up form.
Keep your body in a straighter line.

Strong lockout.
Avoid rounding your back.
```

## ✅ Form score

The current score is based on whether important rule conditions are satisfied.

## ✅ Pose visualization

The analyzed video can display a skeleton overlay and exercise metrics.

## ✅ Audio cue

A short beep can be triggered when a repetition is completed.

---

# 6. How the System Works

The complete processing chain is:

```text
STEP 1
Camera or video provides a frame

        ↓

STEP 2
MediaPipe estimates the human pose

        ↓

STEP 3
33 landmarks are converted into the project's internal format

        ↓

STEP 4
Important joint angles are calculated

        ↓

STEP 5
Exercise-specific form rules are evaluated

        ↓

STEP 6
The state machine determines the movement phase

        ↓

STEP 7
The repetition counter checks whether a valid repetition is complete

        ↓

STEP 8
The result is rendered on the video and shown in the dashboard

        ↓

STEP 9
An audio cue can be played after a completed repetition
```

This separation is intentional: the pose engine does not contain squat rules, and the squat analyzer does not need to know how the camera works.

---

# 7. System Architecture

```text
                    ┌─────────────────────┐
                    │ Camera / Video      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ OpenCV / WebRTC     │
                    │ Frame Input         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ MediaPipe Pose      │
                    │ Landmarker          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ 33 Landmarks        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Geometry / Angles   │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
          ┌──────────┐   ┌──────────┐   ┌───────────┐
          │  Squat   │   │ Push-Up  │   │ Deadlift  │
          └────┬─────┘   └────┬─────┘   └─────┬─────┘
               └──────────────┼──────────────┘
                              ▼
                    ┌─────────────────────┐
                    │ Form Validation     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ State Machine       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Repetition Counter  │
                    └──────────┬──────────┘
                               │
                       ┌───────┴────────┐
                       ▼                ▼
               ┌─────────────┐   ┌─────────────┐
               │ Dashboard   │   │ Audio Cue   │
               └─────────────┘   └─────────────┘
```

---

# 8. Technology Stack

| Technology | Role |
|---|---|
| Python 3 | Main programming language |
| MediaPipe | Human pose estimation |
| OpenCV | Video and frame processing |
| NumPy | Vector and mathematical calculations |
| Streamlit | Web interface |
| streamlit-webrtc | Live browser video processing |
| PyAV | Video frame conversion |
| Pytest | Automated testing |

---

# 9. Why These Technologies?

## Python

Python is used because it has a large ecosystem for computer vision, numerical computing and rapid application development.

## MediaPipe

The project needs a pose-estimation layer capable of locating important body landmarks from ordinary video. The chosen MediaPipe Pose Landmarker API provides the pose landmarks required by the exercise logic.

## OpenCV

OpenCV handles image/frame processing and video input/output.

## NumPy

Angles and other geometric calculations use NumPy vectors and mathematical operations.

## Streamlit

Streamlit provides a quick way to build a browser-based dashboard around the analysis engine.

## streamlit-webrtc

A normal Streamlit file/image input is not sufficient for continuous webcam frame processing. `streamlit-webrtc` is used so the application can receive and process video frames continuously.

---

# 10. Project Structure

```text
posture-tracker/
│
├── app.py
├── run.py
├── requirements.txt
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
│
├── .streamlit/
│   └── config.toml
│
├── assets/
│   └── pose_landmarker_lite.task
│
├── sessions/
│
├── config/
│   ├── __init__.py
│   └── settings.py
│
├── core/
│   ├── __init__.py
│   ├── audio.py
│   ├── feedback.py
│   ├── geometry.py
│   ├── landmarks.py
│   ├── live_processor.py
│   ├── pose_engine.py
│   ├── renderer.py
│   ├── rep_counter.py
│   ├── smoothing.py
│   ├── state_machine.py
│   ├── video_analyzer.py
│   │
│   └── exercises/
│       ├── __init__.py
│       ├── base.py
│       ├── common.py
│       ├── deadlift.py
│       ├── factory.py
│       ├── pushup.py
│       └── squat.py
│
└── tests/
    ├── test_exercises.py
    ├── test_geometry.py
    └── test_state_and_reps.py
```

---

# 11. File-by-File Explanation

## `app.py`

Main Streamlit application.

Provides:

- Live Analyzer
- Video Analysis
- About page
- Exercise selection
- Dashboard metrics

## `run.py`

Convenience launcher:

```bash
python run.py
```

## `requirements.txt`

Contains Python dependencies required by the project.

## `pyproject.toml`

Contains project/build configuration and Pytest settings.

## `config/settings.py`

Stores important configuration and exercise thresholds.

## `core/geometry.py`

Contains mathematical operations such as joint-angle calculations.

## `core/landmarks.py`

Defines the project's 33-landmark representation.

## `core/pose_engine.py`

Loads MediaPipe and performs pose detection.

## `core/state_machine.py`

Tracks movement phases such as `UP`, `DOWN`, `TRANSITION`, and `UNKNOWN`.

## `core/rep_counter.py`

Counts completed repetitions after a valid phase sequence.

## `core/feedback.py`

Defines feedback messages, severity levels and score calculation.

## `core/audio.py`

Generates the short WAV beep used for repetition feedback.

## `core/renderer.py`

Draws the pose skeleton and analysis information on the video frame.

## `core/live_processor.py`

Connects the live browser video stream to the pose/exercise analysis pipeline.

## `core/video_analyzer.py`

Processes uploaded videos frame-by-frame and creates annotated output.

## `core/exercises/`

Contains the exercise-specific logic.

```text
squat.py
pushup.py
deadlift.py
```

## `core/exercises/factory.py`

Creates the correct analyzer based on the selected exercise.

## `tests/`

Contains automated tests for geometry, states, repetition counting and exercise module setup.

---

# 12. Requirements

Recommended environment:

- Ubuntu/Linux
- Python 3
- Git
- VS Code
- Working webcam for live mode
- Internet connection for initial Python package installation and the pose model download

The project can also analyze prerecorded videos without a webcam.

---

# 13. Installation on Linux

Open a terminal.

## Step 1 — Update package information

```bash
sudo apt update
```

## Step 2 — Install Git and Python tools

```bash
sudo apt install -y git python3 python3-pip python3-venv
```

Check the installation:

```bash
git --version
python3 --version
pip3 --version
```

---

# 14. Open the Project in VS Code

Clone the repository:

```bash
cd ~
git clone https://github.com/rohatash-sharma/posture-tracker.git
```

Enter the project:

```bash
cd ~/posture-tracker
```

Open VS Code:

```bash
code .
```

If the `code` command is not available, open VS Code manually and choose:

```text
File → Open Folder → posture-tracker
```

---

# 15. Create the Python Virtual Environment

Inside the project directory:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

You should now see something similar to:

```text
(.venv) user@ubuntu:~/posture-tracker$
```

Every time you open a new terminal for this project, activate the environment again:

```bash
cd ~/posture-tracker
source .venv/bin/activate
```

---

# 16. Install Dependencies

Upgrade the package tools:

```bash
python -m pip install --upgrade pip setuptools wheel
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Verify that important packages are installed:

```bash
pip list
```

Look for packages such as:

```text
mediapipe
opencv-python-headless
streamlit
streamlit-webrtc
numpy
av
pytest
```

---

# 17. Run the Tests

Before opening the application, run:

```bash
pytest -q
```

The tests cover the main low-level building blocks, including:

- Angle calculation
- State transitions
- Repetition counting
- Exercise factory registration
- Landmark representation

If all tests pass, the basic software components are working.

You can also run a Python syntax check:

```bash
python -m compileall .
```

---

# 18. Run the Application

Start Streamlit:

```bash
streamlit run app.py
```

Or use:

```bash
python run.py
```

Streamlit will normally print a local URL similar to:

```text
Local URL: http://localhost:8501
```

Open that URL in your browser.

---

# 19. Live Analyzer

In the browser, select:

```text
Mode → Live Analyzer
```

Then select:

```text
Exercise → Squat
```

or:

```text
Exercise → Push-Up
```

or:

```text
Exercise → Deadlift
```

Allow the browser to access the webcam.

### Recommended camera setup

For the current rule-based analyzers, a side view is generally the most useful setup.

Keep the complete body visible:

```text
       HEAD
        ●
        │
     SHOULDER
        ●
        │
       HIP
        ●
        │
      KNEE
        ●
        │
      ANKLE
        ●
```

Try to avoid:

- Body parts outside the frame
- Very dark lighting
- Strong occlusion
- Excessive camera movement
- Very low-resolution video

---

# 20. Recorded Video Analysis

Select:

```text
Mode → Video Analysis
```

Upload a supported video:

```text
.mp4
.mov
.avi
.mkv
```

Choose the exercise and click:

```text
Analyze Video
```

The application processes the video frame-by-frame.

The result includes metrics such as:

```text
Repetitions
Average Form Score
Duration
Valid Frames
```

An annotated video can also be downloaded.

---

# 21. Squat Analysis

The squat analyzer primarily uses:

```text
Hip → Knee → Ankle
```

for knee-angle analysis and:

```text
Shoulder → Hip → Knee
```

for a simple back/alignment check.

### Simplified movement model

```text
              UP
               │
               ▼
        ┌─────────────┐
        │   Standing  │
        └──────┬──────┘
               │
               ▼
          Knee bends
               │
               ▼
             DOWN
               │
               ▼
          Knee extends
               │
               ▼
              UP
               │
               ▼
          1 repetition
```

The project blueprint proposes a deep-squat down state around a 90° knee angle with tolerance and concurrent back-alignment checking.

The implementation uses configurable practical thresholds in `config/settings.py` rather than treating a single number as a universal biomechanical standard.

---

# 22. Push-Up Analysis

The push-up analyzer primarily uses:

```text
Shoulder → Elbow → Wrist
```

for elbow angle and:

```text
Shoulder → Hip → Ankle
```

for body-line alignment.

### Simplified movement model

```text
             UP
              │
              ▼
        Elbows extended
              │
              ▼
        Elbows bend
              │
              ▼
             DOWN
              │
              ▼
        Elbows extend
              │
              ▼
             UP
              │
              ▼
        1 repetition
```

The blueprint describes the push-up down phase using an approximately 90° elbow target and a body alignment close to 180°.

---

# 23. Deadlift Analysis

The deadlift analyzer monitors:

```text
Knee angle
Hip angle
Back angle
```

The general movement is represented as:

```text
Starting position
       ↓
     Hinge
       ↓
      Pull
       ↓
    Lockout
       ↓
     Lower
       ↓
     Repeat
```

The blueprint emphasizes monitoring the back to reduce rounding and tracking the movement toward knee/hip extension and lockout.

---

# 24. Pose Landmarks

The project internally represents 33 body landmarks.

Important landmarks for the current exercise logic include:

```text
Nose
Shoulders
Elbows
Wrists
Hips
Knees
Ankles
```

A simplified skeleton is:

```text
             NOSE
               ●
              / \
             /   \
        SHOULDER SHOULDER
            ●       ●
            │       │
         ELBOW    ELBOW
            ●       ●
            │       │
         WRIST    WRIST
            │       │
            │       │
           HIP     HIP
            ●       ●
            │       │
          KNEE    KNEE
            ●       ●
            │       │
         ANKLE    ANKLE
            ●       ●
```

Each landmark contains positional information and visibility information.

Conceptually:

```text
x = horizontal position
y = vertical position
z = depth estimate
```

---

# 25. Joint Angle Calculation

Suppose we have three points:

```text
A
 \
  \
   B
    \
     \
      C
```

`B` is the vertex.

The application calculates the angle `ABC` using vector mathematics.

For a knee:

```text
HIP
  \
   \
    KNEE
        \
         \
         ANKLE
```

the code uses:

```python
angle_3d(hip, knee, ankle)
```

Examples:

```text
180° ≈ straight line
90°  ≈ right angle
```

These measurements are then compared with exercise-specific thresholds.

---

# 26. Form Validation

Form validation is performed using deterministic rules.

Example:

```text
Knee angle is acceptable
        AND
Back angle is acceptable
        ↓
     Valid form
```

If an important condition fails, the analyzer can produce a warning.

Examples:

```text
Keep your back more upright.
Go a little deeper.
Keep your body in a straighter line.
Avoid rounding your back.
```

This is not a learned medical or biomechanical judgment model. It is a configurable rule-based prototype.

---

# 27. Exercise State Machine

The application does not decide repetitions from one isolated frame.

It uses movement phases.

The phases are:

```text
UNKNOWN
UP
DOWN
TRANSITION
```

A simplified example:

```text
           UP
            │
            ▼
      TRANSITION
            │
            ▼
          DOWN
            │
            ▼
      TRANSITION
            │
            ▼
           UP
```

The state machine also requires a number of stable frames before changing phase. This helps prevent very small frame-to-frame changes from causing rapid state flipping.

---

# 28. Repetition Counting

The repetition counter uses the state machine.

A simplified valid repetition is:

```text
DOWN
 ↓
UP
 ↓
REP + 1
```

For example:

```text
Frame 1 → UP
Frame 2 → UP
Frame 3 → DOWN
Frame 4 → DOWN
Frame 5 → UP
Frame 6 → UP
```

This is interpreted as one completed repetition instead of counting every frame.

This approach is more reliable than simply doing:

```python
reps += 1
```

whenever a certain angle appears.

---

# 29. Form Score

The score currently represents how many important rule conditions are satisfied.

A simplified example is:

```text
2 conditions

Condition 1 → PASS
Condition 2 → PASS

Score = 100%
```

or:

```text
2 conditions

Condition 1 → PASS
Condition 2 → FAIL

Score = 50%
```

The score should be treated as a feedback indicator, not as a professional biomechanical assessment.

---

# 30. Configuration and Thresholds

Thresholds are stored in:

```text
config/settings.py
```

Examples:

```python
squat_down_knee = 100.0
squat_up_knee = 165.0
squat_back_min = 155.0
```

Push-up thresholds:

```python
pushup_down_elbow = 110.0
pushup_up_elbow = 160.0
pushup_body_min = 165.0
```

Deadlift thresholds:

```python
deadlift_down_knee = 145.0
deadlift_lockout_hip = 165.0
deadlift_back_min = 160.0
```

General settings include:

```python
min_visibility = 0.55
stable_frames = 3
```

These values are deliberately configurable because camera placement, pose visibility and individual movement patterns can affect the observed angles.

---

# 31. Model File

The pose engine expects:

```text
assets/pose_landmarker_lite.task
```

When it is missing, the application attempts to download the model automatically.

After a successful download, the folder should look like:

```text
assets/
└── pose_landmarker_lite.task
```

The model is ignored by Git because large binary model files generally should not be committed directly to the repository.

If automatic download fails, obtain the model separately and place it at exactly:

```text
assets/pose_landmarker_lite.task
```

---

# 32. Troubleshooting

## Python is missing

Run:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

## Virtual environment is not active

Run:

```bash
cd ~/posture-tracker
source .venv/bin/activate
```

## Dependencies are missing

Run:

```bash
pip install -r requirements.txt
```

## Streamlit does not start

Try:

```bash
python -m streamlit run app.py
```

## Camera does not work

Check:

1. Browser camera permission.
2. Another application is not already using the camera.
3. The browser has permission to access the camera.
4. Linux detects the camera.

You can check video devices with:

```bash
ls /dev/video*
```

A device such as:

```text
/dev/video0
```

usually means Linux has detected a camera device.

## No person is detected

Try:

- Moving farther from the camera.
- Keeping the complete body in frame.
- Improving lighting.
- Reducing occlusion.
- Using a side view.

## Repetitions are inaccurate

This may happen because of:

- Camera angle
- Landmark visibility
- Body occlusion
- Fast motion
- Individual body proportions
- Exercise technique
- Current heuristic thresholds

The thresholds can be adjusted in:

```text
config/settings.py
```

## MediaPipe model download fails

Download/place the pose model manually at:

```text
assets/pose_landmarker_lite.task
```

Then restart the application.

---

# 33. Git and GitHub Workflow

The project repository is:

```text
https://github.com/rohatash-sharma/posture-tracker
```

## Check changes

```bash
git status
```

## Add changes

```bash
git add .
```

## Commit

```bash
git commit -m "Describe your change"
```

## Push

```bash
git push
```

Example:

```bash
git add .
git commit -m "Improve squat detection"
git push
```

## Pull latest changes

```bash
git pull
```

---

# 34. Presentation Explanation

This section is specifically included so the README can also help explain the project during a college/SIH presentation.

## 34.1 One-line project explanation

> **AI Exercise Posture Analyzer is a computer-vision system that uses pose landmarks and geometric rules to analyze exercise form and count repetitions from normal video.**

## 34.2 Problem

> Improper exercise posture can reduce workout effectiveness and may increase injury risk, while continuous professional supervision is not always available.

## 34.3 Solution

> We use a camera to detect body landmarks, calculate joint angles, evaluate exercise-specific posture rules, identify movement phases, and count valid repetitions.

## 34.4 How to explain the pipeline

Say:

```text
First, the camera gives us video frames.

Then MediaPipe detects the human body landmarks.

We use those landmarks to calculate important joint angles.

Those angles are passed to the exercise-specific rule engine.

The state machine identifies whether the person is up, down,
or in transition.

The repetition counter checks whether the movement completed a
valid cycle.

Finally, the dashboard shows the repetition count, form score,
angles and feedback.
```

## 34.5 Why not just count frames?

A frame is not a repetition.

We need temporal information.

Therefore:

```text
Frames → Movement phase → Completed movement → Repetition
```

## 34.6 Why use angles?

Pixel positions alone change when the person moves around the camera frame.

Angles describe relationships between body segments and are therefore useful for rule-based movement analysis.

## 34.7 What is the role of AI?

In the current implementation, the main AI/computer-vision component is pose estimation.

The exercise decision layer is deterministic and rule-based.

This distinction is important during a presentation.

Do **not** claim that the current version contains a custom trained exercise-classification model unless one is actually added later.

---

# 35. Demo Checklist

Use this before presenting the project.

## Before the demo

```bash
cd ~/posture-tracker
source .venv/bin/activate
pytest -q
streamlit run app.py
```

## During the demo

### Demo 1 — Application

Show the home/dashboard interface.

### Demo 2 — Squat

Select:

```text
Live Analyzer → Squat
```

Perform a few repetitions.

Show:

- Skeleton
- Knee angle
- Back angle
- Phase
- Repetitions
- Form score

### Demo 3 — Push-Up

Select:

```text
Push-Up
```

Demonstrate the elbow/body alignment logic.

### Demo 4 — Deadlift

Select:

```text
Deadlift
```

Demonstrate the back and lockout analysis.

### Demo 5 — Recorded video

Upload a prepared video and show the annotated result.

---

# 36. Advantages

## No wearable sensors

The project uses a camera instead of attaching sensors to the body.

## Low-cost input

A standard webcam or smartphone/computer camera can be used as the input source.

## Real-time feedback

The live analyzer can provide feedback while the movement is happening.

## Modular architecture

Pose estimation, geometry, exercise logic, state tracking and UI are separated.

## Easy to extend

Additional exercises can be added as new analyzers.

## Configurable rules

Important thresholds can be changed without rewriting the entire application.

---

# 37. Limitations

The current implementation has important limitations.

## Heuristic exercise rules

Exercise analysis uses deterministic thresholds rather than a custom trained model.

## Camera dependence

Results can vary depending on viewpoint, lighting, distance and occlusion.

## One-person focus

The current architecture is intended for one primary person in the frame.

## No medical validation

The system has not been presented as a medical diagnostic or rehabilitation tool.

## Threshold sensitivity

Different users and different camera setups may require different thresholds.

## Not a professional coach

The displayed score should not be interpreted as a complete biomechanical or medical evaluation.

---

# 38. Future Improvements

These are logical engineering improvements to the current implementation.

## 1. Better temporal smoothing

Improve landmark/angle stability using stronger temporal filtering.

Goal:

```text
Noisy angles
    ↓
Smoothing
    ↓
More stable movement states
```

## 2. Better repetition counting

Add:

- Hysteresis
- Minimum repetition duration
- Maximum repetition duration
- Velocity checks
- Better transition handling

## 3. Better camera/view validation

Automatically determine whether the camera view is suitable for the selected exercise.

## 4. Exercise-specific calibration

Allow users to calibrate a neutral standing or starting position before beginning a set.

## 5. More exercises

Possible additions:

- Lunges
- Bicep curls
- Shoulder press
- Bench press
- Calf raises
- Planks
- Jumping jacks

## 6. Better feedback

Instead of only showing text, provide more detailed guidance such as:

```text
Lower your hips further.
Keep your knees aligned.
Maintain a neutral spine.
Control the descent.
```

## 7. Session history

Store workout sessions with:

```text
Date
Exercise
Repetitions
Average form score
Duration
```

## 8. Performance graphs

Show changes over time:

```text
Form score
Repetition count
Exercise duration
```

---

# 39. Future Scope

The following ideas move the project beyond the current rule-based prototype.

## Automatic exercise recognition

Instead of manually selecting the exercise:

```text
Camera
  ↓
Pose sequence
  ↓
Exercise classifier
  ↓
Squat / Push-Up / Deadlift / ...
```

## Custom machine-learning model

A future system could train a model using labeled exercise sequences to classify:

- Exercise type
- Movement phase
- Form quality
- Repetition boundaries

## Multiple pose backends

The architecture can eventually support more than one pose estimation backend.

For example:

```text
              Pose Interface
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      MediaPipe              YOLO
          │                   │
          └─────────┬─────────┘
                    ▼
             Exercise Engine
```

This keeps the exercise logic independent of the specific pose model.

## Personalized models

A future version could learn a user's normal movement range and adapt thresholds based on individual biomechanics.

## Edge/mobile deployment

A future implementation could move the inference pipeline to Android or another edge device for local processing.

## More advanced biomechanics

Future work could include additional measurements such as:

- Segment orientation
- Movement velocity
- Acceleration
- Range of motion
- Tempo
- Symmetry

---

# 40. Privacy Considerations

When the application is run locally, processing can take place on the user's computer.

For a public or production deployment, video handling must be reviewed carefully.

A production system should explicitly consider:

- Whether video is stored.
- How long video is retained.
- Who can access uploaded videos.
- Whether processing happens locally or remotely.
- Encryption and transport security.
- User consent and privacy policy.

The current prototype should not be treated as a complete production privacy/security solution.

---

# 41. Disclaimer

This project is an experimental computer-vision fitness application.

It is **not a medical device**, does not diagnose injuries or medical conditions, and should not replace professional medical or exercise advice.

A high form score does not guarantee that an exercise is safe or biomechanically optimal.

---

# 42. License

This project is released under the MIT License.

See [`LICENSE`](LICENSE) for the full license text.

---

# 43. Author

**Rohatash Sharma**

GitHub:

https://github.com/rohatash-sharma

Repository:

https://github.com/rohatash-sharma/posture-tracker

---

# 🚀 Quick Start

For a fresh Ubuntu/Linux machine:

```bash
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv

cd ~
git clone https://github.com/rohatash-sharma/posture-tracker.git
cd posture-tracker

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

pytest -q

streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

---

# 🎤 30-Second Presentation Version

> **Our project is an AI-based exercise posture analyzer. The user provides a webcam stream or recorded video. MediaPipe detects 33 body landmarks, and we calculate important joint angles such as knee, elbow, hip and body-alignment angles. These measurements are passed into exercise-specific rules for squats, push-ups and deadlifts. A state machine tracks the movement phase, and the repetition counter counts only completed movement cycles. The system then displays the form score, repetition count, joint measurements and feedback in real time. Our current version is a rule-based computer-vision prototype, while future work includes learned exercise recognition, more exercises, personalization and more advanced biomechanical analysis.**

---

## ⭐ Project Flow in One Diagram

```text
             ┌──────────────────┐
             │     USER         │
             │  Webcam / Video  │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │ MediaPipe Pose   │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │ 33 Landmarks     │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │ Joint Angles     │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │ Form Validation  │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │ State Machine    │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │ Rep Counter      │
             └────────┬─────────┘
                      │
              ┌───────┴────────┐
              ▼                ▼
       ┌──────────────┐  ┌─────────────┐
       │ Dashboard    │  │ Audio Cue   │
       └──────────────┘  └─────────────┘
```

**AI Exercise Posture Analyzer — computer vision for exercise form analysis.**
