from __future__ import annotations

import json

import streamlit.components.v1 as components

from backend.config.settings import THRESHOLDS


def render_personal_learning(
    exercise: str,
    enabled: bool,
    event_id: str,
    rep_metrics: dict[str, tuple[float, float]],
    current_metrics: dict[str, float],
    hold_seconds: float,
) -> None:
    movement_cues = {
        "Squat": (
            "knee_angle",
            THRESHOLDS.squat_down_knee,
            "bottom knee angle",
        ),
        "Push-Up": (
            "elbow_angle",
            THRESHOLDS.pushup_down_elbow,
            "bottom elbow angle",
        ),
        "Deadlift": (
            "hip_angle",
            THRESHOLDS.deadlift_down_hip,
            "hinge hip angle",
        ),
        "Lunge": (
            "knee_angle",
            THRESHOLDS.lunge_down_knee,
            "front knee angle",
        ),
        "Bicep Curl": (
            "elbow_angle",
            THRESHOLDS.curl_down_elbow,
            "curl elbow angle",
        ),
        "Plank": ("body_angle", None, "body-line angle"),
    }
    metric, target, label = movement_cues[exercise]
    metrics_json = json.dumps(
        {
            "exercise": exercise,
            "enabled": enabled,
            "eventId": event_id,
            "repMetrics": rep_metrics,
            "currentMetrics": current_metrics,
            "holdSeconds": hold_seconds,
            "metric": metric,
            "target": target,
            "label": label,
        }
    )
    components.html(
        f"""
        <div id="personal-learning" role="status" aria-live="polite"></div>
        <script>
        const app = window.parent;
        const input = {metrics_json};
        const output = document.getElementById("personal-learning");
        const profileKey =
            "posture.learning.v1." + input.exercise.toLowerCase().replaceAll(" ", "-");
        const eventKey = "posture.learning.last." + input.exercise;
        const sampleId = input.exercise === "Plank"
            ? input.eventId + ":" + Math.floor(input.holdSeconds / 5)
            : input.eventId;
        const metricValue = input.exercise === "Plank"
            ? input.currentMetrics[input.metric]
            : input.repMetrics[input.metric]?.[0];
        const medianOf = (items) => {{
            const ordered = [...items].sort((a, b) => a - b);
            const middle = Math.floor(ordered.length / 2);
            return ordered.length % 2
                ? ordered[middle]
                : (ordered[middle - 1] + ordered[middle]) / 2;
        }};

        try {{
            const stored = JSON.parse(app.localStorage.getItem(profileKey) || "[]");
            if (!Array.isArray(stored)) {{
                throw new Error("Saved learning data is not a list.");
            }}
            const history = stored.filter(
                sample => sample && Number.isFinite(sample.value)
            );
            if (
                input.enabled
                && Number.isFinite(metricValue)
                && (input.exercise !== "Plank" || input.holdSeconds >= 5)
                && app.localStorage.getItem(eventKey) !== sampleId
            ) {{
                history.push({{ id: sampleId, value: metricValue }});
                history.splice(0, Math.max(0, history.length - 50));
                app.localStorage.setItem(profileKey, JSON.stringify(history));
                app.localStorage.setItem(eventKey, sampleId);
            }}

            if (!history.length) {{
                output.textContent = input.enabled
                    ? "Complete a counted rep to start a private, browser-only baseline."
                    : "Personal learning is off. Turn it on in the sidebar to save measurements in this browser.";
            }} else {{
                const chronologicalValues = history.map(sample => sample.value);
                const values = [...chronologicalValues].sort((a, b) => a - b);
                const median = medianOf(values);
                const low = values[Math.floor((values.length - 1) * 0.1)];
                const high = values[Math.ceil((values.length - 1) * 0.9)];
                const latest = chronologicalValues[chronologicalValues.length - 1];
                const usualRange =
                    `Your recent ${{input.label}} range is ${{low.toFixed(0)}}°–${{high.toFixed(0)}}° (median ${{median.toFixed(0)}}°).`;

                let learnedRangeText =
                    " Collect more measurements to establish your personal range.";
                if (chronologicalValues.length >= 6) {{
                    const priorValues = chronologicalValues.slice(-21, -1);
                    const personalMedian = medianOf(priorValues);
                    const deviations = priorValues.map(
                        value => Math.abs(value - personalMedian)
                    );
                    const radius = Math.max(3, 3 * 1.4826 * medianOf(deviations));
                    const lower = personalMedian - radius;
                    const upper = personalMedian + radius;
                    const status = latest < lower || latest > upper
                        ? "outside"
                        : "within";
                    learnedRangeText =
                        ` Latest reading is ${{status}} your recent personal range (${{lower.toFixed(0)}}°–${{upper.toFixed(0)}}°); review it in context, not as a form judgment.`;
                }}

                if (input.target === null) {{
                    output.textContent =
                        `${{usualRange}}${{learnedRangeText}} Your history is a reference, not a pass/fail rule.`;
                }} else {{
                    const distance = Math.abs(latest - input.target);
                    const relation = latest > input.target
                        ? "above"
                        : "below";
                    const targetText =
                        `Latest counted rep: ${{distance.toFixed(0)}}° ${{relation}} the app's ${{input.target}}° phase cue.`;
                    let trendText = "";
                    if (chronologicalValues.length >= 10) {{
                        const early = medianOf(chronologicalValues.slice(0, 5));
                        const recent = medianOf(chronologicalValues.slice(-5));
                        const progress =
                            Math.abs(early - input.target)
                            - Math.abs(recent - input.target);
                        if (progress >= 2) {{
                            trendText =
                                ` Your recent reps moved ${{progress.toFixed(0)}}° closer to that cue than your first five.`;
                        }} else if (progress <= -2) {{
                            trendText =
                                ` Your recent reps moved ${{Math.abs(progress).toFixed(0)}}° farther from that cue than your first five.`;
                        }} else {{
                            trendText =
                                " Your recent reps are at a similar distance from that cue as your first five.";
                        }}
                    }}
                    output.textContent =
                        `${{usualRange}} ${{targetText}}${{trendText}}${{learnedRangeText}} The app's scoring and coaching are unchanged.`;
                }}
            }}
        }} catch (error) {{
            output.textContent =
                "Could not access this browser's saved learning data.";
        }}
        </script>
        """,
        height=92,
    )
