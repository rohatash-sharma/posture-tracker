from __future__ import annotations

import streamlit as st


def render_about() -> None:
    st.subheader("About the project")
    st.markdown(
        """
        ## Pipeline

        Camera / Video

        ↓

        MediaPipe Pose Landmarker

        ↓

        33 Body Landmarks

        ↓

        Geometric Angle Calculation

        ↓

        Exercise Form Validation

        ↓

        State Machine

        ↓

        Repetition Counter

        ↓

        Feedback + Dashboard

        ## Supported Exercises

        - **Squat:** knee bend and estimated torso tilt.
        - **Push-Up:** elbow bend and shoulder/hip/ankle alignment.
        - **Deadlift:** hip hinge and standing lockout.
        - **Lunge:** knee bend and estimated torso tilt.
        - **Bicep Curl:** elbow bend and upper-arm movement.
        - **Plank:** shoulder/hip/ankle alignment and hold time.

        ## Important

        This is a fitness-analysis prototype.
        Pose landmarks and movement-phase angle cues are estimates, not
        universal form limits or a professional biomechanical assessment.
        Optional personal trends are stored in this browser only and do not
        verify that a rep is safe or correct. In particular, this application
        cannot determine spinal curvature during a deadlift.
        Stop if you feel pain; this is not a medical device and should not
        replace professional coaching or medical advice.
        """
    )
