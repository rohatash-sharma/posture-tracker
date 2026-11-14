from __future__ import annotations

import io
import math
import wave

import numpy as np


def make_beep_wav(
    frequency: int = 880,
    duration: float = 0.18,
    sample_rate: int = 44100,
) -> bytes:

    time = np.linspace(
        0,
        duration,
        int(
            sample_rate
            * duration
        ),
        endpoint=False,
    )

    samples = (
        0.20
        * np.sin(
            2
            * math.pi
            * frequency
            * time
        )
        * 32767
    ).astype(np.int16)

    buffer = io.BytesIO()

    with wave.open(
        buffer,
        "wb",
    ) as wav:

        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(
            sample_rate
        )

        wav.writeframes(
            samples.tobytes()
        )

    return buffer.getvalue()