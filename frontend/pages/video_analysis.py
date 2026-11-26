from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path
from uuid import uuid4

import streamlit as st
import streamlit.components.v1 as components

from backend.config.settings import SESSIONS_DIR
from backend.video_analyzer import VideoSummary, analyze_video


def render_video_analysis(
    exercise: str,
    audio_enabled: bool,
) -> None:
    st.subheader("Recorded Video Analysis")
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    _remove_expired_results()

    uploaded = st.file_uploader(
        "Upload exercise video",
        type=["mp4", "mov", "avi", "mkv"],
    )

    if uploaded is None:
        _render_saved_result(audio_enabled)
        return

    suffix = Path(uploaded.name).suffix or ".mp4"
    uploaded_bytes = uploaded.getvalue()
    st.video(
        data=uploaded_bytes,
        format=(
            f"video/{suffix.lstrip('.').lower()}"
            if suffix.lower() != ".mov"
            else "video/quicktime"
        ),
    )

    if not st.button("Analyze Video", type="primary"):
        _render_saved_result(audio_enabled)
        return

    session_id = st.session_state.setdefault(
        "video_analysis_session_id",
        uuid4().hex,
    )
    output_path = SESSIONS_DIR / (
        f"analysis-{session_id}-{uuid4().hex}.mp4"
    )
    progress_bar = st.progress(
        0.0,
        text="Starting video analysis...",
    )
    progress_text = st.empty()

    def report_progress(current: int, total: int) -> None:
        if total > 0:
            progress_bar.progress(
                min(current / total, 1.0),
                text=f"Analyzing frame {current:,} of {total:,}...",
            )
        else:
            progress_text.caption(f"Analyzed {current:,} frames...")

    try:
        with tempfile.TemporaryDirectory(
            prefix="posture-tracker-",
        ) as temporary_directory:
            input_path = Path(temporary_directory) / f"input{suffix}"
            input_path.write_bytes(uploaded_bytes)

            with st.spinner("Analyzing video..."):
                summary = analyze_video(
                    input_path,
                    output_path,
                    exercise,
                    progress_callback=report_progress,
                )

        previous_result = st.session_state.get(
            "video_analysis_result"
        )
        st.session_state["video_analysis_result"] = (
            exercise,
            summary,
            str(output_path),
        )
        if previous_result is not None:
            previous_path = Path(previous_result[2])
            if previous_path != output_path:
                previous_path.unlink(missing_ok=True)
    except Exception as exc:
        output_path.unlink(missing_ok=True)
        st.error(f"Analysis failed: {exc}")
        _render_saved_result(audio_enabled)
        return

    progress_bar.progress(1.0, text="Analysis complete.")
    progress_text.empty()
    _render_saved_result(audio_enabled)


def _render_saved_result(audio_enabled: bool) -> None:
    result = st.session_state.get("video_analysis_result")
    if result is None:
        return

    result_exercise, summary, output_name = result
    output_path = Path(output_name)
    if not output_path.is_file():
        st.session_state.pop("video_analysis_result", None)
        return

    st.success(f"{result_exercise} analysis complete.")
    col1, col2, col3, col4 = st.columns(4)
    if result_exercise == "Plank":
        col1.metric("Hold Time", f"{summary.hold_seconds:.1f}s")
    else:
        col1.metric("Repetitions", summary.reps)
    col2.metric("Average Form", f"{summary.average_score:.0f}%")
    col3.metric("Duration", f"{summary.duration_seconds:.1f}s")
    col4.metric("Valid Frames", summary.valid_frames)
    _render_video_voice(result_exercise, summary, audio_enabled)

    angle_ranges = {
        name.replace("_", " ").title(): (
            f"{minimum:.1f}°–{maximum:.1f}°"
        )
        for name, (minimum, maximum)
        in summary.metric_ranges.items()
        if name.endswith("_angle")
    }
    if angle_ranges:
        st.caption("Observed joint-angle ranges")
        st.write(angle_ranges)

    slug = result_exercise.lower().replace(" ", "_")
    st.subheader("Corrections Throughout the Video")
    if summary.correction_timeline:
        report_text = _format_correction_report(
            result_exercise,
            summary,
        )
        st.text_area(
            "Text response",
            value=report_text,
            height=220,
            disabled=True,
        )
        st.download_button(
            "Download Corrections Text",
            report_text,
            file_name=f"{slug}_corrections.txt",
            mime="text/plain",
        )
    else:
        st.info("No correction cues were detected in the processed frames.")

    with output_path.open("rb") as video_file:
        st.download_button(
            "Download Annotated Video",
            video_file,
            file_name=f"{slug}_analysis.mp4",
            mime="video/mp4",
            on_click="ignore",
        )


def _format_correction_report(
    exercise: str,
    summary: VideoSummary,
) -> str:
    lines = [
        f"{exercise} Offline Analysis Report",
        f"Duration: {summary.duration_seconds:.1f} seconds",
        f"Average form score: {summary.average_score:.0f}%",
    ]
    if exercise == "Plank":
        lines.append(f"Hold time: {summary.hold_seconds:.1f} seconds")
    else:
        lines.append(f"Repetitions: {summary.reps}")
    lines.append("\nCorrections throughout the video:")

    for correction in summary.correction_timeline:
        minutes, seconds = divmod(
            float(correction["time_seconds"]),
            60,
        )
        timestamp = f"{int(minutes):02d}:{seconds:05.2f}"
        level = str(correction["level"]).upper()
        lines.append(
            f"- [{timestamp}] {level}: {correction['message']} "
            f"(frame {correction['frame']}, score {float(correction['score']):.0f}%)"
        )

    return "\n".join(lines)


def _render_video_voice(
    exercise: str,
    summary: VideoSummary,
    enabled: bool,
) -> None:
    if not enabled:
        st.caption("Enable voice feedback in the sidebar to hear these results.")
        return

    activity = (
        f"hold time {summary.hold_seconds:.1f} seconds"
        if exercise == "Plank"
        else f"{summary.reps} repetitions"
    )
    correction_count = len(summary.correction_timeline)
    spoken_summary = (
        f"{exercise} analysis complete. {activity}. "
        f"Average form score {summary.average_score:.0f} percent. "
        f"Duration {summary.duration_seconds:.1f} seconds. "
        f"{correction_count} correction cues were recorded throughout the video."
    )
    components.html(
        f"""
        <button id="speak-results" type="button">Read results aloud</button>
        <span id="speech-status" role="status" aria-live="polite"></span>
        <script>
        const app = window.parent;
        const message = {json.dumps(spoken_summary)};
        const button = document.getElementById("speak-results");
        const status = document.getElementById("speech-status");
        button.addEventListener("click", () => {{
            if (!app.speechSynthesis || !window.SpeechSynthesisUtterance) {{
                status.textContent =
                    "Speech is not supported by this browser.";
                return;
            }}
            app.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(message);
            utterance.onerror = () => {{
                status.textContent =
                    "Voice could not play. Check browser audio permissions.";
            }};
            app.speechSynthesis.speak(utterance);
        }});
        </script>
        """,
        height=42,
    )


def _remove_expired_results() -> None:
    expiration_seconds = 24 * 60 * 60
    now = time.time()
    for path in SESSIONS_DIR.glob("analysis-*.mp4"):
        if now - path.stat().st_mtime > expiration_seconds:
            path.unlink(missing_ok=True)
