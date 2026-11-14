from __future__ import annotations

import json

import streamlit as st
import streamlit.components.v1 as components
from streamlit_webrtc import (
    RTCConfiguration,
    WebRtcMode,
    webrtc_streamer,
)

from backend.live_processor import (
    ExerciseVideoProcessor,
    LiveState,
)
from .personal_learning import render_personal_learning


def render_live_analyzer(
    exercise: str,
    audio_enabled: bool,
    learning_enabled: bool,
) -> None:
    st.subheader(f"Live {exercise} Analyzer")
    st.info(
        "For best results, use a side view, "
        "keep your entire body visible and "
        "use good lighting. If your camera is unavailable, "
        "choose Video Analysis in the sidebar to upload a saved clip."
    )

    state_key = f"live_state_{exercise}"
    if state_key not in st.session_state:
        st.session_state[state_key] = LiveState()
    state = st.session_state[state_key]

    rtc_configuration = RTCConfiguration(
        {
            "iceServers": [
                {
                    "urls": [
                        "stun:stun.l.google.com:19302"
                    ]
                }
            ]
        }
    )

    webrtc_streamer(
        key=f"posture-{exercise.lower()}",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=rtc_configuration,
        video_processor_factory=lambda: ExerciseVideoProcessor(
            exercise,
            state,
        ),
        media_stream_constraints={
            "video": {
                "width": {"ideal": 960},
                "height": {"ideal": 540},
                "frameRate": {"ideal": 30},
            },
            "audio": False,
        },
        async_processing=True,
    )

    _render_live_controls(audio_enabled)

    @st.fragment(run_every="0.5s")
    def render_metrics() -> None:
        with state.lock:
            reps = state.reps
            score = state.score
            phase = state.phase
            feedback = state.feedback
            current_metrics = dict(state.metrics)
            voice_event_id = state.voice_event_id
            voice_session_id = state.voice_session_id
            voice_text = state.voice_text
            rep_metrics = dict(state.rep_metrics)

        col1, col2, col3, col4 = st.columns(4)
        if exercise == "Plank":
            hold_seconds = current_metrics.get("hold_seconds", 0.0)
            col1.metric("Hold Time", f"{hold_seconds:.1f}s")
        else:
            col1.metric("Repetitions", reps)
        col2.metric("Form Score", f"{score:.0f}%")
        col3.metric("Phase", phase.upper())

        if score >= 80:
            status = "GOOD"
        elif score >= 50:
            status = "ADJUST"
        else:
            status = "CHECK FORM"
        col4.metric("Status", status)

        st.markdown(f"### Feedback\n**{feedback}**")
        if current_metrics:
            st.write(
                {
                    key.replace("_", " ").title(): round(value, 1)
                    for key, value in current_metrics.items()
                }
            )

        _render_voice_feedback(
            audio_enabled,
            f"{voice_session_id}:{voice_event_id}",
            voice_text,
        )
        render_personal_learning(
            exercise=exercise,
            enabled=learning_enabled,
            event_id=f"{voice_session_id}:{reps}",
            rep_metrics=rep_metrics,
            current_metrics=current_metrics,
            hold_seconds=current_metrics.get("hold_seconds", 0.0),
        )

    render_metrics()


def _render_voice_feedback(
    enabled: bool,
    event_id: str,
    message: str,
) -> None:
    components.html(
        f"""
        <script>
        const app = window.parent;
        const audioEnabled = {json.dumps(enabled)};
        const eventId = {json.dumps(event_id)};
        const message = {json.dumps(message)};
        const eventKey = "postureLastVoiceEvent";

        function speak(text) {{
            if (!app.speechSynthesis || !window.SpeechSynthesisUtterance) {{
                return;
            }}
            app.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1;
            app.speechSynthesis.speak(utterance);
        }}

        if (
            audioEnabled
            && app.localStorage.getItem("postureVoiceEnabled") === "true"
            && eventId.endsWith(":0") === false
            && app.localStorage.getItem(eventKey) !== String(eventId)
        ) {{
            app.localStorage.setItem(eventKey, String(eventId));
            speak(message);
        }}
        </script>
        """,
        height=0,
    )


def _render_live_controls(enabled: bool) -> None:
    voice_control = (
        '<button id="enable-voice" type="button">'
        "Enable voice feedback"
        "</button>"
        if enabled
        else "<span>Voice feedback is off in the sidebar.</span>"
    )
    html = """
        __VOICE_CONTROL__
        <button id="clear-learning" type="button">
            Clear saved learning data
        </button>
        <span id="voice-status" role="status" aria-live="polite"></span>
        <script>
        const app = window.parent;
        const button = document.getElementById("enable-voice");
        const clearButton = document.getElementById("clear-learning");
        const status = document.getElementById("voice-status");
        const preferenceKey = "postureVoiceEnabled";
        const profilePrefix = "posture.learning.v1.";
        const lastSamplePrefix = "posture.learning.last.";

        function speak(text) {
            if (!app.speechSynthesis || !window.SpeechSynthesisUtterance) {
                status.textContent =
                    "Speech is not supported by this browser.";
                return;
            }
            app.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.onerror = () => {
                status.textContent =
                    "Voice could not play. Check browser audio permissions.";
            };
            app.speechSynthesis.speak(utterance);
        }

        clearButton.addEventListener("click", () => {
            for (const key of Object.keys(app.localStorage)) {
                if (
                    key.startsWith(profilePrefix)
                    || key.startsWith(lastSamplePrefix)
                    || key === "postureLastVoiceEvent"
                ) {
                    app.localStorage.removeItem(key);
                }
            }
            status.textContent = "Saved learning data cleared from this browser.";
        });

        if (button && app.localStorage.getItem(preferenceKey) === "true") {
            button.textContent = "Voice feedback enabled";
        }
        button?.addEventListener("click", () => {
            app.localStorage.setItem(preferenceKey, "true");
            button.textContent = "Voice feedback enabled";
            status.textContent = "Voice feedback is on.";
            speak("Voice feedback is on.");
        });
        </script>
        """
    components.html(
        html.replace("__VOICE_CONTROL__", voice_control),
        height=58,
    )
