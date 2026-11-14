import subprocess
import sys
from pathlib import Path


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(project_root / "app.py"),
    ]

    raise SystemExit(
        subprocess.call(
            command,
            cwd=project_root,
        )
    )