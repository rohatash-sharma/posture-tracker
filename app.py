from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from streamlit_webrtc import (
    RTCConfiguration,
    WebRtcMode,
    webrtc_streamer,
)

from core.audio import make_beep_wav
from core.live_processor import (
    ExerciseVideoProcessor,
    LiveState,
)

from core.video_analyzer import (
    analyze_video,
)


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


@st.cache_data
def get_beep() -> bytes:

    return make_beep_wav()


st.title(
    "🏋️ AI Exercise Posture Analyzer"
)

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
    ],
)


audio_enabled = st.sidebar.checkbox(
    "Enable repetition beep",
    value=True,
)


if page == "Live Analyzer":

    st.subheader(
        f"Live {exercise} Analyzer"
    )

    st.info(
        "For best results, use a side view, "
        "keep your entire body visible and "
        "use good lighting."
    )

    state_key = (
        f"live_state_{exercise}"
    )

    if state_key not in st.session_state:

        st.session_state[state_key] = (
            LiveState()
        )

    state = st.session_state[
        state_key
    ]

    rtc_configuration = (
        RTCConfiguration(
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
    )

    context = webrtc_streamer(
        key=(
            f"posture-{exercise.lower()}"
        ),
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=rtc_configuration,
        video_processor_factory=(
            lambda: ExerciseVideoProcessor(
                exercise,
                state,
            )
        ),
        media_stream_constraints={
            "video": {
                "width": {
                    "ideal": 960
                },
                "height": {
                    "ideal": 540
                },
                "frameRate": {
                    "ideal": 30
                },
            },
            "audio": False,
        },
        async_processing=True,
    )

    @st.fragment(run_every="0.5s")
    def metrics():

        with state.lock:

            reps = state.reps
            score = state.score
            phase = state.phase
            feedback = state.feedback

            current_metrics = dict(
                state.metrics
            )

            rep_event = (
                state.last_rep_event
            )

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        col1.metric(
            "Repetitions",
            reps,
        )

        col2.metric(
            "Form Score",
            f"{score:.0f}%",
        )

        col3.metric(
            "Phase",
            phase.upper(),
        )

        if score >= 80:

            status = "GOOD"

        elif score >= 50:

            status = "ADJUST"

        else:

            status = "CHECK FORM"

        col4.metric(
            "Status",
            status,
        )

        st.markdown(
            f"### Feedback\n**{feedback}**"
        )

        if current_metrics:

            st.write(
                {
                    key.replace(
                        "_",
                        " "
                    ).title(): round(
                        value,
                        1,
                    )
                    for key, value
                    in current_metrics.items()
                }
            )

        if (
            audio_enabled
            and rep_event > 0
        ):

            beep_hex = (
                get_beep().hex()
            )

            components.html(
                f"""
                <script>

                const eventId =
                    "posture-rep-{rep_event}";

                if (
                    window.parent
                        .__postureLastRep
                    !== eventId
                ) {{

                    window.parent
                        .__postureLastRep
                        = eventId;

                    const hex =
                        "{beep_hex}";

                    const bytes =
                        new Uint8Array(
                            hex.match(
                                /.{{1,2}}/g
                            ).map(
                                h =>
                                    parseInt(
                                        h,
                                        16
                                    )
                            )
                        );

                    const blob =
                        new Blob(
                            [bytes],
                            {
                                type: "audio/wav"
                            }
                        );

                    const audio =
                        new Audio(
                            URL.createObjectURL(
                                blob
                            )
                        );

                    audio.volume = 0.5;

                    audio.play()
                        .catch(
                            () => {{}}
                        );
                }}

                </script>
                """,
                height=0,
            )

    metrics()


elif page == "Video Analysis":

    st.subheader(
        "Recorded Video Analysis"
    )

    uploaded = st.file_uploader(
        "Upload exercise video",
        type=[
            "mp4",
            "mov",
            "avi",
            "mkv",
        ],
    )

    if uploaded is not None:

        st.video(
            uploaded
        )

        if st.button(
            "Analyze Video",
            type="primary",
        ):

            suffix = (
                Path(
                    uploaded.name
                ).suffix
                or ".mp4"
            )

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
            ) as source:

                source.write(
                    uploaded.getvalue()
                )

                input_path = (
                    source.name
                )

            output = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4",
            )

            output.close()

            try:

                with st.spinner(
                    "Analyzing video..."
                ):

                    summary = analyze_video(
                        input_path,
                        output.name,
                        exercise,
                    )

                st.success(
                    "Analysis complete."
                )

                col1, col2, col3, col4 = (
                    st.columns(4)
                )

                col1.metric(
                    "Repetitions",
                    summary.reps,
                )

                col2.metric(
                    "Average Form",
                    f"{summary.average_score:.0f}%",
                )

                col3.metric(
                    "Duration",
                    f"{summary.duration_seconds:.1f}s",
                )

                col4.metric(
                    "Valid Frames",
                    summary.valid_frames,
                )

                with open(
                    output.name,
                    "rb",
                ) as video_file:

                    st.download_button(
                        "Download Annotated Video",
                        video_file,
                        file_name=(
                            f"{exercise.lower()}"
                            "_analysis.mp4"
                        ),
                        mime="video/mp4",
                    )

            except Exception as exc:

                st.error(
                    f"Analysis failed: {exc}"
                )


else:

    st.subheader(
        "About the project"
    )

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

        **Squat**

        Knee angle, squat depth and back alignment.

        **Push-Up**

        Elbow angle and shoulder/hip/ankle body alignment.

        **Deadlift**

        Knee extension, hip lockout and back posture.

        ## Important

        This is a fitness-analysis prototype.
        It is not a medical device and should not
        replace professional medical or coaching advice.
        """
    )