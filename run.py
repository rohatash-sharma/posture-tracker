import subprocess
import sys


if __name__ == "__main__":

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py",
    ]

    raise SystemExit(
        subprocess.call(command)
    )