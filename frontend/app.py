from __future__ import annotations

import streamlit as st

from .pages.about import render_about
from .pages.live_analyzer import render_live_analyzer
from .pages.video_analysis import render_video_analysis


def run_app() -> None:
    st.set_page_config(
        page_title="AI Exercise Posture Analyzer",
        page_icon="🏋️",
        layout="wide",
    )

    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("🏋️ AI Exercise Posture Analyzer")
    st.caption(
        "Real-time exercise form analysis "
        "using MediaPipe Pose."
    )

    page = st.sidebar.radio(
        "Mode",
        [
            "Live Analyzer",
            "Video Analysis",
            "About",
        ],
    )
    exercise = st.sidebar.selectbox(
        "Exercise",
        [
            "Squat",
            "Push-Up",
            "Deadlift",
            "Lunge",
            "Bicep Curl",
            "Plank",
        ],
    )
    audio_enabled = st.sidebar.checkbox(
        "Enable voice feedback",
        value=True,
    )
    learning_enabled = st.sidebar.checkbox(
        "Learn my range on this browser",
        value=False,
        help=(
            "Opt in to save movement measurements from counted live "
            "repetitions in this browser only. You can clear them anytime."
        ),
    )

    if page == "Live Analyzer":
        render_live_analyzer(
            exercise,
            audio_enabled,
            learning_enabled,
        )
    elif page == "Video Analysis":
        render_video_analysis(exercise, audio_enabled)
    else:
        render_about()
